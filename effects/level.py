def clamp_level(level: int) -> int:
    if level < 1:
        return 1
    if level > 10:
        return 10
    return level


def level_progress(level: int) -> float:
    clamped = clamp_level(level)
    return (clamped - 1) / 9.0


def level_lerp(level: int, minimum: float, maximum: float) -> float:
    progress = level_progress(level)
    return minimum + (maximum - minimum) * progress


def level_lerp_int(level: int, minimum: int, maximum: int) -> int:
    value = level_lerp(level, float(minimum), float(maximum))
    return int(value + 0.5)
