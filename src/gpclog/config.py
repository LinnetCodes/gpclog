# src/gpclog/config.py
"""GPCLoggerConfig - Configuration class for GPCLogger."""

from typing import ClassVar

from gpconfig import GPConfig


class GPCLoggerConfig(GPConfig):
    """Configuration for GPCLogger.

    Attributes:
        cfg_class_name: Class identifier for gpconfig auto-detection.
        configured_class_name: Name of the configurable class (always "GPCLogger").
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        file_format: Format string for file output.
        console_format: Format string for console output.
        output_to_stdout: Whether to output to stdout.
        output_to_stderr: Whether to output to stderr.
        output_to_file: Whether to output to file.
        log_path: Log output path (auto, env, home, or absolute path).
        rotation_enabled: Whether to enable log rotation.
        rotation_size: Rotation size threshold (e.g., "10 MB").
        retention_enabled: Whether to enable log retention/deletion.
        retention_days: Number of days to retain logs.
    """

    cfg_class_name: ClassVar[str] = "GPCLoggerConfig"

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

    log_path: str = "auto"

    rotation_enabled: bool = False
    rotation_size: str = "10 MB"

    retention_enabled: bool = False
    retention_days: int = 7
