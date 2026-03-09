try:
    from typing import Iterable
except ImportError:
    pass  # No typing support on CircuitPython yet

from effects.effect import EffectState, EffectStep, EffectTimer, run_step_updates
from effects.value import DynamicValue, ValueGenerator


class DurationStep(EffectStep):
    def __init__(
        self,
        duration: DynamicValue,
        persist_steps: bool,
        steps: Iterable[EffectStep],
    ):
        self.duration = duration
        self.persist_steps = persist_steps
        self.steps = list(steps)

    class _Data:
        def __init__(self, duration: float):
            self.timer = EffectTimer(duration=duration)
            self.step_index: int = 0

    def update(self, state: EffectState, timer: EffectTimer) -> bool:
        data = state.get_step_data(self, DurationStep._Data)
        if data is None:
            data = self._Data(ValueGenerator.resolve(self.duration))
            state.set_step_data(self, data)

        data.timer.update(timer.elapsed)

        data.step_index = run_step_updates(
            self.steps, data.step_index, state, data.timer
        )

        if data.timer.progress >= 1.0:
            if self.persist_steps:
                data = self._Data(ValueGenerator.resolve(self.duration))
                state.set_step_data(self, data)
            else:
                state.remove_step_data(self)
            return True

        return False

    def adjust_position(self, state: EffectState, position: float) -> float:
        data = state.get_step_data(self, DurationStep._Data)
        if data is not None:
            for step in self.steps:
                position = step.adjust_position(state, position)

        return position

    def adjust_value(self, state: EffectState, position: float, value: float) -> float:
        data = state.get_step_data(self, DurationStep._Data)
        if data is not None:
            for step in self.steps:
                value = step.adjust_value(state, position, value)

        return value


def duration(
    duration: DynamicValue,
    persist_steps: bool = False,
    steps: Iterable[EffectStep] = (),
) -> EffectStep:
    return DurationStep(duration, persist_steps, steps)
