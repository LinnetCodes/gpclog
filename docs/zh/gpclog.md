# gpclog 模块

gpclog 包的公共 API 入口，提供简洁的日志管理接口。

## 导入

```python
import gpclog
```

!!! warning "重要：导入 gpclog 会清除 loguru 的 handlers"

    作为**导入 `gpclog` 的副作用**，会构造 `GPCLoggerManager` 单例，其中会调用
    `loguru.logger.remove()`。这会**清除此前应用（或其他库）已配置的所有 loguru
    handlers**。如果你自行配置了 loguru handlers，请在**导入 `gpclog` 之后**再配置，
    或之后再次调用 `loguru.logger.add(...)`。另见下方的 [`reset()`](#reset) 说明——
    `reset()` 会执行相同的清除操作。

## 导出成员

```python
__all__ = [
    "get_logger",
    "set_config_folder",
    "reset",
    "GPCLogger",
    "GPCLoggerConfig",
]
```

## 函数

### get_logger()

获取或创建指定名称的日志记录器。

这是获取日志记录器的主要接口。每个唯一的 `logger_name` 会创建独立的日志记录器，拥有自己的配置和输出文件。

```python
def get_logger(logger_name: str, sn: Optional[int] = None) -> GPCLogger:
    """获取或创建指定名称的日志记录器。"""
```

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `logger_name` | `str` | 日志记录器的唯一名称，用于配置查找和（不指定 sn 时）日志文件名 |
| `sn` | `Optional[int]` | 可选序列号，用于多进程隔离。指定后 logger 名称为 `{logger_name}-{sn}`，写入独立的 `{logger_name}-{sn}.log` 文件，但仍使用 `logger_name` 对应的配置 |

**返回值：** `GPCLogger` 实例

**示例：**

```python
import gpclog

# 获取 logger
db_logger = gpclog.get_logger("database")

# 使用 logger
db_logger.info("Connected to database")
db_logger.error("Connection failed")

# 获取另一个 logger（独立文件）
api_logger = gpclog.get_logger("api")
api_logger.info("API started")

# 多进程场景：使用 sn 参数避免写入竞争
worker_logger = gpclog.get_logger("worker", sn=process_id)
worker_logger.info("Process started")
```

**注意事项：**

- 相同 `(logger_name, sn)` 组合多次调用返回缓存的同一实例
- 不指定 `sn` 时，日志文件名为 `{logger_name}.log`
- 指定 `sn` 时，日志文件名为 `{logger_name}-{sn}.log`
- 如果设置了配置文件夹，会尝试加载 `{logger_name}.yaml` 配置（不受 `sn` 影响）

---

### set_config_folder()

设置日志配置文件夹。

调用此函数后，日志配置将从指定的文件夹加载。如果找不到特定日志记录器的配置，将使用默认配置。

```python
def set_config_folder(cfg_folder: GPConfigFolder) -> None:
    """设置日志配置文件夹。"""
```

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `cfg_folder` | `GPConfigFolder` | 包含日志配置文件的文件夹 |

**示例：**

```python
import gpclog
from gpconfig import GPConfigManager

# 初始化 GPConfigManager
manager = GPConfigManager("myapp")

# 获取日志配置文件夹
logs_folder = manager.get_config("logs")

# 设置 gpclog 配置文件夹
gpclog.set_config_folder(logs_folder)

# 现在会从配置文件夹加载配置
db_logger = gpclog.get_logger("database")  # 加载 logs/database.yaml
api_logger = gpclog.get_logger("api")      # 加载 logs/api.yaml
```

**配置文件夹结构示例：**

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

重置日志管理器并清除所有缓存。

此函数主要用于测试场景，确保测试之间有干净的状态。它会重置内部状态并清除所有已缓存的日志记录器。

```python
def reset() -> None:
    """重置日志管理器并清除所有缓存。"""
```

**示例：**

```python
import gpclog

# 在测试中使用
def setup_method():
    gpclog.reset()

def test_something():
    logger = gpclog.get_logger("test")
    logger.info("Test message")
```

**注意事项：**

- 此函数会清除所有已创建的日志记录器
- 所有 loguru handlers 会被移除（与导入时执行的 `loguru_logger.remove()` 相同）
- 主要用于测试场景，生产代码通常不需要调用

---

## 完整使用示例

### 零配置快速开始

```python
import gpclog

# 无需任何配置，直接使用
logger = gpclog.get_logger("myapp")
logger.info("Application started")
# 日志输出到: ~/gpclog_output/myapp.log
```

### 使用配置文件

```python
import gpclog
from gpconfig import GPConfigManager

# 初始化 GPConfigManager（GPCLoggerConfig 和 GPCLogger 在导入时已自动注册）
manager = GPConfigManager("myapp", cfg_folder="/path/to/configs")

# 方式一：使用 gpclog 公共 API
logs_folder = manager.get_config("logs")
gpclog.set_config_folder(logs_folder)
logger = gpclog.get_logger("database")

# 方式二：使用 GPConfigManager 直接创建
logger = manager.get_object("logs.database")
```

### 多模块项目示例

```python
import gpclog

# 不同模块使用独立的 logger
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

**输出结果：**

- `database.log`: 数据库相关日志
- `api.log`: API 相关日志
- `cache.log`: 缓存相关日志

### 多进程场景示例

在多进程环境中，使用 `sn` 参数为每个进程创建独立的日志文件，避免写入竞争：

```python
import os
import gpclog
from multiprocessing import Process

def worker(process_id):
    # 每个进程使用独立的 sn，写入独立文件
    logger = gpclog.get_logger("worker", sn=process_id)
    logger.info(f"Process {process_id} started")
    # 输出到: ~/gpclog_output/worker-{process_id}.log

# 启动多个进程
if __name__ == "__main__":
    processes = [Process(target=worker, args=(i,)) for i in range(4)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

# 结果：
# worker-0.log: 进程 0 的日志
# worker-1.log: 进程 1 的日志
# worker-2.log: 进程 2 的日志
# worker-3.log: 进程 3 的日志
```

所有 `worker` logger 共享同一份配置（如 `logs/worker.yaml`），但各自写入独立的日志文件。

## 内部实现

gpclog 使用单例模式管理所有日志记录器：

```python
# 单例管理器实例
_manager: GPCLoggerManager = GPCLoggerManager()

def get_logger(logger_name: str, sn: Optional[int] = None) -> GPCLogger:
    return _manager.get_logger(logger_name, sn)

def set_config_folder(cfg_folder: GPConfigFolder) -> None:
    _manager.set_config_folder(cfg_folder)

def reset() -> None:
    """重置管理器和清除缓存。"""
    global _manager
    GPCLoggerManager._instance = None
    GPCLogger.clear_cache()
    _manager = GPCLoggerManager()
```

这种设计确保：
1. 全局唯一的日志记录器缓存
2. 统一的配置管理入口
3. 简化的用户接口
4. 可通过 `reset()` 重置状态（主要用于测试）
