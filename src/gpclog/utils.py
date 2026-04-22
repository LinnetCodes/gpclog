"""Utility functions for gpclog."""

import os
from pathlib import Path


def resolve_log_path(log_path: str) -> Path:
    """Resolve the log output path.

    Args:
        log_path: Path specification. Can be:
            - "auto": Auto-detect (GPCLOG_PATH env or home directory)
            - "env": Use GPCLOG_PATH environment variable
            - "home": Use user home directory
            - Absolute path: Use specified path

    Returns:
        Resolved Path object pointing to the log output directory.

    Raises:
        ValueError: If path is invalid or cannot be resolved.
    """
    base_path: Path

    if log_path == "auto":
        # Try GPCLOG_PATH first, then fall back to home
        env_path = os.environ.get("GPCLOG_PATH")
        if env_path:
            base_path = Path(env_path)
        else:
            base_path = Path.home()
            # Print message to user
            print(
                f"gpclog: Using home directory for logs: {base_path / 'gpclog_output'}"
            )
    elif log_path == "env":
        env_path = os.environ.get("GPCLOG_PATH")
        if not env_path:
            raise ValueError("GPCLOG_PATH environment variable is not set")
        base_path = Path(env_path)
    elif log_path == "home":
        base_path = Path.home()
    else:
        # Treat as absolute path
        base_path = Path(log_path)

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
