# tests/test_api.py
"""Tests for public API."""

from pathlib import Path
from unittest.mock import MagicMock, patch


import gpclog
from gpclog.logger import GPCLogger


class TestPublicAPI:
    """Test the public API exposed by gpclog package."""

    def setup_method(self) -> None:
        """Reset singleton before each test."""
        gpclog.reset()

    def test_get_logger_function(self, tmp_path: Path) -> None:
        """Test gpclog.get_logger() function."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            logger = gpclog.get_logger("api_test")

        assert isinstance(logger, GPCLogger)
        assert logger.name == "api_test"

    def test_set_config_folder_function(self, tmp_path: Path) -> None:
        """Test gpclog.set_config_folder() function."""
        from gpconfig import GPConfigFolder

        mock_folder = MagicMock(spec=GPConfigFolder)

        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            gpclog.set_config_folder(mock_folder)

        # Verify it was set (by getting a logger that would use it)
        from gpclog.manager import GPCLoggerManager

        manager = GPCLoggerManager()
        assert manager.config_folder is mock_folder

    def test_version_exposed(self) -> None:
        """Test that __version__ is exposed."""
        assert hasattr(gpclog, "__version__")
        assert gpclog.__version__ == "0.3.0"

    def test_all_exports(self) -> None:
        """Test that __all__ contains expected exports."""
        assert "get_logger" in gpclog.__all__
        assert "set_config_folder" in gpclog.__all__
        assert "reset" in gpclog.__all__
        assert "GPCLogger" in gpclog.__all__
        assert "GPCLoggerConfig" in gpclog.__all__

    def test_get_logger_with_sn(self, tmp_path: Path) -> None:
        """Test gpclog.get_logger() with sn parameter."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            logger = gpclog.get_logger("api_test", sn=1)

        assert isinstance(logger, GPCLogger)
        assert logger.name == "api_test-1"

    def test_get_logger_without_sn_unchanged(self, tmp_path: Path) -> None:
        """Test that get_logger() without sn works as before."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            logger = gpclog.get_logger("api_test")

        assert isinstance(logger, GPCLogger)
        assert logger.name == "api_test"

    def test_get_logger_sn_independent_caches(self, tmp_path: Path) -> None:
        """Test that sn and non-sn loggers are independently cached."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            logger_base = gpclog.get_logger("worker")
            logger_sn = gpclog.get_logger("worker", sn=0)

        assert logger_base is not logger_sn
        assert logger_base.name == "worker"
        assert logger_sn.name == "worker-0"
