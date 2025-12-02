<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/msgflux/msgspec-ext/main/docs/assets/msgspec-ext-logo-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/msgflux/msgspec-ext/main/docs/assets/msgspec-ext-logo-light.png">
    <img alt="msgspec-ext" src="https://raw.githubusercontent.com/msgflux/msgspec-ext/main/docs/assets/msgspec-ext-logo-light.png" width="340">
  </picture>
</p>



<p align="center">
  <b>Fast settings management using <a href="https://github.com/jcrist/msgspec">msgspec</a></b> - a high-performance validation and serialization library
</p>

<p align="center">
  <a href="https://github.com/msgflux/msgspec-ext/actions/workflows/ci.yml"><img src="https://github.com/msgflux/msgspec-ext/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/msgspec-ext/"><img src="https://img.shields.io/pypi/v/msgspec-ext.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/msgspec-ext/"><img src="https://img.shields.io/pypi/pyversions/msgspec-ext.svg" alt="Python Versions"></a>
  <a href="https://github.com/msgflux/msgspec-ext/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
</p>

## Features

- ✅ **High performance** - Built on msgspec for speed
- ✅ **Type-safe** - Full type hints and validation
- ✅ **.env support** - Automatic loading from .env files via python-dotenv
- ✅ **Nested settings** - Support for complex configuration structures
- ✅ **Minimal dependencies** - Only msgspec and python-dotenv
- ✅ **Familiar API** - Easy to learn if you've used settings libraries before

## Installation

Using pip:
```bash
pip install msgspec-ext
```

Using uv (recommended):
```bash
uv add msgspec-ext
```

## Quick Start

```python
from msgspec_ext import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",  # Load from .env file
        env_prefix="APP_"  # Prefix for env vars
    )

    # Settings with type validation
    name: str
    debug: bool = False
    port: int = 8000
    timeout: float = 30.0

# Load from environment variables and .env file
settings = AppSettings()

print(settings.name)   # from APP_NAME env var
print(settings.port)   # from APP_PORT env var or default 8000
```

## Environment Variables

By default, msgspec-ext looks for environment variables matching field names (case-insensitive).

**.env file**:
```bash
APP_NAME=my-app
DEBUG=true
PORT=3000
DATABASE__HOST=localhost
DATABASE__PORT=5432
```

**Python code**:
```python
from msgspec_ext import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__"
    )

    app_name: str
    debug: bool = False
    database_host: str = "localhost"
    database_port: int = 5432

settings = AppSettings()
# Automatically loads from .env file and environment variables
```

## Advanced Usage

### Custom .env file path

```python
from msgspec_ext import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.production",
        env_file_encoding="utf-8"
    )

    app_name: str
```

### Prefix for environment variables

```python
from msgspec_ext import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MYAPP_"
    )

    name: str  # Will look for MYAPP_NAME
```

### Case sensitivity

```python
from msgspec_ext import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True
    )

    AppName: str  # Exact match required
```

## Why Choose msgspec-ext?

msgspec-ext provides a **faster, lighter alternative** to pydantic-settings while maintaining a familiar API and full type safety.

### Performance Comparison

**First-time load** (what you'll see when testing):

| Library | Time per load | Speed |
|---------|---------------|-------|
| **msgspec-ext** | **1.818ms** | **1.5x faster** ⚡ |
| pydantic-settings | 2.814ms | Baseline |

**With caching** (repeated loads in long-running applications):

| Library | Time per load | Speed |
|---------|---------------|-------|
| **msgspec-ext** | **0.016ms** | **112x faster** ⚡ |
| pydantic-settings | 1.818ms | Baseline |

> *Benchmark includes .env file parsing, environment variable loading, type validation, and nested configuration (app settings, database, redis, feature flags). Run `benchmark/benchmark_cold_warm.py` to reproduce.*

### Key Advantages

| Feature | msgspec-ext | pydantic-settings |
|---------|------------|-------------------|
| **First load** | **1.5x faster** ⚡ | Baseline |
| **Cached loads** | **112x faster** ⚡ | Baseline |
| **Package size** | **0.49 MB** | 1.95 MB |
| **Dependencies** | **2 (minimal)** | 5+ |
| .env support | ✅ | ✅ |
| Type validation | ✅ | ✅ |
| Advanced caching | ✅ | ❌ |
| Nested config | ✅ | ✅ |
| JSON Schema | ✅ | ✅ |
| Secret masking | ⚠️ Planned | ✅ |

### How is it so fast?

msgspec-ext achieves its performance through:
- **Bulk validation**: Validates all fields at once in C (via msgspec), not one-by-one in Python
- **Smart caching**: Caches .env files, field mappings, and type information - loads after the first are 112x faster
- **Optimized file operations**: Uses fast os.path operations instead of slower pathlib alternatives
- **Zero overhead**: Fast paths for common types (str, bool, int, float) with minimal Python code

This means your application **starts faster** and uses **less memory**, especially important for:
- 🚀 **CLI tools** - 1.5x faster startup every time you run the command
- ⚡ **Serverless functions** - Lower cold start latency means better response times
- 🔄 **Long-running apps** - After the first load, reloading settings is 112x faster (16 microseconds!)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [GitHub Repository](https://github.com/msgflux/msgspec-ext)
- [PyPI Package](https://pypi.org/project/msgspec-ext/)
- [msgspec Documentation](https://jcristharif.com/msgspec/)
