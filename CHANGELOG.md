# Changelog

All notable changes to **gpclog** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.3.0] - 2026-07-07

**Development status raised to Beta** (`Development Status :: 4 - Beta`).

> 本版本以一次代码审查（`dev_docs/reviews/code_review-2026-06-28.md`）为主线，
> 修复了路径穿越、未校验输入、错误的异常捕获等安全性与健壮性问题，并对 API 做了一处
> **破坏性重命名**。请阅读下方的 **Breaking Changes**。

### ⚠️ Breaking Changes

- **`log_path` field renamed to `log_dir`** (`GPCLoggerConfig`, `config.py`).
  The old name was misleading — this is a *directory*, not a file. Existing YAML
  configs and any code referencing `config.log_path` must be updated to `log_dir`.
  (`d802227`)
  - **`log_path` 字段重命名为 `log_dir`**。旧字段名（"路径"）容易让人误以为是文件，
    实际上它指向一个目录。请把现有 YAML 配置和引用 `config.log_path` 的代码改为 `log_dir`。

- **Stricter validation now raises on invalid input where it previously silently
  passed.** The following now raise `ValueError` / `ValidationError` (see
  *Security* and *Added*):
  - `level` not in `{DEBUG, INFO, WARNING, ERROR, CRITICAL}`
  - `rotation_size` not matching `<number> <KB|MB|GB>`
  - `retention_days < 0`, or `retention_days <= 0` when `retention_enabled`
  - `logger_name` containing characters outside `[A-Za-z0-9_.-]`, empty, or
    consisting purely of punctuation (`..`, `---`, `___`, …)
  - `log_dir` supplied as a *relative* path in the else-branch of
    `resolve_log_path` (use the new `"cwd"` mode instead)

### Added

- **`validate_logger_name()`** (`utils.py`): enforces a strict
  `[A-Za-z0-9_.-]` whitelist on logger names and rejects pure-punctuation names.
  This closes the **path-traversal** vector reported in the code review:
  `logger_name` is used to build file paths (`log_dir / f"{name}.log"`), so a
  value like `../` previously allowed writing outside the intended directory.
  The check now runs at every entry point — `gpclog.get_logger()`,
  `GPCLoggerManager.get_logger()` (before the cache lookup), and the
  `GPCLogger` constructor. (`36d0676`, `9a03d74`, `4c1606b`)
- **New `"cwd"` mode** for `resolve_log_path()` / `log_dir`: resolves to the
  current working directory. This replaces the previous (ambiguous and unsafe)
  practice of passing a relative path. (`36d0676`)
- **Field validators on `GPCLoggerConfig`** (`config.py`, fail-early per the
  project's design principles):
  - `level` must be one of the recognized uppercase log levels.
  - `rotation_size` must match `<number> <KB|MB|GB>` (case-insensitive).
  - `retention_days` must be `>= 0`, and `> 0` when `retention_enabled` is
    `True` (a `0` would delete logs immediately).
  (`d802227`)
- **MkDocs documentation stack** added to the `[dev]` extra:
  `mkdocs>=1.6`, `mkdocs-material>=9.5`, `mkdocs-static-i18n>=1.2`
  (the latter powers the EN/ZH bilingual docs). (`6672627`)
- `set_config_folder()` now **eagerly loads `default.yaml`** (if present) as
  the fallback default config, rather than lazily on first miss. (`9a03d74`)
- New test module `tests/test_edge_cases.py` pinning the validator and `sn`
  boundary behavior. (`630e0fe`)
- Docstring notes: documented the **import side effect** (importing `gpclog`
  clears pre-existing loguru handlers) in the README, and the
  **`reset()` invalidates prior logger references** caveat + the
  **non-thread-safe `_bound_loggers` cache** warning on `GPCLogger`. (`1f50f83`)

### Changed

- **`GPCLoggerConfig.__init__` config-copying is consolidated.** Three
  triplicated hand-written copy blocks (`_get_config`, the `sn` override, and
  `_merge_with_defaults`) are replaced by `config.model_copy(update={...})`.
  (`9a03d74`)
- **`GPCLoggerManager._get_config` now catches only `ConfigNotFoundError`**
  instead of a broad `except Exception`. Genuine config *parse/validation*
  errors now propagate (fail-early) instead of being swallowed and silently
  falling back to defaults. (`9a03d74`)
- **`resolve_log_path()` no longer `print()`s to stdout** on the `home`
  fallback. A library must not hijack stdout, so this now uses `warnings.warn`
  (and points the user at the `gpclog_output` subdir). (`36d0676`)
- The else-branch of `resolve_log_path()` **rejects relative paths** with a
  `ValueError` that points the user at the `"cwd"` mode. (`36d0676`)
- `GPCLoggerConfig.VALID_LEVELS` exposed as a `ClassVar` set. (`d802227`)
- README/ZH-README `mkdocs` commands normalized from `venv/bin/mkdocs ...` to
  bare `mkdocs ...` (tool-/platform-agnostic, consistent with `AGENTS.md`).
  (`1f50f83`)

### Removed

- **`GPCLoggerManager._merge_with_defaults()`** deleted. It mixed `is not None`
  and truthiness checks inconsistently, and its job is now covered by pydantic
  field defaults + `model_copy`. (`9a03d74`)

### Fixed

- **Path-traversal via `logger_name`** — see *Added / `validate_logger_name`*.
- **Inconsistent validation ordering**: `validate_logger_name` now runs *before*
  the cache check in `GPCLoggerManager.get_logger`, matching the public
  `gpclog.get_logger` entry point. (`4c1606b`)
- **Documentation inaccuracies** (`1f50f83`), cross-checked against source in
  `dev_docs/reviews/docs_review-2026-07-07.md` and `readme_review-2026-07-07.md`:
  - the `cwd` mode was missing from the Log Path Configuration tables;
  - the `name` field's auto-assignment from the YAML filename was undocumented;
  - misleading "except for cwd/home/auto" existence-check wording;
  - multiprocessing examples lacked a `if __name__ == "__main__":` guard
    (required for Windows `spawn`);
  - the `auto`-mode env-var resolution was mischaracterized.

### Internal / Infrastructure

- `__version__` bumped `0.2.0` → `0.3.0`; PyPI `Development Status` classifier
  raised from `3 - Alpha` to `4 - Beta`. (`4c1606b`)
- `GPCLoggerManager` deliberately kept out of `__all__` (documented contract:
  internal, but reachable from tests). (`9a03d74`)

---

## [0.2.0] - 2026-07-05

Initial PyPI release. Category-based logging on top of **loguru** +
**gpconfig** (`GPConfig` / `GPConfigManager` / `GPConfigurable`): per-category
config and log files, `sn`-based multiprocess isolation, rotation/retention,
and `resolve_log_path()` resolving `"auto"` / `"env"` / `"home"` / absolute
paths.

---

[0.3.0]: https://github.com/LinnetCodes/gpclog/compare/version-0.2.0r1...version-0.3.0
[0.2.0]: https://github.com/LinnetCodes/gpclog/releases/tag/version-0.2.0r1
