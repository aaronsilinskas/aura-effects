import pytest

from effects.level import clamp_level, level_lerp, level_lerp_int, level_progress


# ---------------------------------------------------------------------------
# clamp_level
# ---------------------------------------------------------------------------


def test_clamp_level_returns_level_unchanged_within_valid_range() -> None:
    for level in range(1, 11):
        assert clamp_level(level) == level


def test_clamp_level_clamps_below_minimum_to_one() -> None:
    assert clamp_level(0) == 1
    assert clamp_level(-100) == 1


def test_clamp_level_clamps_above_maximum_to_ten() -> None:
    assert clamp_level(11) == 10
    assert clamp_level(100) == 10


# ---------------------------------------------------------------------------
# level_progress
# ---------------------------------------------------------------------------


def test_level_progress_is_zero_at_minimum_level() -> None:
    assert level_progress(1) == pytest.approx(0.0)


def test_level_progress_is_one_at_maximum_level() -> None:
    assert level_progress(10) == pytest.approx(1.0)


def test_level_progress_is_half_at_midpoint_level() -> None:
    assert level_progress(5) == pytest.approx(4 / 9)


def test_level_progress_clamps_out_of_range_input() -> None:
    assert level_progress(0) == pytest.approx(0.0)
    assert level_progress(11) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# level_lerp
# ---------------------------------------------------------------------------


def test_level_lerp_returns_minimum_at_level_one() -> None:
    assert level_lerp(1, 0.2, 0.8) == pytest.approx(0.2)


def test_level_lerp_returns_maximum_at_level_ten() -> None:
    assert level_lerp(10, 0.2, 0.8) == pytest.approx(0.8)


def test_level_lerp_interpolates_proportionally_at_midpoint() -> None:
    result = level_lerp(5, 0.0, 1.0)

    assert result == pytest.approx(4 / 9)


def test_level_lerp_clamps_out_of_range_level() -> None:
    assert level_lerp(0, 0.0, 1.0) == pytest.approx(0.0)
    assert level_lerp(11, 0.0, 1.0) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# level_lerp_int
# ---------------------------------------------------------------------------


def test_level_lerp_int_returns_minimum_at_level_one() -> None:
    assert level_lerp_int(1, 10, 200) == 10


def test_level_lerp_int_returns_maximum_at_level_ten() -> None:
    assert level_lerp_int(10, 10, 200) == 200


def test_level_lerp_int_rounds_to_nearest_integer() -> None:
    # level 2: progress = 1/9 → value = 10 + (1/9)*190 ≈ 31.1 → rounds to 31
    assert level_lerp_int(2, 10, 200) == 31
