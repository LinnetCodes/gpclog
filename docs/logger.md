# GPCLogger Class

`GPCLogger` is a configurable logger class that inherits from `gpconfig.GPConfigurable` and wraps loguru to provide logging functionality.

## Import

```python
from gpclog import GPCLogger
```

## Class Definition

```python
class GPCLogger(GPConfigurable):
    """A configurable logger that wraps loguru."""

    def __init__(self, config: GPCLoggerConfig) -> None:
        """Initialize the logger with configuration."""
```

## Initialization

### Constructor Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `config` | `GPCLoggerConfig` | Configuration instance containing logger settings |

### Example

```python
from gpclog import GPCLogger
from gpclog.config import GPCLoggerConfig

# Create configuration
config = GPCLoggerConfig(
    name="myapp",
    level="DEBUG",
    output_to_file=True,
    output_to_stdout=True,
)

# Create logger
logger = GPCLogger(config)
logger.info("Logger initialized")
```

## Properties

### name

Get the logger name.

```python
@property
def name(self) -> str:
    """Get the logger name."""
```

**Example:**

```python
logger = GPCLogger(config)
print(logger.name)  # "myapp"
```

## Logging Methods

### debug()

Log a debug level message.

```python
def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
    """Log a debug message."""
```

### info()

Log an info level message.

```python
def info(self, message: str, *args: Any, **kwargs: Any) -> None:
    """Log an info message."""
```

### warning()

Log a warning level message.

```python
def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
    """Log a warning message."""
```

### error()

Log an error level message.

```python
def error(self, message: str, *args: Any, **kwargs: Any) -> None:
    """Log an error message."""
```

### critical()

Log a critical level message.

```python
def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
    """Log a critical message."""
```

## Usage Examples

### Basic Usage

```python
from gpclog import GPCLogger
from gpclog.config import GPCLoggerConfig

# Create logger with default configuration
config = GPCLoggerConfig(name="app")
logger = GPCLogger(config)

# Log different level messages
logger.debug("Debug message for development")
logger.info("Normal information")
logger.warning("Something might be wrong")
logger.error("An error occurred")
logger.critical("Critical system failure")
```

### Custom Configuration

```python
from gpclog import GPCLogger
from gpclog.config import GPCLoggerConfig

# Create custom configuration
config = GPCLoggerConfig(
    name="production",
    level="WARNING",           # Only WARNING and above
    output_to_stdout=False,    # No console output
    output_to_file=True,       # Output to file
    log_path="/var/log/app",   # Custom log path
    rotation_enabled=True,
    rotation_size="50 MB",
    retention_enabled=True,
    retention_days=30,
)

logger = GPCLogger(config)
logger.warning("This will be logged")
logger.info("This will NOT be logged (below WARNING level)")
```

### Creating from GPConfigManager

```python
import gpclog
from gpconfig import GPConfigManager

# Initialize manager (GPCLoggerConfig and GPCLogger are auto-registered on import)
manager = GPConfigManager("myapp")

# Create logger from config file
logger = manager.get_object("logs.database")

# Use the logger
logger.info("Database connected")
```

**Configuration file (logs/database.yaml):**

```yaml
cfg_class_name: "GPCLoggerConfig"
configured_class_name: "GPCLogger"
level: DEBUG
output_to_file: true
output_to_stdout: true
log_path: auto
```

### Multiple Loggers Coexistence

gpclog supports multiple independent logger instances working simultaneously, each writing to separate files:

```python
from gpclog import GPCLogger
from gpclog.config import GPCLoggerConfig

# Create multiple loggers
db_config = GPCLoggerConfig(name="database", level="DEBUG")
api_config = GPCLoggerConfig(name="api", level="INFO")

db_logger = GPCLogger(db_config)
api_logger = GPCLogger(api_config)

# Each logger outputs to a separate file
db_logger.info("Database message")  # -> database.log
api_logger.info("API message")      # -> api.log
```

### Using Format Strings

```python
logger = GPCLogger(config)

# Using positional arguments
logger.info("User {} logged in from {}", "alice", "192.168.1.1")

# Using keyword arguments
logger.info("Processing order {order_id}", order_id="12345")
```

### Logging Exception Information

```python
logger = GPCLogger(config)

try:
    result = risky_operation()
except Exception as e:
    logger.error("Operation failed: {}", str(e))
    logger.critical("Critical error occurred")
```

## Relationship with GPConfigurable

`GPCLogger` inherits from `gpconfig.GPConfigurable`, you can access the original configuration via the `config` property:

```python
from gpclog import GPCLogger

class MyService:
    def __init__(self, logger: GPCLogger):
        self.logger = logger

    def process(self):
        # Access logger's configuration
        level = self.logger.config.level
        self.logger.info(f"Processing with log level: {level}")
```

## Log Format Description

### Default File Format

```
2024-03-20 14:30:45 | INFO     | database | Connection established
2024-03-20 14:30:46 | WARNING  | api      | Rate limit approaching
```

### Default Console Format (with colors)

- Timestamp: Green
- Log level: Colored by level
  - DEBUG: Cyan
  - INFO: Green
  - WARNING: Yellow
  - ERROR: Red
  - CRITICAL: Bold Red
- Logger name: Cyan
- Message: Colored by level

## Notes

### Log Level Filtering

Only messages at or above the configured level will be logged:

```python
config = GPCLoggerConfig(name="app", level="WARNING")
logger = GPCLogger(config)

logger.debug("Hidden")    # Will not log
logger.info("Hidden")     # Will not log
logger.warning("Shown")   # Will log
logger.error("Shown")     # Will log
```

### Configuration Caching

Loggers obtained via `gpclog.get_logger()` are cached, using `(logger_name, sn)` tuple as the cache key:

```python
import gpclog

logger1 = gpclog.get_logger("myapp")
logger2 = gpclog.get_logger("myapp")

print(logger1 is logger2)  # True - same instance

# Different sn values produce independent cached instances
logger_sn1 = gpclog.get_logger("myapp", sn=1)
logger_sn2 = gpclog.get_logger("myapp", sn=2)

print(logger1 is logger_sn1)  # False - independent instances
```

### Handler Isolation

Each GPCLogger instance uses loguru's filter mechanism for message isolation, ensuring messages from different loggers are written to the correct files.

### Logger Cache Mechanism

`GPCLogger` uses a class-level cache internally to prevent duplicate handler creation for loggers with the same name:

```python
# When creating loggers with the same name via GPConfigManager, handlers won't be duplicated
from gpconfig import GPConfigManager

manager = GPConfigManager("myapp")
logger1 = manager.get_object("logs.database")
logger2 = manager.get_object("logs.database")

# logger1 and logger2 use the same internal loguru bound logger
# No duplicate handlers are added
```

To clear the cache (mainly for testing), you can call the class method:

```python
from gpclog import GPCLogger

GPCLogger.clear_cache()
```

Or use the public API:

```python
import gpclog

gpclog.reset()  # Resets all state, including logger cache
```
