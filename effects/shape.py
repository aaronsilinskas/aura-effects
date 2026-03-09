import math

try:
    from typing import Callable, TypeAlias
except ImportError:
    pass

from effects.value import DynamicValue, GAMMA_FACTOR, ValueGenerator


EffectShapeFunc: TypeAlias = "Callable[[float], float]"


class Shape:
    @staticmethod
    def none() -> EffectShapeFunc:
        def shape(_: float) -> float:
            return 0.0

        return shape

    @staticmethod
    def gradient() -> EffectShapeFunc:
        gamma = GAMMA_FACTOR

        def shape(position: float) -> float:
            return pow(position % 1.0, gamma)

        return shape

    @staticmethod
    def centered_gradient() -> EffectShapeFunc:
        gamma = GAMMA_FACTOR

        def shape(position: float) -> float:
            pos = position % 1.0
            if pos < 0.5:
                return pow(pos * 2.0, gamma)

            return pow((1.0 - pos) * 2.0, gamma)

        return shape

    @staticmethod
    def padded(padding: float, shape_func: EffectShapeFunc) -> EffectShapeFunc:
        clamped_padding = max(0.0, min(0.5, padding))
        span = 1.0 - 2.0 * clamped_padding
        if span <= 0.0:
            return Shape.none()

        lower_bound = clamped_padding
        upper_bound = 1.0 - clamped_padding
        inv_span = 1.0 / span

        def shape(position: float) -> float:
            pos = position % 1.0
            if pos < lower_bound:
                return 0.0
            if pos > upper_bound:
                return 0.0

            return shape_func((pos - lower_bound) * inv_span)

        return shape

    @staticmethod
    def reverse(shape_func: EffectShapeFunc) -> EffectShapeFunc:
        def shape(position: float) -> float:
            return shape_func(1.0 - (position % 1.0))

        return shape

    @staticmethod
    def sine(frequency: DynamicValue) -> EffectShapeFunc:
        """Smooth sine wave with a given frequency"""
        frequency_value = ValueGenerator.resolve(frequency)
        tau = 2.0 * math.pi

        def shape(position: float) -> float:
            return math.sin(frequency_value * position * tau) / 2.0 + 0.5

        return shape

    @staticmethod
    def checkers(value: float, count: int, width: float) -> EffectShapeFunc:
        clamped_width = max(0.0, min(1.0, width))
        if count <= 0 or clamped_width <= 0.0:
            return Shape.none()

        span = 1.0 / count

        def shape(position: float) -> float:
            pos = position % 1.0
            mod_pos = pos % span

            if mod_pos < clamped_width:
                return value
            mod_pos -= clamped_width
            if mod_pos < clamped_width:
                return value - (value * mod_pos / clamped_width)

            return 0.0

        return shape
