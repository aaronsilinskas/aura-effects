import pytest

from effects.effect import Effect, EffectState, EffectTimer
from effects.steps.scale import multiplier


def test_multiplier_applies_start_value_at_beginning_of_duration() -> None:
    # Timer at progress 0.0 → multiplier should equal start (0.25).
    effect = Effect("test", lambda _: 1.0).add_steps([multiplier(0.25, 1.0)])
    state = EffectState()
    timer = EffectTimer(duration=1.0)

    effect.update(state, timer)
    value = effect.value(state, 0.0)

    assert value == pytest.approx(0.25)


def test_multiplier_interpolates_toward_end_value_as_duration_progresses() -> None:
    # Timer at progress 0.5 → multiplier should be midpoint between 0.0 and 1.0.
    effect = Effect("test", lambda _: 1.0).add_steps([multiplier(0.0, 1.0)])
    state = EffectState()
    timer = EffectTimer(duration=1.0)
    timer.update(0.5)

    effect.update(state, timer)
    value = effect.value(state, 0.0)

    assert value == pytest.approx(0.5)


def test_multiplier_is_at_end_value_just_before_duration_completes() -> None:
    # At progress just below 1.0 the step is still active and the multiplier
    # should be very close to the end value. At exactly 1.0 the step clears
    # its state (tested separately below).
    effect = Effect("test", lambda _: 1.0).add_steps([multiplier(0.0, 0.75)])
    state = EffectState()
    timer = EffectTimer(duration=1.0)
    timer.update(0.9999)

    effect.update(state, timer)
    value = effect.value(state, 0.0)

    assert value == pytest.approx(0.75, rel=1e-3)


def test_multiplier_clears_state_after_duration_completes_so_it_does_not_modify_subsequent_samples() -> (
    None
):
    # At progress >= 1.0 MultiplierStep removes its data so adjust_value
    # passes the shape value through unmodified.
    step = multiplier(0.0, 0.5)
    effect = Effect("test", lambda _: 1.0).add_steps([step])
    state = EffectState()
    timer = EffectTimer(duration=1.0)
    timer.update(1.0)

    effect.update(state, timer)

    assert state.get_step_data(step, object) is None
