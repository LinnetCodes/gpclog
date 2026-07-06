# src/gpclog/manager.py
"""GPCLoggerManager - Singleton logger manager."""

from typing import ClassVar, Optional
from loguru import logger as loguru_logger

from gpconfig import GPConfigFolder
from gpconfig.exceptions import ConfigNotFoundError

from gpclog.config import GPCLoggerConfig
from gpclog.logger import GPCLogger
from gpclog.utils import validate_logger_name


class GPCLoggerManager:
    """Singleton manager for GPCLogger instances.

    This class manages all logger instances and provides a central
    point for configuration management.
    """

    _instance: ClassVar[Optional["GPCLoggerManager"]] = None

    def __new__(cls) -> "GPCLoggerManager":
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
            loguru_logger.remove()
            # Clear the bound loggers cache since handlers were removed
            GPCLogger.clear_cache()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize the manager instance."""
        self._loggers: dict[tuple[str, Optional[int]], GPCLogger] = {}
        self._config_folder: Optional[GPConfigFolder] = None
        self._default_config: GPCLoggerConfig = self._create_default_config()

    def _create_default_config(self) -> GPCLoggerConfig:
        """Create the default configuration.

        Returns:
            GPCLoggerConfig with default values.
        """
        return GPCLoggerConfig(
            name="default",
            level="INFO",
        )

    @property
    def default_config(self) -> GPCLoggerConfig:
        """Get the default configuration."""
        return self._default_config

    @property
    def config_folder(self) -> Optional[GPConfigFolder]:
        """Get the config folder."""
        return self._config_folder

    def set_config_folder(self, cfg_folder: GPConfigFolder) -> None:
        """Set the configuration folder for logger configs.

        Eagerly loads a ``default.yaml`` from the folder (if present) as the
        fallback default configuration for loggers without their own config file.

        Args:
            cfg_folder: GPConfigFolder instance containing logger configurations.
        """
        self._config_folder = cfg_folder
        try:
            default_config = cfg_folder.get_config("default", GPCLoggerConfig)
            self._default_config = default_config
        except ConfigNotFoundError:
            pass  # No default.yaml — keep the built-in default.

    def get_logger(self, logger_name: str, sn: Optional[int] = None) -> GPCLogger:
        """Get or create a logger by name.

        If a logger with the given name and sn already exists, returns the cached
        instance. Otherwise, creates a new logger with the appropriate
        configuration.

        Args:
            logger_name: Unique name for the logger.
            sn: Optional serial number. When provided, creates a logger named
                "{logger_name}-{sn}" that uses the same configuration as
                logger_name. Useful for multiprocess isolation.

        Returns:
            GPCLogger instance for the given name.
        """
        cache_key = (logger_name, sn)

        # Validate before cache lookup so validation always runs,
        # consistent with the public gpclog.get_logger entry point.
        validate_logger_name(logger_name)

        if cache_key in self._loggers:
            return self._loggers[cache_key]

        # Get or create configuration using original logger_name
        config = self._get_config(logger_name)

        # Override name to include sn if provided
        if sn is not None:
            config = config.model_copy(update={"name": f"{logger_name}-{sn}"})

        # Create logger
        logger = GPCLogger(config)

        # Cache and return
        self._loggers[cache_key] = logger
        return logger

    def _get_config(self, logger_name: str) -> GPCLoggerConfig:
        """Get configuration for a logger.

        Tries to load configuration from config folder if set.
        Falls back to default configuration if not found.

        Args:
            logger_name: Name of the logger.

        Returns:
            GPCLoggerConfig for the logger.
        """
        # Try to get config from config folder
        if self._config_folder is not None:
            try:
                return self._config_folder.get_config(logger_name, GPCLoggerConfig)
            except ConfigNotFoundError:
                # Specific logger config not found — fall back to default config below.
                # (Validation/parse errors are NOT caught here — they propagate, per fail-early.)
                pass

        # Use default config with the logger name
        return self._default_config.model_copy(update={"name": logger_name})
