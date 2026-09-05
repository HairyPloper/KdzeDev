"""Configuration for loop counter guard nodes."""

from dataclasses import dataclass, field
from typing import Mapping, Any, Optional
from utils.iteration_limits import loop_counter_default, positive_integer

from entity.configs.base import (
    BaseConfig,
    ConfigError,
    ConfigFieldSpec,
    require_mapping,
    extend_path,
    optional_str,
)


@dataclass
class LoopCounterConfig(BaseConfig):
    """Configuration schema for the loop counter node type."""

    max_iterations: int = field(default_factory=loop_counter_default)
    reset_on_emit: bool = True
    message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None, *, path: str) -> "LoopCounterConfig":
        mapping = require_mapping(data or {}, path)
        max_iterations_raw = mapping.get("max_iterations")
        try:
            max_iterations = (
                loop_counter_default() if max_iterations_raw is None
                else positive_integer(max_iterations_raw, "max_iterations")
            )
        except ValueError as exc:
            raise ConfigError(
                str(exc),
                extend_path(path, "max_iterations"),
            ) from exc

        reset_on_emit = bool(mapping.get("reset_on_emit", True))
        message = optional_str(mapping, "message", path)

        return cls(
            max_iterations=max_iterations,
            reset_on_emit=reset_on_emit,
            message=message,
            path=path,
        )

    def validate(self) -> None:
        try:
            self.max_iterations = positive_integer(self.max_iterations, "max_iterations")
        except ValueError as exc:
            raise ConfigError(str(exc), extend_path(self.path, "max_iterations")) from exc

    FIELD_SPECS = {
        "max_iterations": ConfigFieldSpec(
            name="max_iterations",
            display_name="Maximum Iterations",
            type_hint="int",
            required=False,
            description="How many times this node is triggered before it emits output. Leave empty to use LOOP_COUNTER_MAX_ITERATIONS from the backend environment (default 10). Enter a positive integer to override it for this node.",
        ),
        "reset_on_emit": ConfigFieldSpec(
            name="reset_on_emit",
            display_name="Reset After Emit",
            type_hint="bool",
            required=False,
            default=True,
            description="Whether to reset the internal counter after reaching the limit.",
            advance=True,
        ),
        "message": ConfigFieldSpec(
            name="message",
            display_name="Release Message",
            type_hint="text",
            required=False,
            description="Optional text sent downstream once the iteration cap is reached.",
            advance=True,
        ),
    }
