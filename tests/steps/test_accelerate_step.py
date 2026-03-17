import pytest

from effects.effect import Effect, EffectState, EffectTimer
from effects.steps.position import VelocitySharedData, accelerate
from conftest import make_timer


def test_accelerate_interpolates_speed_at_midpoint_of_timer() -> None:
    # At progress=0.5, speed = lerp(0.0, 2.0, 0.5) = 1.0.
    # offset accumulated = 1.0 * 0.5s elapsed = 0.5.
    effect = Effect("test", lambda pos: pos % 1.0).add_steps(
        [accelerate(start=0.0, end=2.0)]
    )
    state = EffectState()
    timer = EffectTimer(duration=1.0)
    timer.update(0.5)

    effect.update(state, timer)
    value = effect.value(state, 0.0)

    assert value == pytest.approx(0.5)


def test_accelerate_applies_end_speed_when_timer_completes() -> None:
    # At progress=1.0, speed = end = 1.0. offset = 1.0 * 0.5s = 0.5.
    effect = Effect("test", lambda pos: pos % 1.0).add_steps(
        [accelerate(start=0.0, end=1.0)]
    )
    state = EffectState()
    timer = EffectTimer(duration=0.5)
    timer.update(0.5)

    effect.update(state, timer)
    value = effect.value(state, 0.0)

    assert value == pytest.approx(0.5)


def test_accelerate_seeds_start_speed_from_existing_velocity_when_not_set() -> None:
    # Pre-seed velocity so that start=None reads rps=2.0 instead of defaulting to 0.
    state = EffectState()
    vel = VelocitySharedData.get(state)
    vel.rotations_per_second = 2.0

    # With end=2.0 (same as seeded start), speed stays constant at 2.0.
    # offset = 2.0 * 0.25s = 0.5.
    effect = Effect("test", lambda pos: pos % 1.0).add_steps(
        [accelerate(start=None, end=2.0)]
    )
    timer = EffectTimer(duration=1000.0)
    timer.update(0.25)

    effect.update(state, timer)
    value = effect.value(state, 0.0)

    assert value == pytest.approx(0.5)
