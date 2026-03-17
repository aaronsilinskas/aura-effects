from effects.effect import Effect, EffectState, EffectStep, EffectTimer
from effects.shape import Shape


# ---------------------------------------------------------------------------
# Minimal EffectStep helpers
# ---------------------------------------------------------------------------


class _AlwaysAdvance(EffectStep):
    """Step that immediately yields control to the next step every frame."""

    def update(self, state: EffectState, timer: EffectTimer) -> bool:
        return True


class _NeverAdvance(EffectStep):
    """Step that stays active indefinitely."""

    def update(self, state: EffectState, timer: EffectTimer) -> bool:
        return False


class _OffsetPosition(EffectStep):
    """Step that adds a fixed offset to the sampling position."""

    def __init__(self, offset: float):
        self._offset = offset

    def update(self, state: EffectState, timer: EffectTimer) -> bool:
        return True

    def adjust_position(self, state: EffectState, position: float) -> float:
        return position + self._offset


class _MultiplyValue(EffectStep):
    """Step that scales the output value by a fixed factor."""

    def __init__(self, factor: float):
        self._factor = factor

    def update(self, state: EffectState, timer: EffectTimer) -> bool:
        return True

    def adjust_value(self, state: EffectState, position: float, value: float) -> float:
        return value * self._factor


class _RecordActiveStep(EffectStep):
    """Step that records which step index was active when it was updated."""

    def __init__(self, label: str, log: list):
        self._label = label
        self._log = log

    def update(self, state: EffectState, timer: EffectTimer) -> bool:
        self._log.append(self._label)
        return False


# ---------------------------------------------------------------------------
# Effect construction
# ---------------------------------------------------------------------------


def test_add_steps_returns_effect_for_fluent_chaining() -> None:
    effect = Effect("test")

    result = effect.add_steps([_NeverAdvance()])

    assert result is effect


# ---------------------------------------------------------------------------
# Effect.value — sampling guarantees
# ---------------------------------------------------------------------------


def test_effect_with_no_steps_samples_shape_directly() -> None:
    effect = Effect("test", lambda _: 0.75)
    state = EffectState()

    value = effect.value(state, 0.0)

    assert value == 0.75


def test_effect_applies_position_offset_before_sampling_shape() -> None:
    # Shape returns the raw position, so we can verify what position was passed in.
    effect = Effect("test", lambda pos: pos).add_steps([_OffsetPosition(0.25)])
    state = EffectState()
    timer = EffectTimer()
    timer.update(0.016)
    effect.update(state, timer)

    value = effect.value(state, 0.5)

    # Position 0.5 + 0.25 offset = 0.75 wrapped into [0,1], shape returns it directly.
    assert abs(value - 0.75) < 1e-6


def test_effect_applies_value_transforms_in_step_order() -> None:
    # Two multiplier steps: first halves (×0.5), then doubles (×2.0).
    # Net result should be the original shape value (×1.0).
    effect = Effect("test", lambda _: 0.6).add_steps(
        [_MultiplyValue(0.5), _MultiplyValue(2.0)]
    )
    state = EffectState()
    timer = EffectTimer()
    timer.update(0.016)
    effect.update(state, timer)

    value = effect.value(state, 0.0)

    assert abs(value - 0.6) < 1e-6


def test_effect_clamps_output_above_one_when_step_amplifies_value() -> None:
    effect = Effect("test", lambda _: 0.8).add_steps([_MultiplyValue(3.0)])
    state = EffectState()
    timer = EffectTimer()
    timer.update(0.016)
    effect.update(state, timer)

    value = effect.value(state, 0.0)

    assert value == 1.0


def test_effect_clamps_output_below_zero_when_step_inverts_value() -> None:
    effect = Effect("test", lambda _: 0.5).add_steps([_MultiplyValue(-2.0)])
    state = EffectState()
    timer = EffectTimer()
    timer.update(0.016)
    effect.update(state, timer)

    value = effect.value(state, 0.0)

    assert value == 0.0


# ---------------------------------------------------------------------------
# Effect.update — step sequencing guarantees
# ---------------------------------------------------------------------------


def test_effect_advances_to_next_step_when_current_step_completes() -> None:
    log: list = []
    effect = Effect("test").add_steps(
        [
            _AlwaysAdvance(),
            _RecordActiveStep("second", log),
        ]
    )
    state = EffectState()
    timer = EffectTimer()
    timer.update(0.016)

    effect.update(state, timer)

    assert log == ["second"]


def test_effect_stays_on_active_step_across_frames_when_step_holds() -> None:
    log: list = []
    effect = Effect("test").add_steps(
        [
            _RecordActiveStep("first", log),
            _RecordActiveStep("second", log),
        ]
    )
    state = EffectState()
    timer = EffectTimer()
    timer.update(0.016)

    effect.update(state, timer)
    effect.update(state, timer)

    assert log == ["first", "first"]


def test_effect_can_advance_through_multiple_steps_in_one_frame() -> None:
    log: list = []
    effect = Effect("test").add_steps(
        [
            _AlwaysAdvance(),
            _AlwaysAdvance(),
            _RecordActiveStep("third", log),
        ]
    )
    state = EffectState()
    timer = EffectTimer()
    timer.update(0.016)

    effect.update(state, timer)

    assert log == ["third"]


def test_effect_wraps_back_to_first_step_after_last_step_advances() -> None:
    # Seed the state at the last step; after it advances the sequence should
    # wrap and the first step should fire within the same frame.
    log: list = []
    effect = Effect("test").add_steps(
        [
            _RecordActiveStep("first", log),
            _AlwaysAdvance(),
        ]
    )
    state = EffectState()
    state.set_step_index(effect, 1)  # start at last step
    timer = EffectTimer()
    timer.update(0.016)

    effect.update(state, timer)

    assert log == ["first"]


# ---------------------------------------------------------------------------
# EffectState isolation guarantees
# ---------------------------------------------------------------------------


def test_two_states_drive_same_effect_independently() -> None:
    log: list = []

    class _AdvanceOnce(EffectStep):
        """Advances the first time, then records and holds."""

        def update(self, state: EffectState, timer: EffectTimer) -> bool:
            if state.get_step_data(self, bool) is None:
                state.set_step_data(self, True)
                return True
            return False

    advance_step = _AdvanceOnce()
    record_step = _RecordActiveStep("second", log)
    effect = Effect("test").add_steps([advance_step, record_step])

    state_a = EffectState()
    state_b = EffectState()
    timer = EffectTimer()
    timer.update(0.016)

    # Advance state_a past the first step.
    effect.update(state_a, timer)
    # state_b has not been updated — first update should advance it too, independently.
    effect.update(state_b, timer)

    # Both states should have reached the second step: log has two entries.
    assert log == ["second", "second"]
