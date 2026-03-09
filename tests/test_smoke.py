from effects.effect import Effect, EffectState, EffectTimer
from effects.palette import PaletteLUT256
from effects.render import EffectRenderer


def test_effect_renderer_returns_rgb_int() -> None:
    effect = Effect("demo", lambda _: 1.0)
    palette = PaletteLUT256(bytes([0, 0, 0, 0, 255, 255, 0, 0]))
    renderer = EffectRenderer(effect, palette)

    state = EffectState()
    timer = EffectTimer()
    timer.update(0.016)
    renderer.update(state, timer)

    color = renderer.render(state, 1.0)

    assert isinstance(color, int)
    assert color == 0xFF0000


def test_registry_includes_time() -> None:
    from effects.elements.registry import list_element_names

    assert "time" in list_element_names()
