try:
    from typing import Callable
except ImportError:
    pass  # No typing support on CircuitPython yet

from effects.effect import EffectState, EffectStep, EffectTimer
from effects.value import DynamicValue, ValueGenerator


class HideStep(EffectStep):

    def __init__(self, duration: DynamicValue):
        self.duration = duration

    def update(self, state: EffectState, timer: EffectTimer) -> bool:
        duration_timer = state.get_step_data(self, EffectTimer)
        if duration_timer is None:
            duration_timer = EffectTimer(duration=ValueGenerator.resolve(self.duration))
            state.set_step_data(self, duration_timer)

        if duration_timer.update(timer.elapsed):
            state.remove_step_data(self)
            return True

        return False

    def adjust_value(self, state: EffectState, position: float, value: float) -> float:
        if state.get_step_data(self, EffectTimer) is not None:
            return 0.0

        return value


def hide(duration: DynamicValue) -> EffectStep:
    return HideStep(duration)


class CallStep(EffectStep):
    def __init__(self, callback: Callable[[EffectState, EffectTimer], None]):
        self.callback = callback

    def update(self, state: EffectState, timer: EffectTimer) -> bool:
        self.callback(state, timer)
        return True


def call(callback: Callable[[EffectState, EffectTimer], None]) -> EffectStep:
    return CallStep(callback)
