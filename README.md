# gpclog

[简体中文](README.zh-CN.md) | English

General Purpose Category Logger - A Python library for managing categorized logs in complex projects.

## Features

- **Category-based Logging** - Each category has its own configuration and file
- **Built on loguru** - High-performance, feature-rich logging core
- **Built on gpconfig** - Type-safe configuration management
- **Smart Defaults** - Works out of the box with zero configuration
- **Auto Class Registration** - Automatically registers with GPConfigManager on import

## Installation

```bash
pip install gpclog
```

## Quick Start

> **Note (import side effect):** importing `gpclog` constructs its singleton
> manager, which calls `loguru.logger.remove()` and **clears any pre-existing
> loguru handlers**. If you configure loguru yourself, do so *after* importing
> `gpclog`.

### Basic Usage

```python
import gpclog

# Get a category logger (zero configuration)
logger = gpclog.get_logger("my_category")
logger.info("Hello, gpclog!")
# Output to: ~/gpclog_output/my_category.log
```

### Using Configuration Files

```python
import gpclog
from gpconfig import GPConfigManager

# Initialize GPConfigManager (GPCLoggerConfig and GPCLogger are auto-registered)
manager = GPConfigManager("myapp")

# Method 1: Using gpclog public API
logs_folder = manager.get_config("logs")
gpclog.set_config_folder(logs_folder)
logger = gpclog.get_logger("database")

# Method 2: Using GPConfigManager directly
logger = manager.get_object("logs.database")
```

Configuration schema, multiprocess usage, rotation/retention, and API details are documented in `docs/`.

## Documentation

Build and validate the documentation locally:

```bash
mkdocs build --clean --strict
```

Preview the documentation locally:

```bash
mkdocs serve
```

## API Reference

See:

- [Docs home](docs/index.md)
- [gpclog module](docs/gpclog.md)
- [GPCLogger](docs/logger.md)
- [GPCLoggerConfig](docs/config.md)

## License

MIT
