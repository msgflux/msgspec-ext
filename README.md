<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/msgflux/msgspec-ext/main/docs/assets/msgspec-ext-logo-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/msgflux/msgspec-ext/main/docs/assets/msgspec-ext-logo-light.png">
    <img alt="msgspec-ext" src="https://raw.githubusercontent.com/msgflux/msgspec-ext/main/docs/assets/msgspec-ext-logo-light.png" width="340">
  </picture>
</p>

<p align="center">
  <b>High-performance settings management and validation library powered by <a href="https://github.com/jcrist/msgspec">msgspec</a></b>
</p>

<p align="center">
  <a href="https://github.com/msgflux/msgspec-ext/actions/workflows/ci.yml"><img src="https://github.com/msgflux/msgspec-ext/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/msgspec-ext/"><img src="https://img.shields.io/pypi/v/msgspec-ext.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/msgspec-ext/"><img src="https://img.shields.io/pypi/pyversions/msgspec-ext.svg" alt="Python Versions"></a>
  <a href="https://github.com/msgflux/msgspec-ext/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
</p>

## Features

- ⚡ **7x faster than pydantic-settings** - Built on [msgspec](https://github.com/jcrist/msgspec)'s high-performance validation
- 🎯 **26 built-in validators** - Email, URLs, IP addresses, MAC addresses, dates, storage sizes, and more
- 🔧 **Drop-in API compatibility** - Familiar interface, easy migration from pydantic-settings
- 📦 **All msgspec types supported** - Full compatibility with [msgspec's rich type system](https://jcristharif.com/msgspec/supported-types.html)
- 🔐 **Type-safe** - Complete type hints and validation
- 📁 **.env support** - Fast built-in .env parser (169x faster cached loads)
- 🎨 **Nested settings** - Support for complex configuration structures
- 🪶 **Zero dependencies** - Only msgspec required

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

### With BaseSettings (Environment Variables)

```python
from msgspec_ext import BaseSettings, EmailStr, HttpUrl, PositiveInt

class AppSettings(BaseSettings):
    # Basic types (msgspec native support)
    name: str
    debug: bool = False

    # Numeric validators
    port: PositiveInt = 8000  # Must be > 0
    workers: PositiveInt = 4

    # String validators
    admin_email: EmailStr  # RFC 5321 validation
    api_url: HttpUrl  # HTTP/HTTPS only

# Load from environment variables and .env file
settings = AppSettings()

print(settings.name)  # my-app
print(settings.port)  # 8000
print(settings.admin_email)  # admin@example.com

# Serialize to dict
print(settings.model_dump())
# Output: {
#   'name': 'my-app',
#   'debug': False,
#   'port': 8000,
#   'workers': 4,
#   'admin_email': 'admin@example.com',
#   'api_url': 'https://api.example.com'
# }

# Serialize to JSON
print(settings.model_dump_json())
# Output: '{"name":"my-app","debug":false,"port":8000,"workers":4,"admin_email":"admin@example.com","api_url":"https://api.example.com"}'
```

Set environment variables:
```bash
export NAME="my-app"
export ADMIN_EMAIL="admin@example.com"
export API_URL="https://api.example.com"
```

### With msgspec Structs (Direct Usage)

All validators work directly with msgspec structs for JSON/MessagePack serialization:

```python
import msgspec
from msgspec_ext import EmailStr, IPv4Address, ByteSize, PositiveInt, dec_hook, enc_hook

class ServerConfig(msgspec.Struct):
    host: IPv4Address
    port: PositiveInt
    admin_email: EmailStr
    max_upload: ByteSize

# From JSON (use dec_hook for custom type conversion)
config = msgspec.json.decode(
    b'{"host":"192.168.1.100","port":8080,"admin_email":"admin@example.com","max_upload":"50MB"}',
    type=ServerConfig,
    dec_hook=dec_hook
)

print(config.host)  # 192.168.1.100
print(int(config.max_upload))  # 50000000 (50MB in bytes)

# To JSON (use enc_hook to serialize custom types)
json_bytes = msgspec.json.encode(config, enc_hook=enc_hook)
```

## Type Support

msgspec-ext supports **all msgspec native types** plus **26 additional validators** for common use cases.

### Built-in msgspec Types

msgspec-ext has full compatibility with [msgspec's extensive type system](https://jcristharif.com/msgspec/supported-types.html):

- **Basic**: `bool`, `int`, `float`, `str`, `bytes`, `bytearray`
- **Collections**: `list`, `tuple`, `set`, `frozenset`, `dict`
- **Typing**: `Optional`, `Union`, `Literal`, `Final`, `Annotated`
- **Advanced**: `datetime`, `date`, `time`, `timedelta`, `UUID`, `Decimal`
- **msgspec**: `msgspec.Raw`, `msgspec.UNSET` (re-exported for convenience)

Plus many more - see the [full list in msgspec documentation](https://jcristharif.com/msgspec/supported-types.html).

### Custom Validators (26 types)

msgspec-ext adds **26 specialized validators** for common validation scenarios:

#### 🔢 Numeric Constraints (8 types)

```python
from msgspec_ext import (
    PositiveInt, NegativeInt, NonNegativeInt, NonPositiveInt,
    PositiveFloat, NegativeFloat, NonNegativeFloat, NonPositiveFloat
)

class ServerSettings(BaseSettings):
    port: PositiveInt  # Must be > 0
    offset: NegativeInt  # Must be < 0
    retry_count: NonNegativeInt  # Can be 0 or positive
    balance: NonPositiveFloat  # Can be 0 or negative
```

#### 🌐 Network & Hardware (4 types)

```python
import msgspec
from msgspec_ext import IPv4Address, IPv6Address, IPvAnyAddress, MacAddress

# With BaseSettings
class NetworkSettings(BaseSettings):
    server_ipv4: IPv4Address  # 192.168.1.1
    server_ipv6: IPv6Address  # 2001:db8::1
    proxy_ip: IPvAnyAddress  # Accepts IPv4 or IPv6
    device_mac: MacAddress  # AA:BB:CC:DD:EE:FF

# Or with msgspec.Struct for API responses
class Device(msgspec.Struct):
    name: str
    ip: IPv4Address
    mac: MacAddress

device = msgspec.json.decode(
    b'{"name":"router-01","ip":"192.168.1.1","mac":"AA:BB:CC:DD:EE:FF"}',
    type=Device,
    dec_hook=dec_hook
)
```

#### ✉️ String Validators (4 types)

```python
from msgspec_ext import EmailStr, HttpUrl, AnyUrl, SecretStr

class AppSettings(BaseSettings):
    admin_email: EmailStr  # RFC 5321 validation
    api_url: HttpUrl  # HTTP/HTTPS only
    webhook_url: AnyUrl  # Any valid URL scheme
    api_key: SecretStr  # Masked in logs: **********
```

#### 🗄️ Database & Connections (3 types)

```python
from msgspec_ext import PostgresDsn, RedisDsn, PaymentCardNumber

class ConnectionSettings(BaseSettings):
    database_url: PostgresDsn  # postgresql://user:pass@host/db
    cache_url: RedisDsn  # redis://localhost:6379
    card_number: PaymentCardNumber  # Luhn validation + masking
```

#### 📁 Path Validators (2 types)

```python
from msgspec_ext import FilePath, DirectoryPath

class PathSettings(BaseSettings):
    config_file: FilePath  # Must exist and be a file
    data_dir: DirectoryPath  # Must exist and be a directory
```

#### 💾 Storage & Dates (3 types)

```python
import msgspec
from msgspec_ext import ByteSize, PastDate, FutureDate
from datetime import date

# With BaseSettings
class AppSettings(BaseSettings):
    max_upload: ByteSize  # Parse "10MB", "1GB", etc.
    cache_size: ByteSize  # Supports KB, MB, GB, KiB, MiB, GiB
    founding_date: PastDate  # Must be before today
    launch_date: FutureDate  # Must be after today

# Or with msgspec.Struct for configuration files
class StorageConfig(msgspec.Struct):
    max_file_size: ByteSize
    cache_limit: ByteSize
    cleanup_after: int  # days

config = msgspec.json.decode(
    b'{"max_file_size":"100MB","cache_limit":"5GB","cleanup_after":30}',
    type=StorageConfig,
    dec_hook=dec_hook
)
print(int(config.max_file_size))  # 100000000
```

#### 🎯 Constrained Strings (2 types)

```python
from msgspec_ext import ConStr

class UserSettings(BaseSettings):
    # With constraints
    username: ConStr  # Can use min_length, max_length, pattern

# Usage:
username = ConStr("alice", min_length=3, max_length=20, pattern=r"^[a-z0-9]+$")
```

### Complete Validator List

| Category | Validators |
|----------|-----------|
| **Numeric** | `PositiveInt`, `NegativeInt`, `NonNegativeInt`, `NonPositiveInt`, `PositiveFloat`, `NegativeFloat`, `NonNegativeFloat`, `NonPositiveFloat` |
| **Network** | `IPv4Address`, `IPv6Address`, `IPvAnyAddress`, `MacAddress` |
| **String** | `EmailStr`, `HttpUrl`, `AnyUrl`, `SecretStr` |
| **Database** | `PostgresDsn`, `RedisDsn`, `PaymentCardNumber` |
| **Paths** | `FilePath`, `DirectoryPath` |
| **Storage & Dates** | `ByteSize`, `PastDate`, `FutureDate` |
| **Constrained** | `ConStr` |

See `examples/06_validators.py` and `examples/07_advanced_validators.py` for complete usage examples.

## Use Cases

### API Request/Response Validation

```python
import msgspec
from msgspec_ext import EmailStr, HttpUrl, PositiveInt, ByteSize, dec_hook, enc_hook

class CreateUserRequest(msgspec.Struct):
    email: EmailStr
    age: PositiveInt
    website: HttpUrl
    max_storage: ByteSize

class UserResponse(msgspec.Struct):
    id: int
    email: EmailStr
    website: HttpUrl

# Validate incoming JSON
request = msgspec.json.decode(
    b'{"email":"user@example.com","age":25,"website":"https://example.com","max_storage":"1GB"}',
    type=CreateUserRequest,
    dec_hook=dec_hook
)

print(request.email)  # user@example.com
print(request.age)  # 25
print(int(request.max_storage))  # 1000000000

# Serialize response
response = UserResponse(id=1, email=request.email, website=request.website)
json_bytes = msgspec.json.encode(response, enc_hook=enc_hook)
print(json_bytes)
# b'{"id":1,"email":"user@example.com","website":"https://example.com"}'
```

### Configuration Files with Validation

```python
import msgspec
from msgspec_ext import IPv4Address, PositiveInt, PostgresDsn, ByteSize, dec_hook

class ServerConfig(msgspec.Struct):
    host: IPv4Address
    port: PositiveInt
    database_url: PostgresDsn
    max_upload: ByteSize
    workers: PositiveInt = 4

# Load from JSON config file
with open("config.json", "rb") as f:
    config = msgspec.json.decode(f.read(), type=ServerConfig, dec_hook=dec_hook)

print(f"Server: {config.host}:{config.port}")
# Server: 192.168.1.50:8080

print(f"Max upload: {int(config.max_upload)} bytes")
# Max upload: 100000000 bytes

print(f"Workers: {config.workers}")
# Workers: 4
```

### Message Queue Data Validation

```python
import msgspec
from msgspec_ext import EmailStr, IPvAnyAddress, FutureDate, dec_hook, enc_hook

class ScheduledTask(msgspec.Struct):
    task_id: str
    notify_email: EmailStr
    target_server: IPvAnyAddress
    execute_at: FutureDate

# Serialize for queue (MessagePack is faster than JSON)
task = ScheduledTask(
    task_id="task-123",
    notify_email=EmailStr("admin@example.com"),
    target_server=IPvAnyAddress("192.168.1.100"),
    execute_at=FutureDate("2025-12-31")
)
msg_bytes = msgspec.msgpack.encode(task, enc_hook=enc_hook)

# Deserialize from queue
received_task = msgspec.msgpack.decode(msg_bytes, type=ScheduledTask, dec_hook=dec_hook)
```

## Advanced Usage

### Environment Variables & .env Files

```python
from msgspec_ext import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",  # Load from .env file
        env_prefix="APP_",  # Prefix for env vars
        env_nested_delimiter="__"  # Nested config separator
    )

    name: str
    debug: bool = False
    port: int = 8000

# Loads from APP_NAME, APP_DEBUG, APP_PORT
settings = AppSettings()
```

**.env file**:
```bash
APP_NAME=my-app
APP_DEBUG=true
APP_PORT=3000
APP_DATABASE__HOST=localhost
APP_DATABASE__PORT=5432
```

### Nested Configuration

```python
from msgspec_ext import BaseSettings, SettingsConfigDict, PostgresDsn

class DatabaseSettings(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    name: str = "myapp"
    url: PostgresDsn

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__"
    )

    name: str = "My App"
    debug: bool = False
    database: DatabaseSettings

# Loads from DATABASE__HOST, DATABASE__PORT, DATABASE__URL, etc.
settings = AppSettings()

print(settings.name)  # My App
print(settings.database.host)  # localhost
print(settings.database.port)  # 5432

# Full nested dump
print(settings.model_dump())
# Output: {
#   'name': 'My App',
#   'debug': False,
#   'database': {
#     'host': 'localhost',
#     'port': 5432,
#     'name': 'myapp',
#     'url': 'postgresql://user:pass@localhost:5432/myapp'
#   }
# }
```

### Secret Masking

```python
from msgspec_ext import BaseSettings, SecretStr

class AppSettings(BaseSettings):
    api_key: SecretStr
    db_password: SecretStr

settings = AppSettings()

print(settings.api_key)  # **********
print(settings.api_key.get_secret_value())  # actual-secret-key

print(settings.model_dump())
# Output: {'api_key': '**********', 'db_password': '**********'}

print(settings.model_dump_json())
# Output: '{"api_key":"**********","db_password":"**********"}'
```

### Storage Size Parsing

```python
from msgspec_ext import BaseSettings, ByteSize

class StorageSettings(BaseSettings):
    max_upload: ByteSize
    cache_limit: ByteSize

# Environment variables:
# MAX_UPLOAD=10MB
# CACHE_LIMIT=1GB

settings = StorageSettings()
print(int(settings.max_upload))  # 10000000 (10 MB in bytes)
print(int(settings.cache_limit))  # 1000000000 (1 GB in bytes)

print(settings.model_dump())
# Output: {'max_upload': 10000000, 'cache_limit': 1000000000}
```

Supported units: `B`, `KB`, `MB`, `GB`, `TB`, `KiB`, `MiB`, `GiB`, `TiB`

### Date Validation

```python
from msgspec_ext import BaseSettings, PastDate, FutureDate
from datetime import date, timedelta

class EventSettings(BaseSettings):
    founding_date: PastDate  # Must be before today
    launch_date: FutureDate  # Must be after today

# Environment variables:
# FOUNDING_DATE=2020-01-01
# LAUNCH_DATE=2025-12-31

settings = EventSettings()
```

### JSON Parsing from Environment

```python
from msgspec_ext import BaseSettings

class AppSettings(BaseSettings):
    # Automatically parse JSON from environment variables
    features: list[str] = ["auth", "api"]
    limits: dict[str, int] = {"requests": 100}
    config: dict[str, any] = {}

# Environment variable:
# FEATURES=["auth","api","payments"]
# LIMITS={"requests":1000,"timeout":30}

settings = AppSettings()
print(settings.features)  # ['auth', 'api', 'payments']
```

## Why Choose msgspec-ext?

msgspec-ext provides a **faster, lighter alternative** to pydantic-settings while offering **more validators** and maintaining a familiar API.

### Performance Comparison

**Cold start** (first load, includes .env parsing):

| Library | Time per load | Speed |
|---------|---------------|-------|
| **msgspec-ext** | **0.353ms** | **7.0x faster** ⚡ |
| pydantic-settings | 2.47ms | Baseline |

**Warm (cached)** (repeated loads in long-running applications):

| Library | Time per load | Speed |
|---------|---------------|-------|
| **msgspec-ext** | **0.011ms** | **169x faster** ⚡ |
| pydantic-settings | 1.86ms | Baseline |

> *Benchmarks run on Google Colab. Includes .env parsing, environment variable loading, type validation, and nested configuration. Run `benchmark/benchmark_cold_warm.py` to reproduce.*

### Key Advantages

| Feature | msgspec-ext | pydantic-settings |
|---------|------------|-------------------|
| **Cold start** | **7.0x faster** ⚡ | Baseline |
| **Warm (cached)** | **169x faster** ⚡ | Baseline |
| **Validators** | **26 built-in** | ~15 |
| **Package size** | **0.49 MB** | 1.95 MB |
| **Dependencies** | **1 (msgspec only)** | 5+ |
| .env support | ✅ Built-in fast parser | ✅ Via python-dotenv |
| Type validation | ✅ msgspec C backend | ✅ Pydantic |
| Advanced caching | ✅ 169x faster | ❌ |
| Nested config | ✅ | ✅ |
| JSON Schema | ✅ | ✅ |

### How is it so fast?

msgspec-ext achieves exceptional performance through:

1. **Bulk validation**: Validates all fields at once in C (via msgspec), not one-by-one in Python
2. **Custom .env parser**: Built-in fast parser with zero external dependencies (117.5x faster than pydantic)
3. **Smart caching**: Caches .env files, field mappings, and type information - subsequent loads are 169x faster
4. **Zero overhead**: Fast paths for common types with minimal Python code

This means:
- 🚀 **CLI tools** - 7.0x faster startup every invocation
- ⚡ **Serverless functions** - Lower cold start latency
- 🔄 **Long-running apps** - Reloading settings takes only 11 microseconds after first load!

## Examples

Check out the `examples/` directory for comprehensive examples:

- `01_basic_usage.py` - Getting started with BaseSettings
- `02_env_prefix.py` - Using environment variable prefixes
- `03_dotenv_file.py` - Loading from .env files
- `04_advanced_types.py` - Optional, lists, dicts, JSON parsing
- `05_serialization.py` - model_dump(), model_dump_json(), schema()
- `06_validators.py` - String, numeric, path, and database validators (17 types)
- `07_advanced_validators.py` - Network, storage, and date validators (8 types)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Built on top of the amazing [msgspec](https://github.com/jcrist/msgspec) library by [@jcrist](https://github.com/jcrist).
