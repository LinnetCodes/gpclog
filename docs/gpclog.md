# gpclog Module

The public API entry point for the gpclog package, providing a simple logging management interface.

## Import

```python
import gpclog
```

!!! warning "Important: importing gpclog clears loguru handlers"

    As a **side effect of importing `gpclog`**, the `GPCLoggerManager`
    singleton is constructed, which calls `loguru.logger.remove()`. This
    **clears any pre-existing loguru handlers** that your application (or
    another library) had configured. If you configure loguru handlers
    yourself, do so **after** importing `gpclog`, or call
    `loguru.logger.add(...)` again afterwards. See also the
    [`reset()`](#reset) notes below — `reset()` performs the same removal.

## Exported Members

```python
__all__ = [
    "get_logger",
    "set_config_folder",
    "reset",
    "GPCLogger",
    "GPCLoggerConfig",
]
```

## Functions

### get_logger()

Get or create a logger by name.

This is the primary interface for obtaining loggers. Each unique `logger_name` creates a separate logger with its own configuration and output file.

```python
def get_logger(logger_name: str, sn: Optional[int] = None) -> GPCLogger:
    """Get or create a logger by name."""
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `logger_name` | `str` | Unique name for the logger, used for configuration lookup and (without sn) log file name |
| `sn` | `Optional[int]` | Optional serial number for multiprocess isolation. When provided, the logger is named `{logger_name}-{sn}` and writes to `{logger_name}-{sn}.log`, but still uses the configuration associated with `logger_name` |

**Returns:** `GPCLogger` instance

**Example:**

```python
import gpclog

# Get a logger
db_logger = gpclog.get_logger("database")

# Use the logger
db_logger.info("Connected to database")
db_logger.error("Connection failed")

# Get another logger (separate file)
api_logger = gpclog.get_logger("api")
api_logger.info("API started")

# Multiprocess scenario: use sn to avoid write contention
worker_logger = gpclog.get_logger("worker", sn=process_id)
worker_logger.info("Process started")
```

**Notes:**

- Multiple calls with the same `(logger_name, sn)` return the cached instance
- Without `sn`, log file name is `{logger_name}.log`
- With `sn`, log file name is `{logger_name}-{sn}.log`
- If a config folder is set, it will try to load `{logger_name}.yaml` configuration (unaffected by `sn`)

---

### set_config_folder()

Set the configuration folder for logger configurations.

After calling this function, logger configurations will be loaded from the specified folder. If a logger's configuration is not found, default configuration will be used.

```python
def set_config_folder(cfg_folder: GPConfigFolder) -> None:
    """Set the configuration folder for logger configurations."""
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cfg_folder` | `GPConfigFolder` | Folder containing logger configuration files |

**Example:**

```python
import gpclog
from gpconfig import GPConfigManager

# Initialize GPConfigManager
manager = GPConfigManager("myapp")

# Get the logs config folder
logs_folder = manager.get_config("logs")

# Set gpclog config folder
gpclog.set_config_folder(logs_folder)

# Now configurations will be loaded from the config folder
db_logger = gpclog.get_logger("database")  # Loads logs/database.yaml
api_logger = gpclog.get_logger("api")      # Loads logs/api.yaml
```

**Configuration folder structure example:**

```
myapp/
├── global_env.yaml
└── logs/
    ├── database.yaml
    ├── api.yaml
    └── cache.yaml
```

---

### reset()

Reset the logger manager and clear all caches.

This function is primarily intended for testing purposes to ensure a clean state between tests. It resets the internal state and clears all cached loggers.

```python
def reset() -> None:
    """Reset the logger manager and clear all caches."""
```

**Example:**

```python
import gpclog

# Use in tests
def setup_method():
    gpclog.reset()

def test_something():
    logger = gpclog.get_logger("test")
    logger.info("Test message")
```

**Notes:**

- This function clears all created loggers
- All loguru handlers will be removed (same `loguru_logger.remove()` that runs on import)
- Primarily for testing scenarios, production code typically doesn't need to call this

---

## Complete Usage Examples

### Zero Configuration Quick Start

```python
import gpclog

# No configuration needed, just use it
logger = gpclog.get_logger("myapp")
logger.info("Application started")
# Log output to: ~/gpclog_output/myapp.log
```

### Using Configuration Files

```python
import gpclog
from gpconfig import GPConfigManager

# Initialize GPConfigManager (GPCLoggerConfig and GPCLogger are auto-registered on import)
manager = GPConfigManager("myapp", cfg_folder="/path/to/configs")

# Method 1: Using gpclog public API
logs_folder = manager.get_config("logs")
gpclog.set_config_folder(logs_folder)
logger = gpclog.get_logger("database")

# Method 2: Using GPConfigManager directly
logger = manager.get_object("logs.database")
```

### Multi-Module Project Example

```python
import gpclog

# Different modules use independent loggers
class DatabaseService:
    def __init__(self):
        self.logger = gpclog.get_logger("database")

    def connect(self):
        self.logger.info("Connecting to database")

class APIClient:
    def __init__(self):
        self.logger = gpclog.get_logger("api")

    def request(self):
        self.logger.debug("Sending API request")

class CacheManager:
    def __init__(self):
        self.logger = gpclog.get_logger("cache")

    def get(self, key):
        self.logger.warning(f"Cache miss: {key}")
```

**Output Result:**

- `database.log`: Database-related logs
- `api.log`: API-related logs
- `cache.log`: Cache-related logs

### Multiprocess Scenario Example

In multiprocess environments, use the `sn` parameter to create independent log files per process and avoid write contention:

```python
import os
import gpclog
from multiprocessing import Process

def worker(process_id):
    # Each process uses a unique sn, writing to a separate file
    logger = gpclog.get_logger("worker", sn=process_id)
    logger.info(f"Process {process_id} started")
    # Output to: ~/gpclog_output/worker-{process_id}.log

# Start multiple processes
if __name__ == "__main__":
    processes = [Process(target=worker, args=(i,)) for i in range(4)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

# Result:
# worker-0.log: Process 0 logs
# worker-1.log: Process 1 logs
# worker-2.log: Process 2 logs
# worker-3.log: Process 3 logs
```

All `worker` loggers share the same configuration (e.g., `logs/worker.yaml`), but each writes to its own log file.

## Internal Implementation

gpclog uses singleton pattern to manage all loggers:

```python
# Singleton manager instance
_manager: GPCLoggerManager = GPCLoggerManager()

def get_logger(logger_name: str, sn: Optional[int] = None) -> GPCLogger:
    return _manager.get_logger(logger_name, sn)

def set_config_folder(cfg_folder: GPConfigFolder) -> None:
    _manager.set_config_folder(cfg_folder)

def reset() -> None:
    """Reset the manager and clear caches."""
    global _manager
    GPCLoggerManager._instance = None
    GPCLogger.clear_cache()
    _manager = GPCLoggerManager()
```

This design ensures:
1. Globally unique logger cache
2. Unified configuration management entry point
3. Simplified user interface
4. State can be reset via `reset()` (mainly for testing)
