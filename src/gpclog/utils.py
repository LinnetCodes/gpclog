"""Utility functions for gpclog."""

import os
import re
import warnings
from pathlib import Path

_LOGGER_NAME_PATTERN = re.compile(r"[A-Za-z0-9_.-]+")


def validate_logger_name(name: str) -> str:
    """Validate a logger name against a strict whitelist.

    Only the characters ``[A-Za-z0-9_.-]`` are permitted, and the entire
    string must match. This exists to prevent path-traversal: ``logger_name``
    is used to build file paths (e.g. ``log_dir / f"{name}.log"``), so values
    such as ``../`` or ``/`` would write outside the intended directory.

    Args:
        name: The logger name to validate.

    Returns:
        The validated ``name``, unchanged.

    Raises:
        ValueError: If ``name`` is empty or contains characters outside the
            whitelist.
    """
    if not isinstance(name, str):
        raise ValueError(f"logger name must be a string (got {name!r})")
    if not name or _LOGGER_NAME_PATTERN.fullmatch(name) is None:
        raise ValueError(
            f"invalid logger name {name!r}: only the characters "
            "'[A-Za-z0-9_.-]' are permitted"
        )
    return name


def resolve_log_path(log_path: str) -> Path:
    """Resolve the log output path.

    Args:
        log_path: Path specification. Can be:
            - "auto": Auto-detect (GPCLOG_PATH env or home directory)
            - "env": Use GPCLOG_PATH environment variable
            - "home": Use user home directory
            - "cwd": Use the current working directory
            - Absolute path: Use the specified existing absolute directory.
              Relative paths are rejected; use the "cwd" mode if you want
              current-working-directory output.

    Returns:
        Resolved Path object pointing to the log output directory.

    Raises:
        ValueError: If path is invalid, relative (in the else branch), or
            cannot be resolved.
    """
    base_path: Path

    if log_path == "auto":
        # Try GPCLOG_PATH first, then fall back to home
        env_path = os.environ.get("GPCLOG_PATH")
        if env_path:
            base_path = Path(env_path)
        else:
            base_path = Path.home()
            # Warn the user (a library must not print to stdout)
            warnings.warn(
                f"gpclog: Using home directory for logs: {base_path / 'gpclog_output'}",
                stacklevel=2,
            )
    elif log_path == "env":
        env_path = os.environ.get("GPCLOG_PATH")
        if not env_path:
            raise ValueError("GPCLOG_PATH environment variable is not set")
        base_path = Path(env_path)
    elif log_path == "home":
        base_path = Path.home()
    elif log_path == "cwd":
        base_path = Path.cwd()
    else:
        # Treat as a user-supplied directory.
        # Reject relative paths to avoid ambiguity; point to "cwd" mode instead.
        path = Path(log_path)
        if not path.is_absolute():
            raise ValueError(
                f"log_dir must be an absolute path (got {log_path!r}); "
                "use 'cwd' mode for current-working-directory output"
            )
        base_path = path

    # Validate path exists and is a directory
    if not base_path.exists():
        raise ValueError(f"Log path does not exist: {base_path}")
    if not base_path.is_dir():
        raise ValueError(f"Log path is not a directory: {base_path}")

    # Check if already named gpclog_output
    if base_path.name == "gpclog_output":
        return base_path

    # Create gpclog_output subfolder
    final_path = base_path / "gpclog_output"
    final_path.mkdir(exist_ok=True)
    return final_path
