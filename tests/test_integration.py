# tests/test_integration.py
"""Integration tests for gpclog."""

import os
import shutil
from pathlib import Path
from unittest.mock import patch

import gpclog
from gpclog.config import GPCLoggerConfig


class TestIntegration:
    """Integration tests for full workflows."""

    def setup_method(self) -> None:
        """Reset singleton and loguru handlers before each test."""
        # Reset the manager to clear all caches and handlers
        gpclog.reset()

    def test_basic_logging_workflow(self, tmp_path: Path) -> None:
        """Test basic logging workflow with file output."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            logger = gpclog.get_logger("integration_test")

            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.error("Test error message")

        # Check log file was created
        log_file = tmp_path / "integration_test.log"
        assert log_file.exists()

        # Check log content
        content = log_file.read_text(encoding="utf-8")
        assert "Test info message" in content
        assert "Test warning message" in content
        assert "Test error message" in content

    def test_multiple_loggers_different_files(self, tmp_path: Path) -> None:
        """Test that different loggers write to different files.

        Uses loguru's filter mechanism to allow multiple GPCLogger instances
        to coexist. Each logger's messages are routed to its own file based
        on the 'name' bound to the logger.
        """
        # Create both loggers with the same log path
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            logger1 = gpclog.get_logger("module_a")
            logger2 = gpclog.get_logger("module_b")

            # Log messages from both loggers (using INFO level since default is INFO)
            logger1.info("Message from module A")
            logger2.info("Message from module B")

            # Log more messages to verify isolation
            logger1.warning("Warning from module A")
            logger2.error("Error from module B")

        # Check file A contains only module_a messages
        file_a = tmp_path / "module_a.log"
        assert file_a.exists()
        content_a = file_a.read_text(encoding="utf-8")
        assert "Message from module A" in content_a
        assert "Warning from module A" in content_a
        # Verify module_b messages are NOT in file_a
        assert "Message from module B" not in content_a
        assert "Error from module B" not in content_a

        # Check file B contains only module_b messages
        file_b = tmp_path / "module_b.log"
        assert file_b.exists()
        content_b = file_b.read_text(encoding="utf-8")
        assert "Message from module B" in content_b
        assert "Error from module B" in content_b
        # Verify module_a messages are NOT in file_b
        assert "Message from module A" not in content_b
        assert "Warning from module A" not in content_b

    def test_log_rotation(self, tmp_path: Path) -> None:
        """Test log rotation configuration."""
        gpclog.reset()

        # Create logger with rotation config
        config = GPCLoggerConfig(
            name="rotating_log",
            level="INFO",
            rotation_enabled=True,
            rotation_size="1 KB",
            output_to_file=True,
            output_to_stdout=False,
        )

        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            from gpclog.logger import GPCLogger

            logger = GPCLogger(config)

            # Write enough to trigger rotation
            for i in range(100):
                logger.info(f"Test message number {i} " + "x" * 50)

        # Should have created log files
        log_files = list(tmp_path.glob("rotating_log*.log*"))
        assert len(log_files) >= 1

    def test_path_resolution_integration(self, tmp_path: Path) -> None:
        """Test that path resolution works with real file system."""
        # Create a custom log directory
        custom_log_dir = tmp_path / "my_logs"
        custom_log_dir.mkdir()

        with patch.dict(os.environ, {"GPCLOG_PATH": str(custom_log_dir)}):
            from gpclog.utils import resolve_log_path

            result = resolve_log_path("auto")

        assert result == custom_log_dir / "gpclog_output"
        assert result.exists()

    def test_with_gpconfig_integration(self, tmp_path: Path) -> None:
        """Test real-world scenario using gpconfig for configuration.

        This test simulates a typical user scenario where:
        1. GPCLoggerConfig and GPCLogger are registered with GPConfigManager
        2. Configuration is loaded from a config folder (tests/mocks/config)
        3. Multiple loggers are created from configuration files
        4. Each logger writes to its own file with specific settings
        """
        from gpconfig import GPConfigManager

        # Reset singleton for clean state
        gpclog.reset()

        # Get absolute paths for config and log directories
        project_root = Path(__file__).parent.parent
        config_dir = project_root / "tests" / "mocks" / "config"
        log_dir = project_root / "tests" / "mocks" / "log"

        # Ensure log directory exists, remove gpclog_output to test auto-creation
        log_dir.mkdir(parents=True, exist_ok=True)
        log_output_dir = log_dir / "gpclog_output"
        if log_output_dir.exists():
            shutil.rmtree(log_output_dir)

        # Set GPCLOG_PATH environment variable for log_dir: env configs
        env_vars = {"GPCLOG_PATH": str(log_dir)}

        with patch.dict(os.environ, env_vars, clear=False):
            # Classes are auto-registered when importing gpclog
            # Initialize GPConfigManager with our test config folder
            manager = GPConfigManager("gpclog_test", cfg_folder=config_dir)

            # Get loggers from configuration (using GPConfigManager to create objects)
            # These will be created via get_object() which uses the registered classes
            database_logger = manager.get_object("logs.database")
            event_bus_logger = manager.get_object("logs.event_bus")
            ui_logger = manager.get_object("logs.ui")

            # Test database logger (INFO level, output_to_stderr=True)
            database_logger.info("Database connection established")
            database_logger.debug(
                "This debug message should NOT appear"
            )  # Below INFO level

            # Test event_bus logger (DEBUG level, output_to_stdout=True)
            event_bus_logger.debug(
                "Event bus initialized"
            )  # Should appear at DEBUG level
            event_bus_logger.info("Processing event")

            # Test ui logger (WARNING level)
            ui_logger.warning("UI warning message")
            ui_logger.info("This info message should NOT appear")  # Below WARNING level
            ui_logger.error("UI error occurred")

        # Verify log files were created and contain correct content
        # Database logger (log_dir: env -> tests/mocks/log/gpclog_output)
        db_log_file = log_dir / "gpclog_output" / "database.log"
        assert db_log_file.exists(), "Database log file should exist"
        db_content = db_log_file.read_text(encoding="utf-8")
        assert "Database connection established" in db_content
        assert (
            "This debug message should NOT appear" not in db_content
        )  # Filtered by INFO level

        # Event bus logger (log_dir: env -> tests/mocks/log/gpclog_output)
        event_bus_log_file = log_dir / "gpclog_output" / "event_bus.log"
        assert event_bus_log_file.exists(), "Event bus log file should exist"
        event_bus_content = event_bus_log_file.read_text(encoding="utf-8")
        assert "Event bus initialized" in event_bus_content  # DEBUG level should appear
        assert "Processing event" in event_bus_content

        # UI logger (log_dir: absolute path -> tests/mocks/log/gpclog_output)
        ui_log_file = log_dir / "gpclog_output" / "ui.log"
        assert ui_log_file.exists(), "UI log file should exist"
        ui_content = ui_log_file.read_text(encoding="utf-8")
        assert "UI warning message" in ui_content
        assert "UI error occurred" in ui_content
        assert (
            "This info message should NOT appear" not in ui_content
        )  # Filtered by WARNING level

        # Verify log isolation: each logger's messages are in its own file only
        assert "Database connection established" not in event_bus_content
        assert "Database connection established" not in ui_content
        assert "Event bus initialized" not in db_content
        assert "Event bus initialized" not in ui_content
        assert "UI warning message" not in db_content
        assert "UI warning message" not in event_bus_content

    def test_with_gpclog_public_api(self, tmp_path: Path) -> None:
        """Test real-world scenario using gpclog public API.

        This test demonstrates the recommended way to use gpclog:
        1. Use GPConfigManager to load configuration from a folder
        2. Get GPConfigFolder for the logs subdirectory
        3. Call gpclog.set_config_folder() to configure logger settings
        4. Use gpclog.get_logger() to obtain loggers by name
        """
        from gpconfig import GPConfigManager

        # Reset singleton for clean state
        gpclog.reset()

        # Get absolute paths for config and log directories
        project_root = Path(__file__).parent.parent
        config_dir = project_root / "tests" / "mocks" / "config"
        log_dir = project_root / "tests" / "mocks" / "log"

        # Ensure log directory exists, remove gpclog_output to test auto-creation
        log_dir.mkdir(parents=True, exist_ok=True)
        log_output_dir = log_dir / "gpclog_output"
        if log_output_dir.exists():
            shutil.rmtree(log_output_dir)

        # Set GPCLOG_PATH environment variable for log_dir: env configs
        env_vars = {"GPCLOG_PATH": str(log_dir)}

        with patch.dict(os.environ, env_vars, clear=False):
            # Initialize GPConfigManager with our test config folder
            manager = GPConfigManager("gpclog_test", cfg_folder=config_dir)

            # Get the logs subfolder as GPConfigFolder
            logs_folder = manager.get_config("logs")

            # Configure gpclog to use this config folder
            gpclog.set_config_folder(logs_folder)

            # Get loggers using gpclog public API
            # These will load configuration from the config folder
            database_logger = gpclog.get_logger("database")
            event_bus_logger = gpclog.get_logger("event_bus")
            ui_logger = gpclog.get_logger("ui")

            # Test database logger (INFO level, output_to_stderr=True)
            database_logger.info("Database connection established")
            database_logger.debug("This debug message should NOT appear")

            # Test event_bus logger (DEBUG level, output_to_stdout=True)
            event_bus_logger.debug("Event bus initialized")
            event_bus_logger.info("Processing event")

            # Test ui logger (WARNING level)
            ui_logger.warning("UI warning message")
            ui_logger.info("This info message should NOT appear")
            ui_logger.error("UI error occurred")

        # Verify log files were created and contain correct content
        db_log_file = log_dir / "gpclog_output" / "database.log"
        assert db_log_file.exists(), "Database log file should exist"
        db_content = db_log_file.read_text(encoding="utf-8")
        assert "Database connection established" in db_content
        assert "This debug message should NOT appear" not in db_content

        event_bus_log_file = log_dir / "gpclog_output" / "event_bus.log"
        assert event_bus_log_file.exists(), "Event bus log file should exist"
        event_bus_content = event_bus_log_file.read_text(encoding="utf-8")
        assert "Event bus initialized" in event_bus_content
        assert "Processing event" in event_bus_content

        ui_log_file = log_dir / "gpclog_output" / "ui.log"
        assert ui_log_file.exists(), "UI log file should exist"
        ui_content = ui_log_file.read_text(encoding="utf-8")
        assert "UI warning message" in ui_content
        assert "UI error occurred" in ui_content
        assert "This info message should NOT appear" not in ui_content

        # Verify log isolation
        assert "Database connection established" not in event_bus_content
        assert "Database connection established" not in ui_content
        assert "Event bus initialized" not in db_content
        assert "Event bus initialized" not in ui_content
        assert "UI warning message" not in db_content
        assert "UI warning message" not in event_bus_content

    def test_sn_logger_writes_to_separate_file(self, tmp_path: Path) -> None:
        """Test that sn loggers write to separate log files."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            logger_base = gpclog.get_logger("worker")
            logger_sn0 = gpclog.get_logger("worker", sn=0)
            logger_sn1 = gpclog.get_logger("worker", sn=1)

            logger_base.info("Message from base worker")
            logger_sn0.info("Message from worker 0")
            logger_sn1.info("Message from worker 1")

        # Each logger writes to its own file
        base_file = tmp_path / "worker.log"
        sn0_file = tmp_path / "worker-0.log"
        sn1_file = tmp_path / "worker-1.log"

        assert base_file.exists()
        assert sn0_file.exists()
        assert sn1_file.exists()

        base_content = base_file.read_text(encoding="utf-8")
        sn0_content = sn0_file.read_text(encoding="utf-8")
        sn1_content = sn1_file.read_text(encoding="utf-8")

        # Base file has only base messages
        assert "Message from base worker" in base_content
        assert "Message from worker 0" not in base_content
        assert "Message from worker 1" not in base_content

        # SN0 file has only sn0 messages
        assert "Message from worker 0" in sn0_content
        assert "Message from base worker" not in sn0_content
        assert "Message from worker 1" not in sn0_content

        # SN1 file has only sn1 messages
        assert "Message from worker 1" in sn1_content
        assert "Message from base worker" not in sn1_content
        assert "Message from worker 0" not in sn1_content

    def test_sn_logger_shows_sn_name_in_log_format(self, tmp_path: Path) -> None:
        """Test that log output shows the hyphenated name with sn."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            logger = gpclog.get_logger("worker", sn=3)
            logger.info("Test message")

        log_file = tmp_path / "worker-3.log"
        content = log_file.read_text(encoding="utf-8")

        # The default file format includes {extra[name]} which should be "worker-3"
        assert "worker-3" in content
        assert "Test message" in content
