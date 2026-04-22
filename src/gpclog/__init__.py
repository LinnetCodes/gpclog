"""gpclog - General Purpose Category Logger.

用于在复杂Python项目里管理分类日志。
"""

from typing import Optional

from gpconfig import GPConfigFolder, GPConfigManager

from gpclog.config import GPCLoggerConfig
from gpclog.logger import GPCLogger
from gpclog.manager import GPCLoggerManager

__version__ = "0.2.0"

# Auto-register config and configurable classes with GPConfigManager
GPConfigManager.register_config_class(GPCLoggerConfig)
GPConfigManager.register_configurable_class(GPCLogger)

__all__ = [
    "get_logger",
    "set_config_folder",
    "reset",
    "GPCLogger",
    "GPCLoggerConfig",
]

# Singleton manager instance
_manager: GPCLoggerManager = GPCLoggerManager()


def get_logger(logger_name: str, sn: Optional[int] = None) -> GPCLogger:
    """Get or create a logger by name.

    This is the primary interface for obtaining loggers. Each unique
    logger_name creates a separate logger with its own configuration
    and output file.

    Args:
        logger_name: Unique name for the logger. This name is used
            for configuration lookup and (without sn) for the log file name.
        sn: Optional serial number for multiprocess isolation. When provided,
            the logger is named "{logger_name}-{sn}" and writes to
            "{logger_name}-{sn}.log", but still uses the configuration
            associated with logger_name.

    Returns:
        GPCLogger instance for the given name.

    Example:
        >>> db_logger = gpclog.get_logger("database")
        >>> db_logger.info("Connected to database")
        >>>
        >>> # In multiprocess scenario:
        >>> worker_logger = gpclog.get_logger("worker", sn=process_id)
        >>> worker_logger.info("Process started")
    """
    return _manager.get_logger(logger_name, sn)


def set_config_folder(cfg_folder: GPConfigFolder) -> None:
    """Set the configuration folder for logger configurations.

    After calling this function, logger configurations will be loaded
    from the specified folder. If a logger's configuration is not found,
    the default configuration is used.

    Args:
        cfg_folder: GPConfigFolder instance containing logger
            configuration files.

    Example:
        >>> from gpconfig import GPConfigManager, GPConfigFolder
        >>> manager = GPConfigManager("myapp")
        >>> folder = GPConfigFolder(manager, "logs")
        >>> gpclog.set_config_folder(folder)
    """
    _manager.set_config_folder(cfg_folder)


def reset() -> None:
    """Reset the logger manager and clear all caches.

    This function is primarily intended for testing purposes to ensure
    a clean state between tests. It resets the internal state and clears
    all cached loggers.
    """
    global _manager
    GPCLoggerManager._instance = None
    GPCLogger.clear_cache()
    _manager = GPCLoggerManager()
