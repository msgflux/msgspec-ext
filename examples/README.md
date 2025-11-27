# msgspec-ext Examples

This directory contains practical examples demonstrating various features of msgspec-ext.

## Running the Examples

All examples are standalone Python scripts. Run them using:

```bash
# Using uv (recommended)
uv run python examples/01_basic_usage.py

# Or with regular Python (if msgspec-ext is installed)
python examples/01_basic_usage.py
```

## Example Gallery

### 1. Basic Usage (`01_basic_usage.py`)

Learn the fundamentals of msgspec-ext:
- Creating settings classes with defaults
- Loading from environment variables
- Overriding with explicit values

**Key concepts**: BaseSettings, default values, environment loading

### 2. Environment Prefixes (`02_env_prefix.py`)

Use environment variable prefixes to namespace your settings:
- Organizing settings with prefixes (`DB_`, `REDIS_`, etc.)
- Managing multiple services in one environment
- Avoiding naming conflicts

**Key concepts**: `env_prefix`, SettingsConfigDict, service organization

### 3. .env Files (`03_dotenv_file.py`)

Load settings from `.env` files for local development:
- Creating and loading `.env` files
- Using different env files for different environments
- Best practices for secrets management

**Key concepts**: `.env` files, `env_file`, dotenv integration

### 4. Advanced Types (`04_advanced_types.py`)

Work with complex field types:
- Optional fields (`str | None`)
- Lists and arrays
- Dictionaries and nested data
- JSON loading from environment

**Key concepts**: Optional types, lists, dicts, JSON env vars

### 5. Serialization (`05_serialization.py`)

Serialize settings and generate schemas:
- `model_dump()` - Convert to dictionary
- `model_dump_json()` - Serialize to JSON
- `schema()` - Generate JSON Schema
- Use cases for each method

**Key concepts**: Serialization, JSON Schema, API integration

## Common Patterns

### Loading from Environment

```python
from msgspec_ext import BaseSettings

class AppSettings(BaseSettings):
    name: str
    port: int = 8000

settings = AppSettings()  # Loads from env vars automatically
```

### Using .env Files

```python
from msgspec_ext import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    name: str
    port: int = 8000

settings = AppSettings()  # Loads from .env file
```

### Environment Variable Prefixes

```python
from msgspec_ext import BaseSettings, SettingsConfigDict

class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")

    host: str = "localhost"  # Reads from DB_HOST
    port: int = 5432         # Reads from DB_PORT
```

### Complex Types

```python
import os
from msgspec_ext import BaseSettings

class Settings(BaseSettings):
    hosts: list[str] | None = None
    config: dict | None = None

# Set as JSON in environment
os.environ["HOSTS"] = '["localhost", "127.0.0.1"]'
os.environ["CONFIG"] = '{"debug": true}'

settings = Settings()
# hosts = ["localhost", "127.0.0.1"]
# config = {"debug": True}
```

## Tips and Best Practices

1. **Use prefixes** for multi-service applications to avoid conflicts
2. **Never commit** `.env` files with secrets to version control
3. **Use `.env.example`** to document required environment variables
4. **Leverage type hints** for IDE autocomplete and type checking
5. **Use JSON format** for complex types (lists, dicts) in env vars

## Performance Note

msgspec-ext is optimized for speed using bulk JSON decoding:
- **36% faster** than the previous implementation
- All validation happens in C (via msgspec)
- Minimal Python overhead

## Need Help?

- Check the main README for full documentation
- See the test suite (`tests/test_settings.py`) for more examples
- Report issues at: https://github.com/msgflux/msgspec-ext/issues
