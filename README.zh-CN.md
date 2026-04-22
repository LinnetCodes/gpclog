# gpclog

简体中文 | [English](README.md)

General Purpose Category Logger - 用于在复杂 Python 项目里管理分类日志。

## 特性

- **分类日志管理** - 每个日志类别独立配置、独立文件
- **基于 loguru** - 高性能、功能丰富的日志核心
- **基于 gpconfig** - 类型安全的配置管理
- **智能默认配置** - 零配置即可使用
- **自动类注册** - 导入即自动注册到 GPConfigManager

## 安装

```bash
pip install gpclog
```

## 快速开始

### 基本使用

```python
import gpclog

# 获取一个分类日志器（零配置）
logger = gpclog.get_logger("my_category")
logger.info("Hello, gpclog!")
# 输出到: ~/gpclog_output/my_category.log
```

### 多模块项目

```python
import gpclog

# 每个模块使用独立的 logger
db_logger = gpclog.get_logger("database")
api_logger = gpclog.get_logger("api")
cache_logger = gpclog.get_logger("cache")

# 各 logger 输出到独立文件
db_logger.info("Connected to database")   # -> database.log
api_logger.info("API request received")   # -> api.log
cache_logger.warning("Cache miss")        # -> cache.log
```

### 使用配置文件

```python
import gpclog
from gpconfig import GPConfigManager

# 初始化 GPConfigManager（GPCLoggerConfig 和 GPCLogger 已自动注册）
manager = GPConfigManager("myapp")

# 方式 1：使用 gpclog 公共 API
logs_folder = manager.get_config("logs")
gpclog.set_config_folder(logs_folder)
logger = gpclog.get_logger("database")

# 方式 2：使用 GPConfigManager 直接创建
logger = manager.get_object("logs.database")
```

**配置文件示例 (logs/database.yaml)：**

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

## 日志级别

```python
logger = gpclog.get_logger("myapp")

logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告")
logger.error("错误")
logger.critical("严重错误")
```

## API 参考

详细用法请参阅 [API 文档](docs/api/cn/index.md)。

## 许可证

MIT
