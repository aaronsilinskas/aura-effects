import time
import gc

import neopixel

try:
    from typing import Callable
except ImportError:
    pass  # No typing support on CircuitPython yet

from effects.effect import EffectState, EffectTimer
from effects.elements.registry import get_element_builder, list_element_names
from effects.render import EffectRenderer, RendererConfig
from performance import PerformanceTracker

import board


NUM_LEDS = 12
ring_pixels = neopixel.NeoPixel(
    pin=board.D5, n=NUM_LEDS, brightness=0.25, auto_write=False
)

# PropMaker external power enable
# power = digitalio.DigitalInOut(board.EXTERNAL_POWER)
# power.switch_to_output(value=True)
# NUM_LEDS = 20
# ring_pixels = hw.setup_neopixels(
#     "ring", count=NUM_LEDS, brightness=0.50, data=board.EXTERNAL_NEOPIXELS
# )

# test_timed = TimedFunction(palette_gradient_with_gamma, log_interval=100)

last_update = time.monotonic()

timer = EffectTimer()
state = EffectState()


def logging_listener(event_name: str) -> None:
    print(f"Event: {event_name}")


def create_renderer(
    level: int, build_func: Callable[[RendererConfig], EffectRenderer]
) -> EffectRenderer:
    renderer_config = RendererConfig(
        level=level,
        pixel_count=NUM_LEDS,
        resolution=NUM_LEDS * 3,
        listeners=[logging_listener],
    )
    return build_func(renderer_config)


selected_element = "time"
render_func = get_element_builder(selected_element)
print("Selected element:", selected_element)
print("Available elements:", ", ".join(list_element_names()))


current_level = 1
current_renderer = create_renderer(level=current_level, build_func=render_func)


perf = PerformanceTracker(log_interval=5.0)
level_change_delay = 10.0
next_level_change_time = time.monotonic() + level_change_delay

while True:
    current_time = time.monotonic()
    elapsed_time = current_time - last_update
    last_update = current_time

    timer.update(elapsed_time)

    perf.start_frame()

    perf.start_update_time()
    current_renderer.update(state, timer)
    perf.add_update_time()

    perf.start_render_time()
    for led_index in range(NUM_LEDS):
        position = led_index / NUM_LEDS
        color = current_renderer.render(state, position)
        ring_pixels[led_index] = color
    perf.add_render_time()

    ring_pixels.show()

    perf.complete_frame(current_time)

    if current_time > next_level_change_time:
        current_level += 1
        if current_level > 10:
            current_level = 1
        print(f"CHANGING LEVEL TO {current_level}")
        state = EffectState()  # NOTE: Be absolutely sure to clear state!
        current_renderer = create_renderer(level=current_level, build_func=render_func)
        gc.collect()
        next_level_change_time = current_time + level_change_delay
