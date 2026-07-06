# gpclog API 文档

gpclog (General Purpose Category Logger) 是一个基于 loguru 的 Python 日志管理库，专为复杂项目设计。它提供分类日志管理功能，支持基于 gpconfig 框架的灵活配置。

## 安装

```bash
pip install gpclog
```

## 核心组件

| 组件 | 说明 |
|------|------|
| [`get_logger()`](gpclog.md#get_logger) | 获取或创建日志记录器的主要接口 |
| [`set_config_folder()`](gpclog.md#set_config_folder) | 设置配置文件夹 |
| [`GPCLogger`](logger.md) | 可配置的日志记录器类 |
| [`GPCLoggerConfig`](config.md) | 日志配置类 |

## 依赖

```
gpclog
  ├── loguru >= 0.7.0    # 日志核心
  └── gpconfig           # 配置管理
```

## 快速开始

### 1. 基本使用（零配置）

```python
import gpclog

# 获取 logger，使用默认配置
db_logger = gpclog.get_logger("database")
db_logger.info("Database connected")
# 输出到: ~/gpclog_output/database.log

api_logger = gpclog.get_logger("api")
api_logger.warning("Rate limit at 80%")
# 输出到: ~/gpclog_output/api.log
```

### 2. 使用配置文件夹

```python
import gpclog
from gpconfig import GPConfigManager

# 初始化 GPConfigManager
manager = GPConfigManager("myapp")

# 获取 logs 子文件夹
logs_folder = manager.get_config("logs")

# 配置 gpclog 使用此配置文件夹
gpclog.set_config_folder(logs_folder)

# 现在会从配置文件夹加载配置
db_logger = gpclog.get_logger("database")
```

### 3. 日志级别

```python
logger = gpclog.get_logger("myapp")

logger.debug("Debug message")      # 调试信息
logger.info("Info message")        # 一般信息
logger.warning("Warning message")  # 警告
logger.error("Error message")      # 错误
logger.critical("Critical message") # 严重错误
```

## 典型用例

### 多模块项目的分类日志

在复杂项目中，不同模块通常需要独立的日志文件：

```python
import gpclog

# 每个模块使用独立的 logger
db_logger = gpclog.get_logger("database")
api_logger = gpclog.get_logger("api")
cache_logger = gpclog.get_logger("cache")

# 各 logger 输出到独立文件
db_logger.info("Connected to PostgreSQL")      # -> database.log
api_logger.info("API request received")        # -> api.log
cache_logger.warning("Cache miss for key")     # -> cache.log
```

### 使用配置文件管理日志设置

创建配置文件夹结构：

```
myapp/
├── global_env.yaml
└── logs/
    ├── database.yaml
    ├── api.yaml
    └── cache.yaml
```

**database.yaml 配置示例：**

```yaml
cfg_class_name: "GPCLoggerConfig"
configured_class_name: "GPCLogger"

level: DEBUG

output_to_stdout: true
output_to_stderr: false
output_to_file: true

log_dir: auto

rotation_enabled: true
rotation_size: "50 MB"

retention_enabled: true
retention_days: 30
```

**代码使用：**

```python
import gpclog
from gpconfig import GPConfigManager

# 初始化管理器（GPCLoggerConfig 和 GPCLogger 在导入 gpclog 时已自动注册）
manager = GPConfigManager("myapp")

# 方式 1：使用 gpclog 公共 API
logs_folder = manager.get_config("logs")
gpclog.set_config_folder(logs_folder)
db_logger = gpclog.get_logger("database")

# 方式 2：使用 GPConfigManager 直接创建对象
db_logger = manager.get_object("logs.database")
```

### 多进程日志隔离

在多进程场景中，使用 `sn` 参数为每个进程创建独立的日志文件，避免写入竞争：

```python
import gpclog
from multiprocessing import Process

def worker(pid):
    # 每个进程使用独立的 sn，写入独立文件
    logger = gpclog.get_logger("worker", sn=pid)
    logger.info(f"Process {pid} started")

processes = [Process(target=worker, args=(i,)) for i in range(4)]
for p in processes:
    p.start()
for p in processes:
    p.join()
```

所有 `worker` logger 共享同一份配置，但各自写入独立的日志文件：
- `worker-0.log`、`worker-1.log`、`worker-2.log`、`worker-3.log`

### 日志轮转和保留

```python
import gpclog
from gpclog.config import GPCLoggerConfig
from gpclog.logger import GPCLogger

# 创建带轮转配置的 logger
config = GPCLoggerConfig(
    name="app",
    level="INFO",
    output_to_file=True,
    output_to_stdout=True,
    rotation_enabled=True,
    rotation_size="10 MB",      # 文件达到 10MB 时轮转
    retention_enabled=True,
    retention_days=7,           # 保留 7 天的日志
)

logger = GPCLogger(config)
logger.info("Application started")
```

### 自定义日志格式

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

## 日志路径配置

### 路径类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `auto` | 自动检测（推荐） | `auto` |
| `env` | 使用 GPCLOG_PATH 环境变量 | `env` |
| `home` | 用户主目录 | `home` |
| 绝对路径 | 已存在的目录路径 | `/var/log/myapp` |

### auto 模式解析流程

1. 检查 `GPCLOG_PATH` 环境变量
2. 如果存在且有效，使用该路径
3. 否则使用用户主目录
4. 最终在指定目录下创建 `gpclog_output` 子文件夹

对于绝对路径，目录本身必须已经存在。如果目录名不是 `gpclog_output`，gpclog 实际会写入 `<path>/gpclog_output/`。

### 使用环境变量

```bash
# 设置日志输出路径
export GPCLOG_PATH=/var/log/myapp
```

```python
import gpclog

# 配置文件中使用 log_dir: env
# 或者直接使用 auto 模式
logger = gpclog.get_logger("myapp")
# 日志将输出到 /var/log/myapp/gpclog_output/myapp.log
```

## 默认配置

gpclog 提供内置默认配置，无需任何配置即可使用：

```yaml
cfg_class_name: "GPCLoggerConfig"
configured_class_name: "GPCLogger"
level: "INFO"

file_format: "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[name]} | {message}"
console_format: "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{extra[name]}</cyan> | <level>{message}</level>"

output_to_stdout: true
output_to_stderr: false
output_to_file: true

log_dir: "auto"

rotation_enabled: false
rotation_size: "10 MB"

retention_enabled: false
retention_days: 7
```

## 与 gpconfig 集成

gpclog 与 gpconfig 深度集成，支持类型安全的配置管理。

### 自动类注册

导入 `gpclog` 包时，`GPCLoggerConfig` 和 `GPCLogger` 会自动注册到 `GPConfigManager`，无需手动注册：

```python
import gpclog  # 自动注册 GPCLoggerConfig 和 GPCLogger
from gpconfig import GPConfigManager

# 直接使用，无需手动注册
manager = GPConfigManager("myapp")
logger = manager.get_object("logs.database")
```

### 配置类继承

`GPCLoggerConfig` 继承自 `gpconfig.GPConfig`，`GPCLogger` 继承自 `gpconfig.GPConfigurable`。

### YAML 配置文件要求

配置文件需要包含 `cfg_class_name` 和 `configured_class_name` 字段：

```yaml
cfg_class_name: "GPCLoggerConfig"    # 必须
configured_class_name: "GPCLogger"   # 用于 get_object() 方法
level: INFO
output_to_file: true
```

## API 参考

- [gpclog 模块](gpclog.md) - 公共 API 函数
- [GPCLogger 类](logger.md) - 日志记录器类
- [GPCLoggerConfig 类](config.md) - 配置类
