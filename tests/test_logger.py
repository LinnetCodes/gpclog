# tests/test_logger.py
"""Tests for GPCLogger."""

from pathlib import Path
from unittest.mock import patch


from gpclog.config import GPCLoggerConfig
from gpclog.logger import GPCLogger


class TestGPCLogger:
    """Test GPCLogger class."""

    def test_create_logger_with_config(self, tmp_path: Path) -> None:
        """Test creating a logger with configuration."""
        config = GPCLoggerConfig(
            name="test_logger",
            level="DEBUG",
            output_to_file=False,
            output_to_stdout=True,
            log_path=str(tmp_path),
        )

        with patch(
            "gpclog.logger.resolve_log_path", return_value=tmp_path / "gpclog_output"
        ):
            logger = GPCLogger(config)

        assert logger.name == "test_logger"
        assert hasattr(logger, "debug")
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        assert hasattr(logger, "critical")

    def test_logger_methods_work(self, tmp_path: Path) -> None:
        """Test that logger methods can be called."""
        config = GPCLoggerConfig(
            name="test",
            level="DEBUG",
            output_to_file=False,
            output_to_stdout=False,
        )

        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            logger = GPCLogger(config)

        # Should not raise
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")
        logger.critical("critical message")

    def test_logger_inherits_from_gpconfigurable(self, tmp_path: Path) -> None:
        """Test that GPCLogger inherits from GPConfigurable."""
        from gpconfig import GPConfigurable

        config = GPCLoggerConfig(
            name="test",
            level="INFO",
            output_to_file=False,
        )

        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            logger = GPCLogger(config)

        assert isinstance(logger, GPConfigurable)

    def test_logger_config_accessible(self, tmp_path: Path) -> None:
        """Test that config is accessible via config property."""
        config = GPCLoggerConfig(
            name="test",
            level="WARNING",
            output_to_file=False,
        )

        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            logger = GPCLogger(config)

        assert logger.config is config
        assert logger.config.level == "WARNING"

    def test_bound_logger_cache_prevents_duplicate_handlers(self, tmp_path: Path) -> None:
        """Test that cached bound loggers prevent duplicate handler creation."""
        from loguru import logger as loguru_logger

        # Clear any existing cache
        GPCLogger.clear_cache()

        config = GPCLoggerConfig(
            name="cached_logger",
            level="INFO",
            output_to_file=False,
            output_to_stdout=True,
        )

        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            # Count handlers before creating loggers
            initial_handler_count = len(loguru_logger._core.handlers)

            # Create first logger
            logger1 = GPCLogger(config)
            handler_count_after_first = len(loguru_logger._core.handlers)

            # Create second logger with same name
            logger2 = GPCLogger(config)
            handler_count_after_second = len(loguru_logger._core.handlers)

        # Both loggers should reference the same bound logger
        assert logger1._logger is logger2._logger

        # Handlers should only be added once (for the first logger)
        assert handler_count_after_first > initial_handler_count
        assert handler_count_after_second == handler_count_after_first

        # Clean up
        GPCLogger.clear_cache()
