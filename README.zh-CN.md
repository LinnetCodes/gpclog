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

> **提示（导入副作用）：** 导入 `gpclog` 会构造其单例管理器，其中会调用
> `loguru.logger.remove()`，**清除此前已配置的所有 loguru handlers**。如果你自行
> 配置 loguru，请在导入 `gpclog` *之后* 再进行。

### 基本使用

```python
import gpclog

# 获取一个分类日志器（零配置）
logger = gpclog.get_logger("my_category")
logger.info("Hello, gpclog!")
# 输出到: ~/gpclog_output/my_category.log
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

配置结构、多进程用法、轮转/保留策略以及完整 API 说明请查看 `docs/`。

## 文档

本地构建并校验文档：

```bash
venv/bin/mkdocs build --clean --strict
```

本地预览文档：

```bash
venv/bin/mkdocs serve
```

## API 参考

详见：

- [文档首页](docs/zh/index.md)
- [gpclog 模块](docs/zh/gpclog.md)
- [GPCLogger 类](docs/zh/logger.md)
- [GPCLoggerConfig 类](docs/zh/config.md)

## 许可证

MIT
