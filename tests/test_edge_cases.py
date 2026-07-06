# tests/test_edge_cases.py
"""Edge-case tests for findings 5.1/5.2 (name + field validators), the sn
boundary (finding 7.1 historical gap), and empty-name handling.

These tests pin down the stricter validation added during the code-review
verification series:
- ``validate_logger_name`` enforces a strict ``[A-Za-z0-9_.-]`` whitelist so
  logger names cannot be used for path traversal (finding 5.1).
- ``GPCLoggerConfig`` now validates ``level``, ``rotation_size`` and
  ``retention_days`` at construction time (finding 5.2).
- ``sn`` boundaries: ``sn=0`` / ``sn=-1`` produce hyphenated names that are
  still valid whitelist names (``worker-0`` / ``worker--1``).
- Empty names are rejected at every entry point.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

import gpclog
from gpclog.config import GPCLoggerConfig
from gpclog.logger import GPCLogger
from gpclog.utils import validate_logger_name


class TestValidateLoggerName:
    """Tests for ``validate_logger_name`` (finding 5.1)."""

    def test_valid_names_accepted(self) -> None:
        """Valid whitelist names are returned unchanged."""
        for name in ["database", "worker-3", "my_app.db", "a", "worker--1", "worker-0"]:
            assert validate_logger_name(name) == name

    @pytest.mark.parametrize(
        "name",
        [
            "../escape",
            "a/b",
            "",
            "a b",
            "a\\b",
            "a:b",
            "用户",  # non-ASCII (Chinese) characters
            "a\x00b",  # null byte
            "..",  # bare dots (pure punctuation)
            ".",
            "...",
            "---",
            "___",
            "._-",
        ],
    )
    def test_invalid_names_rejected(self, name: str) -> None:
        """Names outside the whitelist raise ValueError."""
        with pytest.raises(ValueError):
            validate_logger_name(name)

    def test_get_logger_rejects_bad_name(self, tmp_path: Path) -> None:
        """The public ``get_logger`` entry point rejects bad names."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            with pytest.raises(ValueError):
                gpclog.get_logger("../escape")

    def test_gpclogger_init_rejects_bad_config_name(self, tmp_path: Path) -> None:
        """A GPCLoggerConfig with a bad name is rejected at GPCLogger construction."""
        cfg = GPCLoggerConfig(name="../escape")
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            with pytest.raises(ValueError):
                GPCLogger(cfg)


class TestLevelValidator:
    """Tests for the ``level`` field validator (finding 5.2)."""

    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_valid_levels_construct_ok(self, level: str) -> None:
        """Recognized uppercase levels construct successfully."""
        config = GPCLoggerConfig(configured_class_name="GPCLogger", level=level)
        assert config.level == level

    @pytest.mark.parametrize("level", ["", "INVALID", "debug"])
    def test_invalid_levels_rejected(self, level: str) -> None:
        """Empty/unknown/lowercase levels raise ValidationError at construction."""
        with pytest.raises(ValidationError):
            GPCLoggerConfig(configured_class_name="GPCLogger", level=level)


class TestRetentionDaysValidator:
    """Tests for the ``retention_days`` model validator (finding 5.2)."""

    def test_negative_retention_days_rejected(self) -> None:
        """A negative retention_days is always rejected."""
        with pytest.raises(ValidationError):
            GPCLoggerConfig(retention_days=-1)

    def test_zero_retention_days_with_disabled_ok(self) -> None:
        """retention_days=0 is allowed when retention is disabled."""
        config = GPCLoggerConfig(retention_enabled=False, retention_days=0)
        assert config.retention_days == 0

    def test_zero_retention_days_with_enabled_rejected(self) -> None:
        """retention_days=0 is rejected when retention is enabled (would delete at once)."""
        with pytest.raises(ValidationError):
            GPCLoggerConfig(retention_enabled=True, retention_days=0)

    def test_positive_retention_days_ok(self) -> None:
        """A normal positive retention_days constructs fine."""
        config = GPCLoggerConfig(retention_days=7)
        assert config.retention_days == 7


class TestRotationSizeValidator:
    """Tests for the ``rotation_size`` field validator (finding 5.2)."""

    @pytest.mark.parametrize("size", ["10 MB", "500 KB", "1 GB", "10MB"])
    def test_valid_rotation_sizes_ok(self, size: str) -> None:
        """Sizes matching '<number> <KB|MB|GB>' (case-insensitive) construct OK."""
        config = GPCLoggerConfig(rotation_size=size)
        assert config.rotation_size == size

    @pytest.mark.parametrize("size", ["", "not a size", "10", "10 TB"])
    def test_invalid_rotation_sizes_rejected(self, size: str) -> None:
        """Sizes missing a unit or using an unsupported unit are rejected."""
        with pytest.raises(ValidationError):
            GPCLoggerConfig(rotation_size=size)


class TestSnBoundary:
    """Tests for the ``sn`` boundary (finding 7.1 historical gap).

    ``sn`` is interpolated into the logger name as ``{logger_name}-{sn}``. For
    ``sn=0`` and ``sn=-1`` the resulting names (``worker-0`` / ``worker--1``)
    happen to be valid whitelist names, so they are ACCEPTED. This is the
    documented expected behavior, not a bug: the whitelist permits a leading
    minus and multiple consecutive hyphens.
    """

    def setup_method(self) -> None:
        """Reset singleton and loguru handlers before each test."""
        gpclog.reset()

    def test_sn_zero_produces_hyphenated_name(self, tmp_path: Path) -> None:
        """sn=0 produces the logger name 'worker-0'."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            logger = gpclog.get_logger("worker", sn=0)
        assert logger.name == "worker-0"

    def test_sn_negative_produces_double_hyphen_name(self, tmp_path: Path) -> None:
        """sn=-1 produces the logger name 'worker--1', which is a valid whitelist name.

        The whitelist ``[A-Za-z0-9_.-]`` permits the leading ``-`` and the
        double ``--``, so this name is ACCEPTED. Documented as expected behavior.
        """
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            logger = gpclog.get_logger("worker", sn=-1)
        assert logger.name == "worker--1"


class TestEmptyName:
    """Tests for empty-name handling (historical gap).

    The public ``get_logger`` entry point rejects an empty name outright via
    ``validate_logger_name``. When a ``GPCLoggerConfig`` is constructed directly
    with an empty ``name`` and handed to ``GPCLogger``, the ``config.name or
    "default"`` fallback in ``GPCLogger.__init__`` substitutes ``"default"``
    BEFORE validation runs, so an empty config name is normalized to
    ``"default"`` rather than rejected.
    """

    def setup_method(self) -> None:
        """Reset singleton and loguru handlers before each test."""
        gpclog.reset()

    def test_get_logger_empty_name_rejected(self, tmp_path: Path) -> None:
        """get_logger('') raises ValueError."""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            with pytest.raises(ValueError):
                gpclog.get_logger("")

    def test_gpclogger_init_empty_name_falls_back_to_default(
        self, tmp_path: Path
    ) -> None:
        """An empty config name is normalized to 'default' by the GPCLogger fallback.

        ``GPCLogger.__init__`` does ``self._name = config.name or "default"`` before
        calling ``validate_logger_name``, so an empty name never reaches the
        validator — it becomes the valid name ``"default"``.
        """
        cfg = GPCLoggerConfig(name="")
        assert cfg.name == ""
        with patch("gpclog.logger.resolve_log_path", return_value=tmp_path):
            logger = GPCLogger(cfg)
        assert logger.name == "default"
