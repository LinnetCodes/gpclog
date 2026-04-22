# GPCLoggerConfig Class

`GPCLoggerConfig` is the logger configuration class that inherits from `gpconfig.GPConfig`, providing type-safe configuration management.

## Import

```python
from gpclog import GPCLoggerConfig
```

## Class Definition

```python
class GPCLoggerConfig(GPConfig):
    """Configuration class for GPCLogger."""

    cfg_class_name: ClassVar[str] = "GPCLoggerConfig"
    configured_class_name: str = "GPCLogger"
```

## Class Variables

### cfg_class_name

Identifier for gpconfig auto-detection of configuration classes. Setting this value in YAML files allows automatic association with the configuration class.

```python
cfg_class_name: ClassVar[str] = "GPCLoggerConfig"
```

### configured_class_name

Name of the configurable class associated with this configuration class. Used by the `GPConfigManager.get_object()` method.

```python
configured_class_name: str = "GPCLogger"
```

**YAML configuration example:**

```yaml
cfg_class_name: "GPCLoggerConfig"
configured_class_name: "GPCLogger"
level: DEBUG
```

## Configuration Fields

### Core Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL |

### Format Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `file_format` | `str` | See below | File log format string |
| `console_format` | `str` | See below | Console log format string |

**Default file_format:**

```
{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[name]} | {message}
```

**Default console_format:**

```
<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{extra[name]}</cyan> | <level>{message}</level>
```

### Output Target Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `output_to_stdout` | `bool` | `True` | Whether to output to stdout |
| `output_to_stderr` | `bool` | `False` | Whether to output to stderr |
| `output_to_file` | `bool` | `True` | Whether to output to file |

### Path Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `log_path` | `str` | `"auto"` | Log path: auto, env, home, or an existing absolute directory |

### Rotation Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `rotation_enabled` | `bool` | `False` | Whether to enable log rotation |
| `rotation_size` | `str` | `"10 MB"` | Rotation size threshold |

### Retention Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `retention_enabled` | `bool` | `False` | Whether to enable log retention/deletion |
| `retention_days` | `int` | `7` | Number of days to retain logs |

## Usage Examples

### Basic Configuration

```python
from gpclog.config import GPCLoggerConfig
from gpclog.logger import GPCLogger

# Create configuration (all fields have defaults)
config = GPCLoggerConfig(name="myapp")

# Create logger
logger = GPCLogger(config)
```

### Custom Log Level

```python
from gpclog.config import GPCLoggerConfig

# DEBUG level - log all messages
debug_config = GPCLoggerConfig(
    name="development",
    level="DEBUG",
)

# WARNING level - only warnings and above
prod_config = GPCLoggerConfig(
    name="production",
    level="WARNING",
)
```

### Custom Output Targets

```python
from gpclog.config import GPCLoggerConfig

# File output only
file_only = GPCLoggerConfig(
    name="background",
    output_to_stdout=False,
    output_to_stderr=False,
    output_to_file=True,
)

# Console output only
console_only = GPCLoggerConfig(
    name="cli",
    output_to_stdout=True,
    output_to_stderr=False,
    output_to_file=False,
)

# Output to both stderr and file
mixed_output = GPCLoggerConfig(
    name="service",
    output_to_stdout=False,
    output_to_stderr=True,
    output_to_file=True,
)
```

### Configuring Log Rotation

```python
from gpclog.config import GPCLoggerConfig

config = GPCLoggerConfig(
    name="app",
    rotation_enabled=True,
    rotation_size="50 MB",      # Rotate when file reaches 50MB
    retention_enabled=True,
    retention_days=30,          # Keep for 30 days
)
```

**Supported rotation size formats:**

- `"500 KB"` - 500 KB
- `"10 MB"` - 10 MB
- `"1 GB"` - 1 GB

### Custom Log Path

```python
from gpclog.config import GPCLoggerConfig

# Use auto-detect (recommended)
config = GPCLoggerConfig(name="app", log_path="auto")

# Use GPCLOG_PATH environment variable
config = GPCLoggerConfig(name="app", log_path="env")

# Use user home directory
config = GPCLoggerConfig(name="app", log_path="home")

# Use an existing absolute parent directory
config = GPCLoggerConfig(name="app", log_path="/var/log/myapp")
```

The directory passed in `log_path` must already exist. Unless the directory name is already `gpclog_output`, gpclog creates and uses a `gpclog_output` subdirectory inside it.

### Custom Log Format

```python
from gpclog.config import GPCLoggerConfig

config = GPCLoggerConfig(
    name="custom",
    file_format="{time} | {level} | {message}",
    console_format="<level>{level}</level>: {message}",
)
```

**Available format variables:**

| Variable | Description |
|----------|-------------|
| `{time}` | Timestamp |
| `{level}` | Log level |
| `{message}` | Log message |
| `{extra[name]}` | Logger name |
| `{file}` | Source file name |
| `{line}` | Line number |
| `{function}` | Function name |

## Integration with gpconfig

### Auto Class Registration

When importing the `gpclog` package, `GPCLoggerConfig` and `GPCLogger` are automatically registered with `GPConfigManager`:

```python
import gpclog  # Auto-registers GPCLoggerConfig and GPCLogger
from gpconfig import GPConfigManager

# No manual registration needed, just use directly
manager = GPConfigManager("myapp")
logger = manager.get_object("logs.database")
```

### Loading from YAML File

**Configuration file structure:**

```
myapp/
├── global_env.yaml
└── logs/
    ├── database.yaml
    └── api.yaml
```

**database.yaml:**

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

**Loading in code:**

```python
import gpclog  # Auto-registers GPCLoggerConfig and GPCLogger
from gpconfig import GPConfigManager

# Initialize manager
manager = GPConfigManager("myapp")

# Method 1: Get config object
config = manager.get_config("logs.database", gpclog.GPCLoggerConfig)
logger = gpclog.GPCLogger(config)

# Method 2: Create object directly (recommended)
logger = manager.get_object("logs.database")
```

## Type Validation

`GPCLoggerConfig` inherits from Pydantic-based gpconfig classes, so field types are validated. The project does not currently validate the allowed values of `level` at config-construction time.

```python
from gpclog.config import GPCLoggerConfig

config = GPCLoggerConfig(
    name="app",
    level="DEBUG",
    rotation_size="10 MB",
)

# Type validation applies to field shapes, but level names are not restricted here.
config = GPCLoggerConfig(name="app", level="INVALID_LEVEL")
assert config.level == "INVALID_LEVEL"
```

## Saving Configuration

```python
from gpconfig import GPConfigManager
from gpclog.config import GPCLoggerConfig

# Get configuration
manager = GPConfigManager("myapp")
config = manager.get_config("logs.database", GPCLoggerConfig)

# Modify configuration
config.level = "DEBUG"
config.rotation_enabled = True

# Save back to file
config.save()
```

## Complete Configuration Examples

### Development Environment Configuration

```yaml
# logs/development.yaml
cfg_class_name: "GPCLoggerConfig"
configured_class_name: "GPCLogger"
level: DEBUG
output_to_stdout: true
output_to_stderr: false
output_to_file: true
log_path: auto
rotation_enabled: false
retention_enabled: false
```

### Production Environment Configuration

```yaml
# logs/production.yaml
cfg_class_name: "GPCLoggerConfig"
configured_class_name: "GPCLogger"
level: WARNING
output_to_stdout: false
output_to_stderr: true
output_to_file: true
log_path: env
rotation_enabled: true
rotation_size: "100 MB"
retention_enabled: true
retention_days: 30
```
