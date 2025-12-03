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

- ✅ **7x faster than pydantic-settings** - High performance built on msgspec
- ✅ **Drop-in API compatibility** - Familiar interface, easy migration from pydantic-settings
- ✅ **Type-safe** - Full type hints and validation
- ✅ **17+ built-in validators** - Email, URLs, numeric constraints, payment cards, paths, and more
- ✅ **.env support** - Fast built-in .env parser (no dependencies)
- ✅ **Nested settings** - Support for complex configuration structures
- ✅ **Zero dependencies** - Only msgspec required
- ✅ **169x faster cached loads** - Smart caching for repeated access

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

### Field Validators

msgspec-ext provides 17+ built-in validator types for common use cases:

#### Numeric Constraints

```python
from msgspec_ext import BaseSettings, PositiveInt, NonNegativeInt

class ServerSettings(BaseSettings):
    port: PositiveInt  # Must be > 0
    max_connections: PositiveInt
    retry_count: NonNegativeInt  # Can be 0
```

**Available numeric types:**
- `PositiveInt`, `NegativeInt`, `NonNegativeInt`, `NonPositiveInt`
- `PositiveFloat`, `NegativeFloat`, `NonNegativeFloat`, `NonPositiveFloat`

#### String Validators

```python
from msgspec_ext import BaseSettings, EmailStr, HttpUrl, SecretStr

class AppSettings(BaseSettings):
    admin_email: EmailStr  # RFC 5321 validation
    api_url: HttpUrl  # HTTP/HTTPS only
    api_key: SecretStr  # Masked in logs/output
```

**Available string types:**
- `EmailStr` - Email validation (RFC 5321)
- `HttpUrl` - HTTP/HTTPS URLs only
- `AnyUrl` - Any valid URL scheme
- `SecretStr` - Masks sensitive data in output

#### Database & Cache Validators

```python
from msgspec_ext import BaseSettings, PostgresDsn, RedisDsn

class ConnectionSettings(BaseSettings):
    database_url: PostgresDsn  # postgresql://user:pass@host/db
    cache_url: RedisDsn  # redis://localhost:6379
```

#### Payment Card Validation

```python
from msgspec_ext import BaseSettings, PaymentCardNumber

class PaymentSettings(BaseSettings):
    card: PaymentCardNumber  # Luhn algorithm + masking
```

**Features:**
- Validates using Luhn algorithm
- Automatically strips spaces/dashes
- Masks card number in repr (shows last 4 digits only)

#### Path Validators

```python
from msgspec_ext import BaseSettings, FilePath, DirectoryPath

class PathSettings(BaseSettings):
    config_file: FilePath  # Must exist and be a file
    data_dir: DirectoryPath  # Must exist and be a directory
```

**Complete validator list:**

| Validator | Description |
|-----------|-------------|
| `PositiveInt` | Integer > 0 |
| `NegativeInt` | Integer < 0 |
| `NonNegativeInt` | Integer ≥ 0 |
| `NonPositiveInt` | Integer ≤ 0 |
| `PositiveFloat` | Float > 0.0 |
| `NegativeFloat` | Float < 0.0 |
| `NonNegativeFloat` | Float ≥ 0.0 |
| `NonPositiveFloat` | Float ≤ 0.0 |
| `EmailStr` | Email address (RFC 5321) |
| `HttpUrl` | HTTP/HTTPS URL |
| `AnyUrl` | Any valid URL |
| `SecretStr` | Masked sensitive data |
| `PostgresDsn` | PostgreSQL connection string |
| `RedisDsn` | Redis connection string |
| `PaymentCardNumber` | Credit card with Luhn validation |
| `FilePath` | Existing file path |
| `DirectoryPath` | Existing directory path |

See `examples/06_validators.py` for complete examples.

### Nested Configuration

```python
from msgspec_ext import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    name: str = "myapp"
    user: str = "postgres"
    password: str = ""

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__"
    )
    
    name: str = "My App"
    debug: bool = False
    database: DatabaseSettings

# Loads nested config from DATABASE__HOST, DATABASE__PORT, etc.
settings = AppSettings()
print(settings.database.host)  # from DATABASE__HOST env var
```

### Custom Validation

```python
from msgspec_ext import BaseSettings, SettingsConfigDict
from typing import Literal

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    # Custom validation with enums
    environment: Literal["development", "staging", "production"] = "development"
    
    # JSON parsing from environment variables
    features: list[str] = ["auth", "api"]
    limits: dict[str, int] = {"requests": 100, "timeout": 30}

settings = AppSettings()
print(settings.features)  # Automatically parsed from JSON string
```

## Why Choose msgspec-ext?

msgspec-ext provides a **faster, lighter alternative** to pydantic-settings while maintaining a familiar API and full type safety.

### Performance Comparison (Google Colab Results)

**Cold start** (first load, includes .env parsing) - *Benchmarked on Google Colab*:

| Library | Time per load | Speed |
|---------|---------------|-------|
| **msgspec-ext** | **0.353ms** | **7.0x faster** ⚡ |
| pydantic-settings | 2.47ms | Baseline |

**Warm (cached)** (repeated loads in long-running applications) - *Benchmarked on Google Colab*:

| Library | Time per load | Speed |
|---------|---------------|-------|
| **msgspec-ext** | **0.011ms** | **169x faster** ⚡ |
| pydantic-settings | 1.86ms | Baseline |

> *Benchmark executed on Google Colab includes .env file parsing, environment variable loading, type validation, and nested configuration. Run `benchmark/benchmark_cold_warm.py` on Google Colab to reproduce these results.*

### Key Advantages

| Feature | msgspec-ext | pydantic-settings |
|---------|------------|-------------------|
| **Cold start** | **7.0x faster** ⚡ | Baseline |
| **Warm (cached)** | **169x faster** ⚡ | Baseline |
| **Package size** | **0.49 MB** | 1.95 MB |
| **Dependencies** | **1 (msgspec only)** | 5+ |
| .env support | ✅ Built-in | ✅ Via python-dotenv |
| Type validation | ✅ | ✅ |
| Advanced caching | ✅ | ❌ |
| Nested config | ✅ | ✅ |
| JSON Schema | ✅ | ✅ |
| Secret masking | ⚠️ Planned | ✅ |

### How is it so fast?

msgspec-ext achieves its performance through:
- **Bulk validation**: Validates all fields at once in C (via msgspec), not one-by-one in Python
- **Custom .env parser**: Built-in fast parser with zero external dependencies (no python-dotenv overhead)
- **Smart caching**: Caches .env files, field mappings, and type information - loads after the first are 169x faster
- **Optimized file operations**: Uses fast os.path operations instead of slower pathlib alternatives
- **Zero overhead**: Fast paths for common types (str, bool, int, float) with minimal Python code

This means your application **starts faster** and uses **less memory**, especially important for:
- 🚀 **CLI tools** - 7.0x faster startup every time you run the command
- ⚡ **Serverless functions** - Lower cold start latency means better response times
- 🔄 **Long-running apps** - After the first load, reloading settings is 169x faster (11 microseconds!)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.