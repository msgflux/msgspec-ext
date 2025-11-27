"""Comprehensive tests for BaseSettings class."""

import os
import tempfile
from pathlib import Path

import pytest

from msgspec_ext import BaseSettings, SettingsConfigDict


def test_settings_import():
    """Test that BaseSettings can be imported."""
    assert BaseSettings is not None


def test_basic_settings_with_defaults():
    """Test creating settings with default values."""

    class AppSettings(BaseSettings):
        name: str = "test-app"
        port: int = 8000
        debug: bool = False

    settings = AppSettings()
    assert settings.name == "test-app"
    assert settings.port == 8000
    assert settings.debug is False


def test_settings_from_env_vars():
    """Test loading settings from environment variables."""
    os.environ["NAME"] = "from-env"
    os.environ["PORT"] = "9000"
    os.environ["DEBUG"] = "true"

    try:

        class AppSettings(BaseSettings):
            name: str
            port: int = 8000
            debug: bool = False

        settings = AppSettings()
        assert settings.name == "from-env"
        assert settings.port == 9000
        assert settings.debug is True
    finally:
        os.environ.pop("NAME", None)
        os.environ.pop("PORT", None)
        os.environ.pop("DEBUG", None)


def test_settings_with_env_prefix():
    """Test env_prefix configuration."""
    os.environ["APP_NAME"] = "prefixed-app"
    os.environ["APP_PORT"] = "3000"

    try:

        class AppSettings(BaseSettings):
            model_config = SettingsConfigDict(env_prefix="APP_")

            name: str
            port: int = 8000

        settings = AppSettings()
        assert settings.name == "prefixed-app"
        assert settings.port == 3000
    finally:
        os.environ.pop("APP_NAME", None)
        os.environ.pop("APP_PORT", None)


def test_settings_with_explicit_values():
    """Test creating settings with explicit keyword arguments."""

    class AppSettings(BaseSettings):
        name: str
        port: int = 8000
        debug: bool = False

    settings = AppSettings(name="explicit", port=5000, debug=True)
    assert settings.name == "explicit"
    assert settings.port == 5000
    assert settings.debug is True


def test_settings_type_conversion():
    """Test automatic type conversion from env vars."""
    os.environ["STR_VAL"] = "hello"
    os.environ["INT_VAL"] = "42"
    os.environ["FLOAT_VAL"] = "3.14"
    os.environ["BOOL_TRUE"] = "true"
    os.environ["BOOL_FALSE"] = "false"

    try:

        class TypeSettings(BaseSettings):
            str_val: str
            int_val: int
            float_val: float
            bool_true: bool
            bool_false: bool

        settings = TypeSettings()
        assert settings.str_val == "hello"
        assert settings.int_val == 42
        assert settings.float_val == 3.14
        assert settings.bool_true is True
        assert settings.bool_false is False
    finally:
        for key in ["STR_VAL", "INT_VAL", "FLOAT_VAL", "BOOL_TRUE", "BOOL_FALSE"]:
            os.environ.pop(key, None)


def test_settings_bool_conversion_variants():
    """Test different boolean string representations."""
    test_cases = [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("y", True),
        ("t", True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("0", False),
        ("no", False),
        ("n", False),
        ("f", False),
    ]

    for env_value, expected in test_cases:
        os.environ["BOOL_VAL"] = env_value

        try:

            class BoolSettings(BaseSettings):
                bool_val: bool

            settings = BoolSettings()
            assert settings.bool_val is expected, (
                f"Failed for env_value='{env_value}', expected={expected}"
            )
        finally:
            os.environ.pop("BOOL_VAL", None)


def test_settings_from_env_file():
    """Test loading settings from .env file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("NAME=env-file-app\n")
        f.write("PORT=7000\n")
        f.write("DEBUG=true\n")
        env_file_path = f.name

    try:

        class AppSettings(BaseSettings):
            model_config = SettingsConfigDict(env_file=env_file_path)

            name: str
            port: int = 8000
            debug: bool = False

        settings = AppSettings()
        assert settings.name == "env-file-app"
        assert settings.port == 7000
        assert settings.debug is True
    finally:
        # Clean up env vars loaded from file
        os.environ.pop("NAME", None)
        os.environ.pop("PORT", None)
        os.environ.pop("DEBUG", None)
        Path(env_file_path).unlink(missing_ok=True)


def test_settings_optional_fields():
    """Test optional fields with None default."""

    class OptionalSettings(BaseSettings):
        required: str
        optional: str | None = None
        optional_int: int | None = None

    settings = OptionalSettings(required="test")
    assert settings.required == "test"
    assert settings.optional is None
    assert settings.optional_int is None

    settings2 = OptionalSettings(required="test", optional="value", optional_int=42)
    assert settings2.optional == "value"
    assert settings2.optional_int == 42


def test_settings_json_list_from_env():
    """Test loading list from JSON env var."""
    os.environ["HOSTS"] = '["localhost", "127.0.0.1", "0.0.0.0"]'

    try:

        class ListSettings(BaseSettings):
            hosts: list[str]

        settings = ListSettings()
        assert settings.hosts == ["localhost", "127.0.0.1", "0.0.0.0"]
    finally:
        os.environ.pop("HOSTS", None)


def test_settings_json_dict_from_env():
    """Test loading dict from JSON env var."""
    os.environ["CONFIG"] = '{"key1": "value1", "key2": 42}'

    try:

        class DictSettings(BaseSettings):
            config: dict

        settings = DictSettings()
        assert settings.config == {"key1": "value1", "key2": 42}
    finally:
        os.environ.pop("CONFIG", None)


def test_model_dump():
    """Test model_dump method."""

    class AppSettings(BaseSettings):
        name: str = "test"
        port: int = 8000

    settings = AppSettings()
    data = settings.model_dump()

    assert isinstance(data, dict)
    assert data == {"name": "test", "port": 8000}


def test_model_dump_json():
    """Test model_dump_json method."""

    class AppSettings(BaseSettings):
        name: str = "test"
        port: int = 8000
        debug: bool = True

    settings = AppSettings()
    json_str = settings.model_dump_json()

    assert isinstance(json_str, str)
    assert "test" in json_str
    assert "8000" in json_str
    assert "true" in json_str


def test_schema():
    """Test schema generation."""

    class AppSettings(BaseSettings):
        name: str
        port: int = 8000
        debug: bool = False

    # Schema is a classmethod on the returned struct
    settings = AppSettings(name="test")
    schema = type(settings).schema()

    assert isinstance(schema, dict)
    assert "$defs" in schema or "properties" in schema or "$ref" in schema


def test_settings_validation_error_missing_required():
    """Test that missing required fields raise errors."""

    class AppSettings(BaseSettings):
        required_field: str
        optional_field: str = "default"

    # Should raise error when required field is missing
    with pytest.raises((ValueError, TypeError)):
        AppSettings()


def test_settings_validation_error_wrong_type():
    """Test that wrong types raise validation errors."""
    os.environ["PORT"] = "not-a-number"

    try:

        class AppSettings(BaseSettings):
            port: int

        with pytest.raises(ValueError):
            AppSettings()
    finally:
        os.environ.pop("PORT", None)


def test_case_sensitive_false():
    """Test case_sensitive=False (default)."""
    os.environ["app_name"] = "lowercase"  # lowercase env var
    os.environ["APP_NAME"] = "uppercase"  # uppercase env var

    try:

        class AppSettings(BaseSettings):
            model_config = SettingsConfigDict(case_sensitive=False)
            app_name: str

        settings = AppSettings()
        # Should use uppercase version (APP_NAME)
        assert settings.app_name == "uppercase"
    finally:
        os.environ.pop("app_name", None)
        os.environ.pop("APP_NAME", None)


def test_settings_struct_instance():
    """Test that returned instance is a msgspec Struct."""
    import msgspec

    class AppSettings(BaseSettings):
        name: str = "test"

    settings = AppSettings()

    # Should be a Struct instance
    assert hasattr(settings, "__struct_fields__")
    assert "name" in settings.__struct_fields__


def test_settings_caching():
    """Test that Struct classes are cached."""

    class AppSettings(BaseSettings):
        name: str = "test"

    settings1 = AppSettings()
    settings2 = AppSettings()

    # Should be same Struct class (cached)
    assert type(settings1) is type(settings2)


def test_settings_with_multiple_types():
    """Test settings with various field types."""

    class ComplexSettings(BaseSettings):
        name: str = "app"
        port: int = 8000
        timeout: float = 30.5
        enabled: bool = True
        tags: list[str] | None = None

    settings = ComplexSettings()
    assert settings.name == "app"
    assert settings.port == 8000
    assert settings.timeout == 30.5
    assert settings.enabled is True
    assert settings.tags is None


def test_env_override_defaults():
    """Test that env vars override default values."""
    os.environ["PORT"] = "9000"

    try:

        class AppSettings(BaseSettings):
            port: int = 8000  # default

        settings = AppSettings()
        assert settings.port == 9000  # env var overrides default
    finally:
        os.environ.pop("PORT", None)


def test_explicit_override_env():
    """Test that explicit values override env vars."""
    os.environ["PORT"] = "9000"

    try:

        class AppSettings(BaseSettings):
            port: int = 8000

        settings = AppSettings(port=7000)  # explicit value
        assert settings.port == 7000  # explicit overrides env
    finally:
        os.environ.pop("PORT", None)
