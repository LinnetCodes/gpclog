# GPCLoggerConfig 类

`GPCLoggerConfig` 是日志配置类，继承自 `gpconfig.GPConfig`，提供类型安全的配置管理。

## 导入

```python
from gpclog import GPCLoggerConfig
```

## 类定义

```python
class GPCLoggerConfig(GPConfig):
    """GPCLogger 的配置类。"""

    cfg_class_name: ClassVar[str] = "GPCLoggerConfig"
    configured_class_name: str = "GPCLogger"
```

## 类级变量

### cfg_class_name

用于 gpconfig 自动检测配置类的标识符。在 YAML 文件中设置此值可以自动关联配置类。

```python
cfg_class_name: ClassVar[str] = "GPCLoggerConfig"
```

### configured_class_name

与此配置类关联的可配置对象类的名称。用于 `GPConfigManager.get_object()` 方法。

```python
configured_class_name: str = "GPCLogger"
```

**YAML 配置示例：**

```yaml
cfg_class_name: "GPCLoggerConfig"
configured_class_name: "GPCLogger"
level: DEBUG
```

## 配置字段

### 核心字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `level` | `str` | `"INFO"` | 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL |

### 格式配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `file_format` | `str` | 见下方 | 文件日志格式字符串 |
| `console_format` | `str` | 见下方 | 控制台日志格式字符串 |

**默认 file_format：**

```
{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[name]} | {message}
```

**默认 console_format：**

```
<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{extra[name]}</cyan> | <level>{message}</level>
```

### 输出目标配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `output_to_stdout` | `bool` | `True` | 是否输出到标准输出 |
| `output_to_stderr` | `bool` | `False` | 是否输出到标准错误 |
| `output_to_file` | `bool` | `True` | 是否输出到文件 |

### 路径配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `log_path` | `str` | `"auto"` | 日志路径：auto, env, home，或已存在的绝对目录 |

### 轮转配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `rotation_enabled` | `bool` | `False` | 是否启用日志轮转 |
| `rotation_size` | `str` | `"10 MB"` | 轮转大小阈值 |

### 保留配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `retention_enabled` | `bool` | `False` | 是否启用日志过期删除 |
| `retention_days` | `int` | `7` | 日志保留天数 |

## 使用示例

### 基本配置

```python
from gpclog.config import GPCLoggerConfig
from gpclog.logger import GPCLogger

# 创建配置（所有字段都有默认值）
config = GPCLoggerConfig(name="myapp")

# 创建 logger
logger = GPCLogger(config)
```

### 自定义日志级别

```python
from gpclog.config import GPCLoggerConfig

# DEBUG 级别 - 记录所有消息
debug_config = GPCLoggerConfig(
    name="development",
    level="DEBUG",
)

# WARNING 级别 - 只记录警告及以上
prod_config = GPCLoggerConfig(
    name="production",
    level="WARNING",
)
```

### 自定义输出目标

```python
from gpclog.config import GPCLoggerConfig

# 只输出到文件
file_only = GPCLoggerConfig(
    name="background",
    output_to_stdout=False,
    output_to_stderr=False,
    output_to_file=True,
)

# 只输出到控制台
console_only = GPCLoggerConfig(
    name="cli",
    output_to_stdout=True,
    output_to_stderr=False,
    output_to_file=False,
)

# 同时输出到 stderr 和文件
mixed_output = GPCLoggerConfig(
    name="service",
    output_to_stdout=False,
    output_to_stderr=True,
    output_to_file=True,
)
```

### 配置日志轮转

```python
from gpclog.config import GPCLoggerConfig

config = GPCLoggerConfig(
    name="app",
    rotation_enabled=True,
    rotation_size="50 MB",      # 文件达到 50MB 时轮转
    retention_enabled=True,
    retention_days=30,          # 保留 30 天
)
```

**支持的轮转大小格式：**

- `"500 KB"` - 500 KB
- `"10 MB"` - 10 MB
- `"1 GB"` - 1 GB

### 自定义日志路径

```python
from gpclog.config import GPCLoggerConfig

# 使用自动检测（推荐）
config = GPCLoggerConfig(name="app", log_path="auto")

# 使用环境变量 GPCLOG_PATH
config = GPCLoggerConfig(name="app", log_path="env")

# 使用用户主目录
config = GPCLoggerConfig(name="app", log_path="home")

# 使用已存在的绝对父目录
config = GPCLoggerConfig(name="app", log_path="/var/log/myapp")
```

`log_path` 指向的目录必须已经存在。除非目录名本身就是 `gpclog_output`，否则 gpclog 会在其下创建并使用 `gpclog_output` 子目录。

### 自定义日志格式

```python
from gpclog.config import GPCLoggerConfig

config = GPCLoggerConfig(
    name="custom",
    file_format="{time} | {level} | {message}",
    console_format="<level>{level}</level>: {message}",
)
```

**可用的格式化变量：**

| 变量 | 说明 |
|------|------|
| `{time}` | 时间戳 |
| `{level}` | 日志级别 |
| `{message}` | 日志消息 |
| `{extra[name]}` | Logger 名称 |
| `{file}` | 源文件名 |
| `{line}` | 行号 |
| `{function}` | 函数名 |

## 与 gpconfig 集成

### 自动类注册

导入 `gpclog` 包时，`GPCLoggerConfig` 和 `GPCLogger` 会自动注册到 `GPConfigManager`：

```python
import gpclog  # 自动注册 GPCLoggerConfig 和 GPCLogger
from gpconfig import GPConfigManager

# 无需手动注册，直接使用
manager = GPConfigManager("myapp")
logger = manager.get_object("logs.database")
```

### 从 YAML 文件加载

**配置文件结构：**

```
myapp/
├── global_env.yaml
└── logs/
    ├── database.yaml
    └── api.yaml
```

**database.yaml：**

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

**代码加载：**

```python
import gpclog  # 自动注册 GPCLoggerConfig 和 GPCLogger
from gpconfig import GPConfigManager

# 初始化管理器
manager = GPConfigManager("myapp")

# 方式 1：获取配置对象
config = manager.get_config("logs.database", GPCLoggerConfig)
logger = GPCLogger(config)

# 方式 2：直接创建对象（推荐）
logger = manager.get_object("logs.database")
```

## 类型验证

`GPCLoggerConfig` 继承自基于 Pydantic 的 gpconfig 类，因此字段类型会被校验。但当前项目不会在配置对象创建阶段校验 `level` 的取值是否合法。

```python
from gpclog.config import GPCLoggerConfig

config = GPCLoggerConfig(
    name="app",
    level="DEBUG",
    rotation_size="10 MB",
)

# 这里会校验字段类型，但不会限制 level 名称。
config = GPCLoggerConfig(name="app", level="INVALID_LEVEL")
assert config.level == "INVALID_LEVEL"
```

## 保存配置

```python
from gpconfig import GPConfigManager
from gpclog.config import GPCLoggerConfig

# 获取配置
manager = GPConfigManager("myapp")
config = manager.get_config("logs.database", GPCLoggerConfig)

# 修改配置
config.level = "DEBUG"
config.rotation_enabled = True

# 保存回文件
config.save()
```

## 完整配置示例

### 开发环境配置

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

### 生产环境配置

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
