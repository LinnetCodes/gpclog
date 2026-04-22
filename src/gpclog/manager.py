# src/gpclog/manager.py
"""GPCLoggerManager - Singleton logger manager."""

from typing import ClassVar, Optional
from loguru import logger as loguru_logger

from gpconfig import GPConfigFolder

from gpclog.config import GPCLoggerConfig
from gpclog.logger import GPCLogger


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

        Args:
            cfg_folder: GPConfigFolder instance containing logger configurations.
        """
        self._config_folder = cfg_folder

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

        # Check cache first
        if cache_key in self._loggers:
            return self._loggers[cache_key]

        # Get or create configuration using original logger_name
        config = self._get_config(logger_name)

        # Override name to include sn if provided
        if sn is not None:
            config = GPCLoggerConfig(
                name=f"{logger_name}-{sn}",
                level=config.level,
                file_format=config.file_format,
                console_format=config.console_format,
                output_to_stdout=config.output_to_stdout,
                output_to_stderr=config.output_to_stderr,
                output_to_file=config.output_to_file,
                log_path=config.log_path,
                rotation_enabled=config.rotation_enabled,
                rotation_size=config.rotation_size,
                retention_enabled=config.retention_enabled,
                retention_days=config.retention_days,
            )

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
                config = self._config_folder.get_config(logger_name, GPCLoggerConfig)
                # Merge with defaults for missing fields
                return self._merge_with_defaults(config)
            except Exception:
                # Config not found, try default.yaml
                try:
                    default_config = self._config_folder.get_config(
                        "default", GPCLoggerConfig
                    )
                    self._default_config = self._merge_with_defaults(default_config)
                except Exception:
                    pass

        # Use default config with the logger name
        return GPCLoggerConfig(
            name=logger_name,
            level=self._default_config.level,
            file_format=self._default_config.file_format,
            console_format=self._default_config.console_format,
            output_to_stdout=self._default_config.output_to_stdout,
            output_to_stderr=self._default_config.output_to_stderr,
            output_to_file=self._default_config.output_to_file,
            log_path=self._default_config.log_path,
            rotation_enabled=self._default_config.rotation_enabled,
            rotation_size=self._default_config.rotation_size,
            retention_enabled=self._default_config.retention_enabled,
            retention_days=self._default_config.retention_days,
        )

    def _merge_with_defaults(self, config: GPCLoggerConfig) -> GPCLoggerConfig:
        """Merge user config with defaults for missing fields.

        Args:
            config: User-provided configuration.

        Returns:
            GPCLoggerConfig with all fields filled.
        """
        defaults = self._default_config
        return GPCLoggerConfig(
            name=config.name,
            level=config.level if config.level else defaults.level,
            file_format=config.file_format
            if config.file_format
            else defaults.file_format,
            console_format=config.console_format
            if config.console_format
            else defaults.console_format,
            output_to_stdout=config.output_to_stdout
            if config.output_to_stdout is not None
            else defaults.output_to_stdout,
            output_to_stderr=config.output_to_stderr
            if config.output_to_stderr is not None
            else defaults.output_to_stderr,
            output_to_file=config.output_to_file
            if config.output_to_file is not None
            else defaults.output_to_file,
            log_path=config.log_path if config.log_path else defaults.log_path,
            rotation_enabled=config.rotation_enabled
            if config.rotation_enabled is not None
            else defaults.rotation_enabled,
            rotation_size=config.rotation_size
            if config.rotation_size
            else defaults.rotation_size,
            retention_enabled=config.retention_enabled
            if config.retention_enabled is not None
            else defaults.retention_enabled,
            retention_days=config.retention_days
            if config.retention_days is not None
            else defaults.retention_days,
        )
