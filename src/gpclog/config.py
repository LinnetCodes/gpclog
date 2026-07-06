# src/gpclog/config.py
"""GPCLoggerConfig - Configuration class for GPCLogger."""

import re
from typing import ClassVar

from gpconfig import GPConfig
from pydantic import field_validator, model_validator

# Rotation size must be a number optionally followed by whitespace and a
# unit of KB, MB, or GB (case-insensitive). e.g. "10 MB", "500KB", "1 GB".
_ROTATION_SIZE_PATTERN = re.compile(r"^\d+\s*(KB|MB|GB)$", re.IGNORECASE)


class GPCLoggerConfig(GPConfig):
    """Configuration for GPCLogger.

    Attributes:
        cfg_class_name: Class identifier for gpconfig auto-detection.
        configured_class_name: Name of the configurable class (always "GPCLogger").
        level: Log level; must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL
            (case-sensitive uppercase). Any other value (including "") is rejected.
        file_format: Format string for file output.
        console_format: Format string for console output.
        output_to_stdout: Whether to output to stdout.
        output_to_stderr: Whether to output to stderr.
        output_to_file: Whether to output to file.
        log_dir: Directory for log output (auto, env, home, or absolute path).
            Renamed from log_path to make clear this is a directory, not a file.
        rotation_enabled: Whether to enable log rotation.
        rotation_size: Rotation size threshold (e.g., "10 MB"); must match
            "<number> <KB|MB|GB>" (case-insensitive).
        retention_enabled: Whether to enable log retention/deletion.
        retention_days: Number of days to retain logs; must be >= 0, and when
            retention_enabled is True must be > 0 (0 deletes logs immediately).
    """

    cfg_class_name: ClassVar[str] = "GPCLoggerConfig"

    VALID_LEVELS: ClassVar[set[str]] = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    # Required fields
    configured_class_name: str = "GPCLogger"
    level: str = "INFO"

    # Optional fields with defaults
    file_format: str = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[name]} | {message}"
    )
    console_format: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{extra[name]}</cyan> | "
        "<level>{message}</level>"
    )

    output_to_stdout: bool = True
    output_to_stderr: bool = False
    output_to_file: bool = True

    log_dir: str = "auto"

    rotation_enabled: bool = False
    rotation_size: str = "10 MB"

    retention_enabled: bool = False
    retention_days: int = 7

    @field_validator("level")
    @classmethod
    def _validate_level(cls, v: str) -> str:
        """Ensure level is a recognized uppercase log level."""
        if v not in cls.VALID_LEVELS:
            raise ValueError(
                f"level must be one of {sorted(cls.VALID_LEVELS)} "
                f"(case-sensitive), got {v!r}"
            )
        return v

    @field_validator("rotation_size")
    @classmethod
    def _validate_rotation_size(cls, v: str) -> str:
        """Ensure rotation_size looks like '<number> <KB|MB|GB>'."""
        if not _ROTATION_SIZE_PATTERN.match(v):
            raise ValueError(
                "rotation_size must match '<number> <KB|MB|GB>' "
                "(case-insensitive), e.g. '10 MB'; "
                f"got {v!r}"
            )
        return v

    @model_validator(mode="after")
    def _validate_retention(self) -> "GPCLoggerConfig":
        """Enforce retention_days rules: >= 0 always, > 0 when enabled."""
        if self.retention_days < 0:
            raise ValueError(f"retention_days must be >= 0, got {self.retention_days}")
        if self.retention_enabled and self.retention_days <= 0:
            raise ValueError(
                "retention_days must be > 0 when retention_enabled is True "
                "(0 would delete logs immediately)"
            )
        return self
