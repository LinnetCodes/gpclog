"""Tests for utility functions."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from gpclog.utils import resolve_log_path


class TestResolveLogPath:
    """Test resolve_log_path function."""

    def test_auto_mode_with_env_variable(self, tmp_path: Path) -> None:
        """Test auto mode uses GPCLOG_PATH environment variable."""
        env_path = tmp_path / "custom_logs"
        env_path.mkdir()

        with patch.dict(os.environ, {"GPCLOG_PATH": str(env_path)}):
            result = resolve_log_path("auto")
            # Should create gpclog_output subfolder
            assert result == env_path / "gpclog_output"

    def test_auto_mode_without_env_variable(self, tmp_path: Path) -> None:
        """Test auto mode falls back to home directory."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("gpclog.utils.Path.home", return_value=tmp_path):
                result = resolve_log_path("auto")
                assert result == tmp_path / "gpclog_output"

    def test_auto_mode_creates_gpclog_output_subfolder(self, tmp_path: Path) -> None:
        """Test that gpclog_output subfolder is created if parent is not named gpclog_output."""
        with patch.dict(os.environ, {"GPCLOG_PATH": str(tmp_path)}):
            result = resolve_log_path("auto")
            assert result.name == "gpclog_output"
            assert result.exists()

    def test_auto_mode_no_subfolder_if_already_gpclog_output(
        self, tmp_path: Path
    ) -> None:
        """Test that no subfolder is created if path is already gpclog_output."""
        gpclog_path = tmp_path / "gpclog_output"
        gpclog_path.mkdir()

        with patch.dict(os.environ, {"GPCLOG_PATH": str(gpclog_path)}):
            result = resolve_log_path("auto")
            assert result == gpclog_path

    def test_absolute_path(self, tmp_path: Path) -> None:
        """Test with absolute path."""
        result = resolve_log_path(str(tmp_path))
        assert result == tmp_path / "gpclog_output"

    def test_home_mode(self, tmp_path: Path) -> None:
        """Test home mode uses user home directory."""
        with patch("gpclog.utils.Path.home", return_value=tmp_path):
            result = resolve_log_path("home")
            assert result == tmp_path / "gpclog_output"

    def test_env_mode_with_env_variable(self, tmp_path: Path) -> None:
        """Test env mode uses GPCLOG_PATH."""
        with patch.dict(os.environ, {"GPCLOG_PATH": str(tmp_path)}):
            result = resolve_log_path("env")
            assert result == tmp_path / "gpclog_output"

    def test_env_mode_without_env_variable_raises_error(self) -> None:
        """Test env mode raises error if GPCLOG_PATH not set."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GPCLOG_PATH"):
                resolve_log_path("env")

    def test_nonexistent_path_raises_error(self, tmp_path: Path) -> None:
        """Test that an absolute, nonexistent path raises 'does not exist'."""
        # Use a tmp_path-derived path so it's genuinely absolute on every OS
        # (a leading "/" alone is not absolute on Windows — there's no drive).
        nonexistent = tmp_path / "nope" / "deep"
        with pytest.raises(ValueError, match="does not exist"):
            resolve_log_path(str(nonexistent))

    def test_cwd_mode(self, tmp_path: Path, monkeypatch) -> None:
        """cwd mode creates gpclog_output under the current working directory."""
        monkeypatch.chdir(tmp_path)
        result = resolve_log_path("cwd")
        assert result == tmp_path / "gpclog_output"
        assert result.exists()

    def test_relative_path_rejected(self) -> None:
        """Relative paths are rejected; use cwd mode or an absolute path."""
        with pytest.raises(ValueError, match="absolute path"):
            resolve_log_path("some/relative/dir")

    def test_absolute_nonexistent_rejected(self, tmp_path: Path) -> None:
        """An absolute path that doesn't exist is rejected with 'does not exist'."""
        nonexistent = tmp_path / "nope" / "deep"
        with pytest.raises(ValueError, match="does not exist"):
            resolve_log_path(str(nonexistent))

    def test_file_path_raises_error(self, tmp_path: Path) -> None:
        """Test that file path (not directory) raises error."""
        file_path = tmp_path / "file.txt"
        file_path.touch()

        with pytest.raises(ValueError, match="not a directory"):
            resolve_log_path(str(file_path))
