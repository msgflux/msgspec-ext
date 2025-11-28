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

## Performance

msgspec-ext leverages msgspec's high-performance serialization with bulk JSON decoding for maximum speed.

**Benchmark Results** (Python 3.12):

| Scenario | msgspec-ext | pydantic-settings | Advantage |
|----------|-------------|-------------------|-----------|
| Cold start (first load) | 1.709ms | 1.945ms | 1.1x faster |
| Warm (cached) | 0.037ms | 1.501ms | **40.6x faster** ⚡ |
| Average (1000 iterations) | 0.074ms | 6.582ms | **89x faster** |

**Key insight**: pydantic-settings re-parses .env on every load, while msgspec-ext caches it. This provides 40x advantage on subsequent loads.

**Key optimizations:**
- **Cached .env file loading** - Parse once, reuse forever
- Bulk JSON decoding in C (via msgspec)
- Cached encoders and decoders
- Automatic field ordering
- Zero Python loops for validation

*Benchmark measures complete settings initialization with complex configuration (app settings, database, redis, feature flags) including .env file parsing and type validation. Run `./benchmark/run_benchmark.sh` to reproduce.*

## Why msgspec-ext?

- **Performance** - 89x faster than pydantic-settings
- **Lightweight** - 4x smaller package size (0.49 MB vs 1.95 MB)
- **Type safety** - Full type validation with modern Python type checkers
- **Minimal dependencies** - Only msgspec and python-dotenv

## Comparison with Pydantic Settings

| Feature | msgspec-ext | Pydantic Settings |
|---------|------------|-------------------|
| .env support | ✅ | ✅ |
| Type validation | ✅ | ✅ |
| Performance | **89x faster** ⚡ | Baseline |
| Package size | 0.49 MB | 1.95 MB |
| Nested config | ✅ | ✅ |
| Field aliases | ✅ | ✅ |
| JSON Schema | ✅ | ✅ |
| Secret masking | ⚠️ Planned | ✅ |
| Dependencies | Minimal (2) | More (5+) |

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [GitHub Repository](https://github.com/msgflux/msgspec-ext)
- [PyPI Package](https://pypi.org/project/msgspec-ext/)
- [msgspec Documentation](https://jcristharif.com/msgspec/)
