from __future__ import annotations

import random

try:
    from typing import Callable, TypeAlias
except ImportError:
    pass  # No typing support on CircuitPython yet

GAMMA_FACTOR = 2.7

DynamicValue: TypeAlias = "float | Callable[[], float]"


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


class Range:
    __slots__ = ("start", "end")

    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end

    def lerp(self, progress: float) -> float:
        if progress >= 1.0:
            return self.end
        return lerp(self.start, self.end, progress)


class ValueGenerator:

    @staticmethod
    def resolve(value: DynamicValue) -> float:
        if callable(value):
            return value()
        return value

    @staticmethod
    def random(min_value: float = 0.0, max_value: float = 1.0) -> DynamicValue:
        return lambda: random.uniform(min_value, max_value)

    @staticmethod
    def random_choice(choices: list[float]) -> DynamicValue:
        return lambda: random.choice(choices)
