try:
    from typing import Callable, TypeAlias
except ImportError:
    pass

from effects.effect import Effect, EffectState, EffectTimer
from effects.palette import Palette


EffectListenerFunc: TypeAlias = "Callable[[str], None]"


class RendererConfig:
    __slots__ = ["level", "pixel_count", "resolution", "listeners"]

    def __init__(
        self,
        level: int,
        pixel_count: int,
        resolution: int,
        listeners: list[EffectListenerFunc] | None = None,
    ):
        self.level = min(max(1, level), 10)
        self.pixel_count = max(1, pixel_count)
        self.resolution = max(1, resolution)
        self.listeners = listeners if listeners is not None else []

    def notify_listeners(self, event_name: str) -> None:
        for listener in self.listeners:
            listener(event_name)


class EffectRenderer:
    def __init__(self, effect: Effect, palette: Palette):
        self._effect = effect
        self._palette = palette

    def update(self, state: EffectState, timer: EffectTimer) -> None:
        self._effect.update(state, timer)

    def render(self, state: EffectState, position: float) -> int:
        value = self._effect.value(state, position)
        color = self._palette.lookup(value)
        return color


class AverageMergeRenderer(EffectRenderer):
    def __init__(self, renderers: list[EffectRenderer]):
        self._renderers = renderers

    def update(self, state: EffectState, timer: EffectTimer) -> None:
        for renderer in self._renderers:
            renderer.update(state, timer)

    def render(self, state: EffectState, position: float) -> int:
        r_total = 0
        g_total = 0
        b_total = 0
        for renderer in self._renderers:
            color = renderer.render(state, position)
            r = (color >> 16) & 255
            g = (color >> 8) & 255
            b = color & 255
            r_total += r
            g_total += g
            b_total += b

        count = len(self._renderers)
        r = min(255, r_total // count)
        g = min(255, g_total // count)
        b = min(255, b_total // count)
        return (r << 16) | (g << 8) | b


class AdditiveMergeRenderer(EffectRenderer):
    def __init__(self, renderers: list[EffectRenderer]):
        self._renderers = renderers

    def update(self, state: EffectState, timer: EffectTimer) -> None:
        for renderer in self._renderers:
            renderer.update(state, timer)

    def render(self, state: EffectState, position: float) -> int:
        r_total = 0
        g_total = 0
        b_total = 0
        for renderer in self._renderers:
            color = renderer.render(state, position)
            r = (color >> 16) & 255
            g = (color >> 8) & 255
            b = color & 255
            r_total += r
            g_total += g
            b_total += b

        r = min(255, r_total)
        g = min(255, g_total)
        b = min(255, b_total)
        return (r << 16) | (g << 8) | b
