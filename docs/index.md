# gpclog API Documentation

gpclog (General Purpose Category Logger) is a Python logging library based on loguru, designed for complex projects. It provides category-based logging management with flexible configuration through the gpconfig framework.

## Installation

```bash
pip install gpclog
```

## Core Components

| Component | Description |
|-----------|-------------|
| [`get_logger()`](gpclog.md#get_logger) | Primary interface for getting or creating loggers |
| [`set_config_folder()`](gpclog.md#set_config_folder) | Set the configuration folder |
| [`GPCLogger`](logger.md) | Configurable logger class |
| [`GPCLoggerConfig`](config.md) | Logger configuration class |

## Dependencies

```
gpclog
  ├── loguru >= 0.7.0    # Logging core
  └── gpconfig           # Configuration management
```

## Quick Start

### 1. Basic Usage (Zero Configuration)

```python
import gpclog

# Get a logger with default configuration
db_logger = gpclog.get_logger("database")
db_logger.info("Database connected")
# Output to: ~/gpclog_output/database.log

api_logger = gpclog.get_logger("api")
api_logger.warning("Rate limit at 80%")
# Output to: ~/gpclog_output/api.log
```

### 2. Using Configuration Folder

```python
import gpclog
from gpconfig import GPConfigManager

# Initialize GPConfigManager
manager = GPConfigManager("myapp")

# Get the logs subfolder
logs_folder = manager.get_config("logs")

# Configure gpclog to use this config folder
gpclog.set_config_folder(logs_folder)

# Now configurations will be loaded from the config folder
db_logger = gpclog.get_logger("database")
```

### 3. Log Levels

```python
logger = gpclog.get_logger("myapp")

logger.debug("Debug message")      # Debug information
logger.info("Info message")        # General information
logger.warning("Warning message")  # Warning
logger.error("Error message")      # Error
logger.critical("Critical message") # Critical error
```

## Typical Use Cases

### Categorized Logging for Multi-Module Projects

In complex projects, different modules typically need separate log files:

```python
import gpclog

# Each module uses its own logger
db_logger = gpclog.get_logger("database")
api_logger = gpclog.get_logger("api")
cache_logger = gpclog.get_logger("cache")

# Each logger outputs to a separate file
db_logger.info("Connected to PostgreSQL")      # -> database.log
api_logger.info("API request received")        # -> api.log
cache_logger.warning("Cache miss for key")     # -> cache.log
```

### Managing Log Settings with Configuration Files

Create a configuration folder structure:

```
myapp/
├── global_env.yaml
└── logs/
    ├── database.yaml
    ├── api.yaml
    └── cache.yaml
```

**database.yaml configuration example:**

```yaml
cfg_class_name: "GPCLoggerConfig"
configured_class_name: "GPCLogger"

level: DEBUG

output_to_stdout: true
output_to_stderr: false
output_to_file: true

log_path: auto

rotation_enabled: true
rotation_size: "50 MB"

retention_enabled: true
retention_days: 30
```

**Code usage:**

```python
import gpclog
from gpconfig import GPConfigManager

# Initialize manager (GPCLoggerConfig and GPCLogger are auto-registered when importing gpclog)
manager = GPConfigManager("myapp")

# Method 1: Using gpclog public API
logs_folder = manager.get_config("logs")
gpclog.set_config_folder(logs_folder)
db_logger = gpclog.get_logger("database")

# Method 2: Using GPConfigManager to create objects directly
db_logger = manager.get_object("logs.database")
```

### Multiprocess Log Isolation

In multiprocess scenarios, use the `sn` parameter to create independent log files per process and avoid write contention:

```python
import gpclog
from multiprocessing import Process

def worker(pid):
    # Each process uses a unique sn, writing to a separate file
    logger = gpclog.get_logger("worker", sn=pid)
    logger.info(f"Process {pid} started")

processes = [Process(target=worker, args=(i,)) for i in range(4)]
for p in processes:
    p.start()
for p in processes:
    p.join()
```

All `worker` loggers share the same configuration, but each writes to its own log file:
- `worker-0.log`, `worker-1.log`, `worker-2.log`, `worker-3.log`

### Log Rotation and Retention

```python
import gpclog
from gpclog.config import GPCLoggerConfig
from gpclog.logger import GPCLogger

# Create a logger with rotation configuration
config = GPCLoggerConfig(
    name="app",
    level="INFO",
    output_to_file=True,
    output_to_stdout=True,
    rotation_enabled=True,
    rotation_size="10 MB",      # Rotate when file reaches 10MB
    retention_enabled=True,
    retention_days=7,           # Keep logs for 7 days
)

logger = GPCLogger(config)
logger.info("Application started")
```

### Custom Log Format

```python
from gpclog.config import GPCLoggerConfig
from gpclog.logger import GPCLogger

config = GPCLoggerConfig(
    name="custom",
    level="DEBUG",
    file_format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[name]} | {message}",
    console_format="<level>{level: <8}</level> | <cyan>{extra[name]}</cyan> | {message}",
)

logger = GPCLogger(config)
```

## Log Path Configuration

### Path Types

| Type | Description | Example |
|------|-------------|---------|
| `auto` | Auto-detect (recommended) | `auto` |
| `env` | Use GPCLOG_PATH environment variable | `env` |
| `home` | User home directory | `home` |
| Absolute path | Specify exact path | `/var/log/myapp` |

### Auto Mode Resolution

1. Check `GPCLOG_PATH` environment variable
2. If exists and valid, use that path
3. Otherwise, use user home directory
4. Create `gpclog_output` subfolder in the specified directory

### Using Environment Variables

```bash
# Set log output path
export GPCLOG_PATH=/var/log/myapp
```

```python
import gpclog

# Use log_path: env in config file
# Or use auto mode directly
logger = gpclog.get_logger("myapp")
# Logs will output to /var/log/myapp/gpclog_output/myapp.log
```

## Default Configuration

gpclog provides built-in default configuration, usable without any setup:

```yaml
cfg_class_name: "GPCLoggerConfig"
configured_class_name: "GPCLogger"
level: "INFO"

file_format: "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[name]} | {message}"
console_format: "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{extra[name]}</cyan> | <level>{message}</level>"

output_to_stdout: true
output_to_stderr: false
output_to_file: true

log_path: "auto"

rotation_enabled: false
rotation_size: "10 MB"

retention_enabled: false
retention_days: 7
```

## Integration with gpconfig

gpclog integrates deeply with gpconfig, supporting type-safe configuration management.

### Auto Class Registration

When importing the `gpclog` package, `GPCLoggerConfig` and `GPCLogger` are automatically registered with `GPConfigManager` - no manual registration needed:

```python
import gpclog  # Auto-registers GPCLoggerConfig and GPCLogger
from gpconfig import GPConfigManager

# Use directly without manual registration
manager = GPConfigManager("myapp")
logger = manager.get_object("logs.database")
```

### Configuration Class Inheritance

`GPCLoggerConfig` inherits from `gpconfig.GPConfig`, and `GPCLogger` inherits from `gpconfig.GPConfigurable`.

### YAML Configuration File Requirements

Configuration files need to include `cfg_class_name` and `configured_class_name` fields:

```yaml
cfg_class_name: "GPCLoggerConfig"    # Required
configured_class_name: "GPCLogger"   # For get_object() method
level: INFO
output_to_file: true
```

## API Reference

- [gpclog Module](gpclog.md) - Public API functions
- [GPCLogger Class](logger.md) - Logger class
- [GPCLoggerConfig Class](config.md) - Configuration class
