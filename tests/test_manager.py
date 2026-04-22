# tests/test_manager.py
"""Tests for GPCLoggerManager."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from gpclog.config import GPCLoggerConfig
from gpclog.logger import GPCLogger
from gpclog.manager import GPCLoggerManager


class TestGPCLoggerManager:
    """Test GPCLoggerManager class."""

    def setup_method(self) -> None:
        """Reset singleton before each test."""
        GPCLoggerManager._instance = None
        GPCLogger.clear_cache()

    def test_singleton_pattern(self, tmp_path: Path) -> None:
        """Test that GPCLoggerManager is a singleton."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            manager1 = GPCLoggerManager()
            manager2 = GPCLoggerManager()

        assert manager1 is manager2

    def test_get_logger_returns_gpclogger(self, tmp_path: Path) -> None:
        """Test that get_logger returns a GPCLogger instance."""
        from gpclog.logger import GPCLogger

        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            manager = GPCLoggerManager()
            logger = manager.get_logger("test_logger")

        assert isinstance(logger, GPCLogger)
        assert logger.name == "test_logger"

    def test_get_logger_caches_instances(self, tmp_path: Path) -> None:
        """Test that get_logger returns cached instance for same name."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            manager = GPCLoggerManager()
            logger1 = manager.get_logger("cached_logger")
            logger2 = manager.get_logger("cached_logger")

        assert logger1 is logger2

    def test_get_logger_different_names(self, tmp_path: Path) -> None:
        """Test that different names return different loggers."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            manager = GPCLoggerManager()
            logger1 = manager.get_logger("logger1")
            logger2 = manager.get_logger("logger2")

        assert logger1 is not logger2
        assert logger1.name != logger2.name

    def test_default_config_exists(self, tmp_path: Path) -> None:
        """Test that default config is created."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            manager = GPCLoggerManager()

        assert manager.default_config is not None
        assert isinstance(manager.default_config, GPCLoggerConfig)
        assert manager.default_config.level == "INFO"

    def test_set_config_folder(self, tmp_path: Path) -> None:
        """Test setting config folder."""
        from gpconfig import GPConfigFolder

        mock_folder = MagicMock(spec=GPConfigFolder)

        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            manager = GPCLoggerManager()
            manager.set_config_folder(mock_folder)

        assert manager.config_folder is mock_folder

    def test_get_logger_with_sn_returns_correct_name(self, tmp_path: Path) -> None:
        """Test that get_logger with sn returns a logger with hyphenated name."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            manager = GPCLoggerManager()
            logger = manager.get_logger("database", sn=1)

        assert logger.name == "database-1"

    def test_get_logger_with_sn_caches_independently(self, tmp_path: Path) -> None:
        """Test that different sn values produce independent cached loggers."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            manager = GPCLoggerManager()
            logger_base = manager.get_logger("database")
            logger_sn1 = manager.get_logger("database", sn=1)
            logger_sn2 = manager.get_logger("database", sn=2)

        assert logger_base is not logger_sn1
        assert logger_base is not logger_sn2
        assert logger_sn1 is not logger_sn2
        assert logger_base.name == "database"
        assert logger_sn1.name == "database-1"
        assert logger_sn2.name == "database-2"

    def test_get_logger_with_sn_same_cache_hit(self, tmp_path: Path) -> None:
        """Test that same (logger_name, sn) returns cached instance."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            manager = GPCLoggerManager()
            logger1 = manager.get_logger("database", sn=1)
            logger2 = manager.get_logger("database", sn=1)

        assert logger1 is logger2

    def test_get_logger_with_sn_uses_base_config(self, tmp_path: Path) -> None:
        """Test that sn logger uses config from original logger_name."""
        from gpconfig import GPConfigFolder

        mock_folder = MagicMock(spec=GPConfigFolder)
        mock_config = GPCLoggerConfig(
            name="database",
            level="DEBUG",
            output_to_file=False,
        )
        mock_folder.get_config.return_value = mock_config

        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            manager = GPCLoggerManager()
            manager.set_config_folder(mock_folder)
            logger = manager.get_logger("database", sn=1)

        # Config was looked up with original name "database"
        mock_folder.get_config.assert_called_with("database", GPCLoggerConfig)
        # But logger name has sn appended
        assert logger.name == "database-1"
        # Config level should be DEBUG (from the mock config, merged)
        assert logger.config.level == "DEBUG"
