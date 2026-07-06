# tests/test_config.py
"""Tests for GPCLoggerConfig."""

import pytest

from gpclog.config import GPCLoggerConfig


class TestGPCLoggerConfig:
    """Test GPCLoggerConfig class."""

    def test_create_config_with_required_fields(self) -> None:
        """Test creating config with only required fields."""
        config = GPCLoggerConfig(
            configured_class_name="GPCLogger",
            level="INFO",
        )
        assert config.configured_class_name == "GPCLogger"
        assert config.level == "INFO"

    def test_config_has_default_values(self) -> None:
        """Test that optional fields have correct defaults."""
        config = GPCLoggerConfig(
            configured_class_name="GPCLogger",
            level="DEBUG",
        )
        # Check defaults
        assert config.output_to_stdout is True
        assert config.output_to_stderr is False
        assert config.output_to_file is True
        assert config.log_dir == "auto"
        assert config.rotation_enabled is False
        assert config.retention_enabled is False

    def test_config_with_all_fields(self) -> None:
        """Test creating config with all fields specified."""
        config = GPCLoggerConfig(
            configured_class_name="GPCLogger",
            level="WARNING",
            file_format="{time} | {level} | {message}",
            console_format="<level>{message}</level>",
            output_to_stdout=False,
            output_to_stderr=True,
            output_to_file=True,
            log_dir="/var/log/app",
            rotation_enabled=True,
            rotation_size="50 MB",
            retention_enabled=True,
            retention_days=30,
        )
        assert config.log_dir == "/var/log/app"
        assert config.level == "WARNING"
        assert config.rotation_size == "50 MB"
        assert config.retention_days == 30

    def test_cfg_class_name_is_set(self) -> None:
        """Test that cfg_class_name class variable is set."""
        assert GPCLoggerConfig.cfg_class_name == "GPCLoggerConfig"

    def test_invalid_level_raises_error(self) -> None:
        """Test that invalid level is rejected at config-construction time."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            GPCLoggerConfig(configured_class_name="GPCLogger", level="INVALID")
        # Empty string is also rejected.
        with pytest.raises(ValidationError):
            GPCLoggerConfig(configured_class_name="GPCLogger", level="")
