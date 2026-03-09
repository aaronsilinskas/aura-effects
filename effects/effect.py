from __future__ import annotations

from effects.value import DynamicValue, Range, ValueGenerator

try:
    from typing import Any, Callable, TypeVar, Iterable, Type

    T = TypeVar("T")
except ImportError:
    pass  # No typing support on CircuitPython yet

from effects.shape import EffectShapeFunc, Shape


_MISSING = object()


def run_step_updates(
    steps: list["EffectStep"],
    step_index: int,
    state: "EffectState",
    timer: "EffectTimer",
) -> int:
    step_count = len(steps)
    if step_count == 0:
        return step_index

    steps_processed = 0
    while steps_processed < step_count and steps[step_index].update(state, timer):
        step_index = (step_index + 1) % step_count
        steps_processed += 1

    return step_index


class SharedStateKey:
    pass


class EffectState:
    def __init__(self):
        self._step_indices: dict[Effect, int] = {}
        self._step_data: dict[EffectStep, "Any"] = {}
        self._shared_data: dict[SharedStateKey, "Any"] = {}

    def get_step_index(self, effect: Effect) -> int:
        return self._step_indices.get(effect, 0)

    def set_step_index(self, effect: Effect, index: int) -> None:
        self._step_indices[effect] = index

    def get_step_data(self, step: EffectStep, expected_class: "Type[T]") -> "T | None":
        return self._step_data.get(step)

    def set_step_data(self, step: EffectStep, value: "Any") -> None:
        self._step_data[step] = value

    def remove_step_data(self, step: EffectStep) -> None:
        self._step_data.pop(step, None)

    def get_shared_data(
        self, key: SharedStateKey, expected_class: "Type[T]"
    ) -> "T | None":
        return self._shared_data.get(key)

    def set_shared_data(self, key: SharedStateKey, value: "Any") -> None:
        self._shared_data[key] = value

    def remove_shared_data(self, key: SharedStateKey) -> None:
        self._shared_data.pop(key, None)

    def __str__(self):
        return (
            "EffectState("
            f"step_indices={self._step_indices}, step_data={self._step_data})"
        )


class EffectTimer:
    """Tracks frame timing for effect steps.

    `elapsed` is the last frame delta, `total` is cumulative elapsed time,
    and `progress` is normalized to [0, 1] when a finite duration is set. When
    duration is None, progress remains 0.0 and update always returns False.
    """

    __slots__ = ("elapsed", "total", "duration", "progress")

    def __init__(self, duration: float | None = None):
        """Initialize with optional finite duration in seconds.

        If `duration` is None, progress remains 0.0 and update always returns False.
        """
        self.elapsed: float = 0.0
        self.total: float = 0.0
        self.duration: float | None = duration
        self.progress: float = 0.0

    def update(self, elapsed: float) -> bool:
        """Advance timer by one frame delta and return whether duration is complete."""
        self.elapsed = elapsed
        self.total += elapsed
        if self.duration is not None:
            self.progress = min(1.0, self.total / self.duration)

        return self.progress >= 1.0

    def __str__(self) -> str:
        return f"EffectTimer(elapsed={self.elapsed}, total={self.total}, duration={self.duration}, progress={self.progress})"


class EffectStep:

    def update(self, state: EffectState, timer: EffectTimer) -> bool:
        raise NotImplementedError(
            "EffectStep subclasses must implement the update method"
        )

    def adjust_position(self, state: EffectState, position: float) -> float:
        return position

    def adjust_value(self, state: EffectState, position: float, value: float) -> float:
        return value


class Effect:
    def __init__(self, name: str, shape_func: EffectShapeFunc = Shape.none()):
        self.name = name
        self._shape: EffectShapeFunc = shape_func
        self._steps: list[EffectStep] = []

    def add_steps(self, steps: Iterable[EffectStep]) -> Effect:
        self._steps.extend(steps)
        return self

    def update(self, state: EffectState, timer: EffectTimer):
        step_index = state.get_step_index(self)
        next_step_index = run_step_updates(self._steps, step_index, state, timer)
        if next_step_index != step_index:
            state.set_step_index(self, next_step_index)

    def value(self, state: EffectState, position: float) -> float:
        steps = self._steps
        for step in steps:
            position = step.adjust_position(state, position)

        shape_value = self._shape(position)
        for step in steps:
            shape_value = step.adjust_value(state, position, shape_value)

        return max(0.0, min(1.0, shape_value))

    def __str__(self):
        return f"Effect(name={self.name}) at {hex(id(self))} )"
