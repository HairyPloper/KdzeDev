"""Validated iteration defaults, read when a workflow is configured."""

import os


def positive_integer(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError(f"{name} must be a positive integer (>= 1)")
    try:
        parsed = int(value)
    except ValueError:
        raise ValueError(f"{name} must be a positive integer (>= 1)") from None
    if parsed < 1:
        raise ValueError(f"{name} must be a positive integer (>= 1)")
    return parsed


def loop_counter_default() -> int:
    return positive_integer(
        os.environ.get("LOOP_COUNTER_MAX_ITERATIONS", "10"),
        "LOOP_COUNTER_MAX_ITERATIONS",
    )


def engine_cycle_default() -> int:
    return positive_integer(
        os.environ.get("ENGINE_MAX_ITERATIONS", "100"), "ENGINE_MAX_ITERATIONS"
    )
