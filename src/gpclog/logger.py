# src/gpclog/logger.py
"""GPCLogger - Configurable logger class."""

import sys
from typing import Any, ClassVar

from gpconfig import GPConfigurable
from loguru import logger as loguru_logger

from gpclog.config import GPCLoggerConfig
from gpclog.utils import resolve_log_path, validate_logger_name


class GPCLogger(GPConfigurable):
    """A configurable logger that wraps loguru.

    This class provides a category-based logger with configuration support
    through GPCLoggerConfig. Each logger instance writes to its own file
    and can be configured independently.

    Note:
        There are two cache layers: ``GPCLoggerManager._loggers`` dedups
        GPCLogger instances, and ``GPCLogger._bound_loggers`` dedups loguru
        handlers. Both are cleared by ``reset()``.

    Warning:
        The class-level ``_bound_loggers`` cache is NOT thread-safe (a
        check-then-set race exists in ``_create_logger``). Initialize loggers
        from the main thread before spawning worker threads.
    """

    # Class-level cache for bound loguru loggers to prevent duplicate handlers
    _bound_loggers: ClassVar[dict[str, Any]] = {}

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the bound loggers cache.

        This should be called when the singleton manager is reset to ensure
        that cached loggers with stale handlers are not reused.
        """
        cls._bound_loggers.clear()

    def __init__(self, config: GPCLoggerConfig) -> None:
        """Initialize the logger with configuration.

        Args:
            config: GPCLoggerConfig instance containing logger settings.
        """
        super().__init__(config)
        self._name: str = config.name or "default"
        validate_logger_name(self._name)
        self._logger = self._create_logger(config)

    @property
    def name(self) -> str:
        """Get the logger name."""
        return self._name

    def _create_logger(self, config: GPCLoggerConfig) -> Any:
        """Create and configure a loguru logger.

        Uses loguru's filter mechanism to allow multiple GPCLogger instances
        to coexist and write to different files. Each logger binds its name
        to the record's extra dict, and handlers use filters to route
        messages to the appropriate sinks.

        If a logger with the same name has already been bound, returns the
        cached instance to avoid adding duplicate handlers.

        Args:
            config: Configuration for the logger.

        Returns:
            Configured loguru logger instance with bound name.
        """
        # Check if a logger with this name already exists in cache
        if self._name in self._bound_loggers:
            return self._bound_loggers[self._name]

        # Create a logger filter function that captures the name by value
        # to avoid closure issues with late binding
        logger_name = self._name

        def name_filter(record: dict) -> bool:
            """Filter records by logger name."""
            return record["extra"].get("name") == logger_name

        # Create a new logger with bound context
        new_logger = loguru_logger.bind(name=self._name)

        # Add console handler if enabled
        if config.output_to_stdout:
            loguru_logger.add(
                sink=sys.stdout,
                format=config.console_format,
                level=config.level,
                colorize=True,
                filter=name_filter,
            )

        # Add stderr handler if enabled
        if config.output_to_stderr:
            loguru_logger.add(
                sink=sys.stderr,
                format=config.console_format,
                level=config.level,
                colorize=True,
                filter=name_filter,
            )

        # Add file handler if enabled
        if config.output_to_file:
            log_dir = resolve_log_path(config.log_dir)
            log_file = log_dir / f"{self._name}.log"

            # Configure rotation
            rotation = None
            if config.rotation_enabled:
                rotation = config.rotation_size

            # Configure retention
            retention = None
            if config.retention_enabled:
                retention = f"{config.retention_days} days"

            loguru_logger.add(
                sink=str(log_file),
                format=config.file_format,
                level=config.level,
                rotation=rotation,
                retention=retention,
                encoding="utf-8",
                filter=name_filter,
            )

        # Cache the bound logger to prevent duplicate handlers
        self._bound_loggers[self._name] = new_logger

        return new_logger

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        self._logger.critical(message, *args, **kwargs)
