# GPCLogger 类

`GPCLogger` 是可配置的日志记录器类，继承自 `gpconfig.GPConfigurable`，封装 loguru 提供日志功能。

## 导入

```python
from gpclog import GPCLogger
```

## 类定义

```python
class GPCLogger(GPConfigurable):
    """可配置的日志记录器，封装 loguru。"""

    def __init__(self, config: GPCLoggerConfig) -> None:
        """使用配置初始化日志记录器。"""
```

## 初始化

### 构造函数参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `config` | `GPCLoggerConfig` | 包含日志设置的配置实例 |

### 示例

```python
from gpclog import GPCLogger
from gpclog.config import GPCLoggerConfig

# 创建配置
config = GPCLoggerConfig(
    name="myapp",
    level="DEBUG",
    output_to_file=True,
    output_to_stdout=True,
)

# 创建 logger
logger = GPCLogger(config)
logger.info("Logger initialized")
```

## 属性

### name

获取日志记录器名称。

```python
@property
def name(self) -> str:
    """获取日志记录器名称。"""
```

**示例：**

```python
logger = GPCLogger(config)
print(logger.name)  # "myapp"
```

## 日志方法

### debug()

记录调试级别消息。

```python
def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
    """记录调试消息。"""
```

### info()

记录信息级别消息。

```python
def info(self, message: str, *args: Any, **kwargs: Any) -> None:
    """记录信息消息。"""
```

### warning()

记录警告级别消息。

```python
def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
    """记录警告消息。"""
```

### error()

记录错误级别消息。

```python
def error(self, message: str, *args: Any, **kwargs: Any) -> None:
    """记录错误消息。"""
```

### critical()

记录严重错误级别消息。

```python
def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
    """记录严重错误消息。"""
```

## 使用示例

### 基本使用

```python
from gpclog import GPCLogger
from gpclog.config import GPCLoggerConfig

# 创建默认配置的 logger
config = GPCLoggerConfig(name="app")
logger = GPCLogger(config)

# 记录不同级别的日志
logger.debug("Debug message for development")
logger.info("Normal information")
logger.warning("Something might be wrong")
logger.error("An error occurred")
logger.critical("Critical system failure")
```

### 自定义配置

```python
from gpclog import GPCLogger
from gpclog.config import GPCLoggerConfig

# 创建自定义配置
config = GPCLoggerConfig(
    name="production",
    level="WARNING",           # 只记录 WARNING 及以上
    output_to_stdout=False,    # 不输出到控制台
    output_to_file=True,       # 输出到文件
    log_dir="/var/log/app",   # 已存在的父目录
    rotation_enabled=True,
    rotation_size="50 MB",
    retention_enabled=True,
    retention_days=30,
)

logger = GPCLogger(config)
logger.warning("This will be logged")
logger.info("This will NOT be logged (below WARNING level)")
```

如果 `log_dir` 目录名本身不是 `gpclog_output`，gpclog 实际会写入该目录下的 `gpclog_output` 子目录。

### 从 GPConfigManager 创建

```python
import gpclog
from gpconfig import GPConfigManager

# 初始化管理器（GPCLoggerConfig 和 GPCLogger 在导入时已自动注册）
manager = GPConfigManager("myapp")

# 从配置文件创建 logger
logger = manager.get_object("logs.database")

# 使用 logger
logger.info("Database connected")
```

**配置文件 (logs/database.yaml)：**

```yaml
cfg_class_name: "GPCLoggerConfig"
configured_class_name: "GPCLogger"
level: DEBUG
output_to_file: true
output_to_stdout: true
log_dir: auto
```

### 多 Logger 共存

gpclog 支持多个独立的 logger 实例同时工作，每个 logger 写入独立的文件：

```python
from gpclog import GPCLogger
from gpclog.config import GPCLoggerConfig

# 创建多个 logger
db_config = GPCLoggerConfig(name="database", level="DEBUG")
api_config = GPCLoggerConfig(name="api", level="INFO")

db_logger = GPCLogger(db_config)
api_logger = GPCLogger(api_config)

# 各 logger 输出到独立文件
db_logger.info("Database message")  # -> database.log
api_logger.info("API message")      # -> api.log
```

### 使用格式化字符串

```python
logger = GPCLogger(config)

# 使用位置参数
logger.info("User {} logged in from {}", "alice", "192.168.1.1")

# 使用关键字参数
logger.info("Processing order {order_id}", order_id="12345")
```

### 记录异常信息

```python
logger = GPCLogger(config)

try:
    result = risky_operation()
except Exception as e:
    logger.error("Operation failed: {}", str(e))
    logger.critical("Critical error occurred")
```

## 与 GPConfigurable 的关系

`GPCLogger` 继承自 `gpconfig.GPConfigurable`，可以通过 `config` 属性访问原始配置：

```python
from gpclog import GPCLogger

class MyService:
    def __init__(self, logger: GPCLogger):
        self.logger = logger

    def process(self):
        # 访问 logger 的配置
        level = self.logger.config.level
        self.logger.info(f"Processing with log level: {level}")
```

## 日志格式说明

### 默认文件格式

```
2024-03-20 14:30:45 | INFO     | database | Connection established
2024-03-20 14:30:46 | WARNING  | api      | Rate limit approaching
```

### 默认控制台格式（带颜色）

- 时间戳：绿色
- 日志级别：根据级别着色
  - DEBUG: 青色
  - INFO: 绿色
  - WARNING: 黄色
  - ERROR: 红色
  - CRITICAL: 红色加粗
- Logger 名称：青色
- 消息：根据级别着色

## 注意事项

### 日志级别过滤

只有大于或等于配置级别的消息会被记录：

```python
config = GPCLoggerConfig(name="app", level="WARNING")
logger = GPCLogger(config)

logger.debug("Hidden")    # 不会记录
logger.info("Hidden")     # 不会记录
logger.warning("Shown")   # 会记录
logger.error("Shown")     # 会记录
```

### 配置缓存

通过 `gpclog.get_logger()` 获取的 logger 会被缓存，缓存键为 `(logger_name, sn)` 元组：

```python
import gpclog

logger1 = gpclog.get_logger("myapp")
logger2 = gpclog.get_logger("myapp")

print(logger1 is logger2)  # True - 同一实例

# 不同的 sn 参数会产生独立的缓存实例
logger_sn1 = gpclog.get_logger("myapp", sn=1)
logger_sn2 = gpclog.get_logger("myapp", sn=2)

print(logger1 is logger_sn1)  # False - 独立实例
```

### Handler 隔离

每个 GPCLogger 实例使用 loguru 的 filter 机制实现消息隔离，确保不同 logger 的消息写入正确的文件。

### Logger 缓存机制

`GPCLogger` 内部使用类级别的缓存来防止重复创建同名 logger 的 handler：

```python
# 直接使用 GPConfigManager 创建同名 logger 时，handler 不会重复添加
from gpconfig import GPConfigManager

manager = GPConfigManager("myapp")
logger1 = manager.get_object("logs.database")
logger2 = manager.get_object("logs.database")

# logger1 和 logger2 内部使用相同的 loguru bound logger
# 不会重复添加 handler
```

如需清除缓存（主要用于测试），可以调用类方法：

```python
from gpclog import GPCLogger

GPCLogger.clear_cache()
```

或者使用公共 API：

```python
import gpclog

gpclog.reset()  # 重置所有状态，包括 logger 缓存
```
