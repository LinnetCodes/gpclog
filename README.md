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

### Basic Usage

```python
import gpclog

# Get a category logger (zero configuration)
logger = gpclog.get_logger("my_category")
logger.info("Hello, gpclog!")
# Output to: ~/gpclog_output/my_category.log
```

### Multi-Module Project

```python
import gpclog

# Each module uses its own logger
db_logger = gpclog.get_logger("database")
api_logger = gpclog.get_logger("api")
cache_logger = gpclog.get_logger("cache")

# Each logger outputs to a separate file
db_logger.info("Connected to database")   # -> database.log
api_logger.info("API request received")   # -> api.log
cache_logger.warning("Cache miss")        # -> cache.log
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

**Configuration file example (logs/database.yaml):**

```yaml
cfg_class_name: "GPCLoggerConfig"
configured_class_name: "GPCLogger"
level: DEBUG
output_to_stdout: true
output_to_file: true
log_path: auto
rotation_enabled: true
rotation_size: "50 MB"
retention_enabled: true
retention_days: 30
```

## Log Levels

```python
logger = gpclog.get_logger("myapp")

logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning")
logger.error("Error")
logger.critical("Critical error")
```

## API Reference

See the [API documentation](docs/api/en/index.md) for detailed usage.

## License

MIT
