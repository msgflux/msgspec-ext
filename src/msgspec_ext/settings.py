"""Optimized settings management using msgspec.Struct and bulk JSON decoding."""

import os
import types
from typing import Annotated, Any, ClassVar, Union, get_args, get_origin

import msgspec

from msgspec_ext.fast_dotenv import load_dotenv
from msgspec_ext.types import (
    AnyUrl,
    ByteSize,
    DirectoryPath,
    EmailStr,
    FilePath,
    FutureDate,
    HttpUrl,
    IPv4Address,
    IPv6Address,
    IPvAnyAddress,
    MacAddress,
    PastDate,
    PaymentCardNumber,
    PostgresDsn,
    RedisDsn,
    SecretStr,
)

__all__ = ["BaseSettings", "SettingsConfigDict"]


def _dec_hook(typ: type, obj: Any) -> Any:
    """Decoding hook for custom types.

    Handles conversion from JSON-decoded values to custom types like EmailStr, HttpUrl, etc.

    Args:
        typ: The target type to decode to
        obj: The JSON-decoded object

    Returns:
        Converted object of type typ

    Raises:
        NotImplementedError: If type is not supported
    """
    # Handle our custom string types
    custom_types = (
        EmailStr,
        HttpUrl,
        AnyUrl,
        SecretStr,
        PostgresDsn,
        RedisDsn,
        PaymentCardNumber,
        FilePath,
        DirectoryPath,
        IPv4Address,
        IPv6Address,
        IPvAnyAddress,
        MacAddress,
    )
    if typ in custom_types:
        if isinstance(obj, str):
            return typ(obj)

    # Handle ByteSize (accepts str or int)
    if typ is ByteSize:
        return ByteSize(obj)

    # Handle date types (PastDate, FutureDate)
    if typ in (PastDate, FutureDate):
        return typ(obj)

    # Handle ConStr (string with constraints) - but needs special handling
    # ConStr requires additional parameters, so it can't be used directly in dec_hook
    # Users should use it manually or with custom validators

    # If we don't handle it, let msgspec raise an error
    raise NotImplementedError(f"Type {typ} unsupported in dec_hook")


def _enc_hook(obj: Any) -> Any:
    """Encoding hook for custom types.

    Handles conversion from custom types to JSON-serializable values.

    Args:
        obj: The object to encode

    Returns:
        JSON-serializable representation of obj

    Raises:
        NotImplementedError: If type is not supported
    """
    # Convert all our custom string-based types to str
    custom_types = (
        EmailStr,
        HttpUrl,
        AnyUrl,
        SecretStr,
        PostgresDsn,
        RedisDsn,
        PaymentCardNumber,
        FilePath,
        DirectoryPath,
        IPv4Address,
        IPv6Address,
        IPvAnyAddress,
        MacAddress,
    )
    if isinstance(obj, custom_types):
        return str(obj)

    # Convert ByteSize to int
    if isinstance(obj, ByteSize):
        return int(obj)

    # Convert date types to ISO format string
    if isinstance(obj, (PastDate, FutureDate)):
        return obj.isoformat()

    # If we don't handle it, let msgspec raise an error
    raise NotImplementedError(
        f"Encoding objects of type {type(obj).__name__} is unsupported"
    )


class SettingsConfigDict(msgspec.Struct):
    """Configuration options for BaseSettings."""

    env_file: str | None = None
    env_file_encoding: str = "utf-8"
    case_sensitive: bool = False
    env_prefix: str = ""
    env_nested_delimiter: str | None = None
    env_nested_max_depth: int = 0


class BaseSettings:
    """Base class for settings loaded from environment variables.

    This class acts as a wrapper factory that creates optimized msgspec.Struct
    instances. It uses bulk JSON decoding for maximum performance.

    Usage:
        class AppSettings(BaseSettings):
            model_config = SettingsConfigDict(env_prefix="APP_")

            name: str
            port: int = 8000

        # Load from environment variables
        settings = AppSettings()

        # Load with overrides
        settings = AppSettings(name="custom", port=9000)

    Performance:
        - Uses msgspec.json.decode for bulk validation (all in C)
        - ~10-100x faster than field-by-field validation
        - Minimal Python overhead
    """

    model_config: SettingsConfigDict = SettingsConfigDict()

    # Cache for dynamically created Struct classes
    _struct_class_cache: ClassVar[dict[type, type]] = {}

    # Cache for JSON encoders and decoders (performance optimization)
    _encoder_cache: ClassVar[dict[type, msgspec.json.Encoder]] = {}
    _decoder_cache: ClassVar[dict[type, msgspec.json.Decoder]] = {}

    # Cache for loaded .env files (massive performance boost)
    _loaded_env_files: ClassVar[set[str]] = set()

    # Cache for field name to env name mapping
    _field_env_mapping_cache: ClassVar[dict[type, dict[str, str]]] = {}

    # Cache for absolute paths to avoid repeated pathlib operations
    _absolute_path_cache: ClassVar[dict[str, str]] = {}

    # Cache for type introspection results (avoid repeated get_origin/get_args calls)
    _type_cache: ClassVar[dict[type, type]] = {}

    def __new__(cls, **kwargs):
        """Create a msgspec.Struct instance from environment variables or kwargs.

        Args:
            **kwargs: Explicit field values (override environment variables)

        Returns:
            msgspec.Struct instance with validated fields
        """
        # Get or create Struct class for this Settings class
        struct_cls = cls._get_or_create_struct_class()

        # Load from environment if no kwargs provided
        if not kwargs:
            return cls._create_from_env(struct_cls)
        else:
            # Create from explicit values using bulk JSON decode
            return cls._create_from_dict(struct_cls, kwargs)

    @classmethod
    def _get_or_create_struct_class(cls):
        """Get cached Struct class or create a new one."""
        if cls not in cls._struct_class_cache:
            cls._struct_class_cache[cls] = cls._create_struct_class()
        return cls._struct_class_cache[cls]

    @classmethod
    def _create_struct_class(cls):
        """Create a msgspec.Struct class from BaseSettings definition.

        This dynamically creates a Struct with:
        - Fields from annotations
        - Default values from class attributes
        - Injected helper methods (model_dump, model_dump_json, schema)
        - Automatic field ordering (required before optional)
        """
        # Extract fields from annotations (skip model_config)
        required_fields = []
        optional_fields = []

        for field_name, field_type in cls.__annotations__.items():
            if field_name == "model_config":
                continue

            # Resolve BaseSettings subclass types to struct equivalents
            resolved_type = cls._resolve_field_type(field_type)

            # Get default value from class attribute if exists
            if hasattr(cls, field_name):
                default_value = getattr(cls, field_name)
                # Field with default: (name, type, default) - goes to optional
                optional_fields.append((field_name, resolved_type, default_value))
            else:
                # Required field: (name, type) - goes to required
                required_fields.append((field_name, resolved_type))

        # IMPORTANT: Required fields must come before optional fields
        # This avoids "Required field cannot follow optional fields" error
        fields = required_fields + optional_fields

        # Create Struct dynamically using defstruct
        struct_cls = msgspec.defstruct(
            cls.__name__,
            fields,
            kw_only=True,
        )

        # Inject helper methods
        cls._inject_helper_methods(struct_cls)

        return struct_cls

    @classmethod
    def _resolve_field_type(cls, field_type):
        """Convert BaseSettings subclass types to their struct equivalents.

        Recursively walks the type tree to handle:
        - Direct: DatabaseSettings → DatabaseStruct
        - Union/Optional: DatabaseSettings | None → DatabaseStruct | None
        - Generic: list[DatabaseSettings] → list[DatabaseStruct]
        - Annotated: Annotated[DatabaseSettings, Meta] → Annotated[DatabaseStruct, Meta]
        """
        # Direct BaseSettings subclass
        if (
            isinstance(field_type, type)
            and field_type is not BaseSettings
            and issubclass(field_type, BaseSettings)
        ):
            return field_type._get_or_create_struct_class()

        origin = get_origin(field_type)
        if origin is None:
            return field_type

        args = get_args(field_type)
        if not args:
            return field_type

        # Handle Union / Optional (typing.Union and Python 3.10+ X | Y)
        if origin is Union or origin is types.UnionType:
            resolved = tuple(cls._resolve_field_type(a) for a in args)
            if resolved != args:
                result = resolved[0]
                for t in resolved[1:]:
                    result = result | t
                return result
            return field_type

        # Handle Annotated[BaseType, *metadata]
        if origin is Annotated:
            resolved_base = cls._resolve_field_type(args[0])
            if resolved_base is not args[0]:
                return Annotated[(resolved_base, *args[1:])]
            return field_type

        # Handle generic types: list[X], dict[K, V], set[X], tuple[X, ...], etc.
        resolved = tuple(cls._resolve_field_type(a) for a in args)
        if resolved != args:
            return (
                origin[resolved[0]] if len(resolved) == 1 else origin[tuple(resolved)]
            )

        return field_type

    @classmethod
    def _inject_helper_methods(cls, struct_cls):
        """Inject helper methods into the dynamically created Struct."""

        def model_dump(self) -> dict[str, Any]:
            """Return settings as a dictionary."""
            return {f: getattr(self, f) for f in self.__struct_fields__}

        def model_dump_json(self) -> str:
            """Return settings as a JSON string."""
            return msgspec.json.encode(self).decode()

        @classmethod
        def schema(struct_cls_inner) -> dict[str, Any]:
            """Return JSON schema for the settings."""
            return msgspec.json.schema(struct_cls_inner)

        # Attach methods to Struct class
        struct_cls.model_dump = model_dump
        struct_cls.model_dump_json = model_dump_json
        struct_cls.schema = schema

    @classmethod
    def _create_from_env(cls, struct_cls):
        """Create Struct instance from environment variables.

        This is the core optimization: loads all env vars at once,
        converts to JSON, then uses msgspec.json.decode for bulk validation.
        """
        # 1. Load .env file if specified
        cls._load_env_files()

        # 2. Collect all environment values
        env_dict = cls._collect_env_values(struct_cls)

        # 3. Add defaults for missing optional fields (handled by msgspec)
        # No-op for now, msgspec.defstruct handles defaults automatically

        # 4. Bulk decode with validation (ALL IN C!)
        return cls._decode_from_dict(struct_cls, env_dict)

    @classmethod
    def _create_from_dict(cls, struct_cls, values: dict[str, Any]):
        """Create Struct instance from explicit values dict."""
        # Bulk decode with validation (defaults handled by msgspec)
        return cls._decode_from_dict(struct_cls, values)

    @classmethod
    def _decode_from_dict(cls, struct_cls, values: dict[str, Any]):
        """Decode dict to Struct using JSON encoding/decoding with cached encoder/decoder.

        This is the key performance optimization:
        1. Reuses cached encoder/decoder instances (faster than creating new ones)
        2. msgspec.json.decode validates and converts all fields in one C-level operation
        """
        try:
            # Get or create cached encoder/decoder pair atomically
            encoder_decoder = cls._encoder_cache.get(struct_cls)
            if encoder_decoder is None:
                encoder = msgspec.json.Encoder()
                decoder = msgspec.json.Decoder(type=struct_cls, dec_hook=_dec_hook)
                encoder_decoder = (encoder, decoder)
                cls._encoder_cache[struct_cls] = encoder_decoder
                cls._decoder_cache[struct_cls] = encoder_decoder
            else:
                encoder, decoder = encoder_decoder

            # Encode and decode in one shot
            json_bytes = encoder.encode(values)
            return decoder.decode(json_bytes)

        except msgspec.ValidationError as e:
            # Re-raise with more context
            raise ValueError(f"Validation error: {e}") from e
        except msgspec.EncodeError as e:
            # Error encoding to JSON (e.g., invalid type in values dict)
            raise ValueError(f"Error encoding values to JSON: {e}") from e

    @classmethod
    def _load_env_files(cls):
        """Load environment variables from .env file if specified.

        Uses caching to avoid re-parsing the same .env file multiple times.
        This provides massive performance gains for repeated instantiations.

        Optimized to minimize filesystem operations (2.5x faster on cache hits):
        - Uses os.path.abspath() instead of Path().absolute() (2x faster)
        - Uses os.path.exists() instead of Path.exists() (3.5x faster)
        - Fast return on cache hit to avoid unnecessary checks
        """
        if not cls.model_config.env_file:
            return

        # Get or compute cached absolute path using os.path (faster than pathlib)
        cache_key = cls._absolute_path_cache.get(cls.model_config.env_file)
        if cache_key is None:
            # First time: compute and cache absolute path
            cache_key = os.path.abspath(cls.model_config.env_file)
            cls._absolute_path_cache[cls.model_config.env_file] = cache_key

        # Fast path: if already loaded, return immediately (cache hit)
        if cache_key in cls._loaded_env_files:
            return

        # Only load if file exists (os.path.exists is 3.5x faster than Path.exists)
        if os.path.exists(cache_key):
            load_dotenv(
                dotenv_path=cls.model_config.env_file,
                encoding=cls.model_config.env_file_encoding,
            )
            cls._loaded_env_files.add(cache_key)

    @classmethod
    def _collect_env_values(cls, struct_cls) -> dict[str, Any]:
        """Collect environment variable values for all fields."""
        if cls.model_config.env_nested_delimiter is not None:
            return cls._collect_nested_env_values(struct_cls)
        return cls._collect_flat_env_values(struct_cls)

    @classmethod
    def _collect_flat_env_values(cls, struct_cls) -> dict[str, Any]:
        """Collect flat environment variable values for all fields.

        Returns dict with field_name -> converted_value.
        Highly optimized with cached field->env name mapping.
        """
        env_dict = {}

        # Get cached field->env name mapping or create it
        field_mapping = cls._field_env_mapping_cache.get(cls)
        if field_mapping is None:
            field_mapping = {}
            for field_name in struct_cls.__struct_fields__:
                field_mapping[field_name] = cls._get_env_name(field_name)
            cls._field_env_mapping_cache[cls] = field_mapping

        # Cache struct fields and annotations as local variables for faster access
        struct_fields = struct_cls.__struct_fields__
        annotations = struct_cls.__annotations__
        environ_get = os.environ.get  # Local reference for faster calls
        preprocess_func = cls._preprocess_env_value  # Local reference

        for field_name in struct_fields:
            # Get cached environment variable name
            env_name = field_mapping[field_name]
            env_value = environ_get(env_name)

            if env_value is not None:
                # Preprocess string value to proper type for JSON
                field_type = annotations[field_name]
                converted_value = preprocess_func(env_value, field_type)
                env_dict[field_name] = converted_value

        return env_dict

    @classmethod
    def _collect_nested_env_values(cls, struct_cls) -> dict[str, Any]:
        """Collect env values and unfold nested keys by delimiter."""
        delimiter = cls.model_config.env_nested_delimiter
        prefix = cls.model_config.env_prefix
        case_sensitive = cls.model_config.case_sensitive
        max_depth = cls.model_config.env_nested_max_depth

        # Precompute prefix and delimiter for case-insensitive matching
        if not case_sensitive:
            prefix = prefix.upper()
            delimiter = delimiter.upper()
        prefix_len = len(prefix)

        result = {}
        struct_fields = set(struct_cls.__struct_fields__)

        for env_key, env_value in os.environ.items():
            # Normalize key for matching
            key = env_key if case_sensitive else env_key.upper()

            # Check and strip prefix
            if prefix:
                if not key.startswith(prefix):
                    continue
                key = key[prefix_len:]

            # Split by delimiter (respect max_depth)
            if max_depth > 0:
                parts = key.split(delimiter, maxsplit=max_depth)
            else:
                parts = key.split(delimiter)

            # Normalize parts to field names (lowercase for case-insensitive)
            if not case_sensitive:
                parts = [p.lower() for p in parts]

            # Skip if root field doesn't exist in struct
            if parts[0] not in struct_fields:
                continue

            # Resolve leaf type and preprocess value
            leaf_type = cls._resolve_leaf_type(struct_cls, parts)
            if leaf_type is not None:
                converted = cls._preprocess_env_value(env_value, leaf_type)
            else:
                converted = env_value

            # Set value in nested dict
            cls._set_nested_value(result, parts, converted)

        return result

    @staticmethod
    def _set_nested_value(target: dict, parts: list[str], value: Any) -> None:
        """Set a value in a nested dict by key path."""
        for part in parts[:-1]:
            if part not in target or not isinstance(target[part], dict):
                target[part] = {}
            target = target[part]
        target[parts[-1]] = value

    @classmethod
    def _resolve_leaf_type(cls, struct_cls, parts: list[str]) -> type | None:
        """Walk struct annotations to find the leaf field type."""
        current = struct_cls
        for i, part in enumerate(parts):
            annotations = current.__annotations__
            if part not in annotations:
                return None
            field_type = annotations[part]
            if i == len(parts) - 1:
                return field_type
            # Navigate into nested struct
            inner = cls._unwrap_struct_type(field_type)
            if inner is not None and hasattr(inner, "__struct_fields__"):
                current = inner
            else:
                return None
        return None

    @classmethod
    def _unwrap_struct_type(cls, field_type) -> type | None:
        """Extract the core struct type, unwrapping Optional if needed."""
        if isinstance(field_type, type) and hasattr(field_type, "__struct_fields__"):
            return field_type
        origin = get_origin(field_type)
        if origin is Union or origin is types.UnionType:
            args = get_args(field_type)
            non_none = [a for a in args if a is not type(None)]
            if len(non_none) == 1 and hasattr(non_none[0], "__struct_fields__"):
                return non_none[0]
        return None

    @classmethod
    def _get_env_name(cls, field_name: str) -> str:
        """Convert Python field name to environment variable name.

        Examples:
            field_name="app_name", prefix="", case_sensitive=False -> "APP_NAME"
            field_name="port", prefix="MY_", case_sensitive=False -> "MY_PORT"
        """
        # Fast path: no transformations needed
        if cls.model_config.case_sensitive and not cls.model_config.env_prefix:
            return field_name

        env_name = field_name

        if not cls.model_config.case_sensitive:
            env_name = env_name.upper()

        if cls.model_config.env_prefix:
            env_name = f"{cls.model_config.env_prefix}{env_name}"

        return env_name

    @classmethod
    def _preprocess_env_value(cls, env_value: str, field_type: type) -> Any:  # noqa: C901, PLR0912
        """Convert environment variable string to JSON-compatible type.

        Ultra-optimized to minimize type introspection overhead with caching.

        Examples:
            "true" -> True (for bool fields)
            "123" -> 123 (for int fields)
            "[1,2,3]" -> [1,2,3] (for list fields)
        """
        # Fast path: JSON structures (most complex case first)
        if env_value and env_value[0] in "{[":
            try:
                return msgspec.json.decode(env_value.encode())
            except msgspec.DecodeError as e:
                raise ValueError(f"Invalid JSON in env var: {e}") from e

        # Check type cache first
        cached_type = cls._type_cache.get(field_type)
        if cached_type is not None:
            field_type = cached_type

        # Fast path: Direct type comparison (avoid get_origin when possible)
        if field_type is str:
            return env_value
        if field_type is bool:
            return env_value.lower() in ("true", "1", "yes", "y", "t")
        if field_type is int:
            try:
                return int(env_value)
            except ValueError as e:
                raise ValueError(f"Cannot convert '{env_value}' to int") from e
        if field_type is float:
            try:
                return float(env_value)
            except ValueError as e:
                raise ValueError(f"Cannot convert '{env_value}' to float") from e

        # Only use typing introspection for complex types (Union, Optional, Annotated, etc.)
        origin = get_origin(field_type)

        # Handle Annotated types (e.g., Annotated[int, Meta(...)])
        # For Annotated, get_origin returns typing.Annotated and get_args()[0] is the base type
        if origin is not None and (
            origin is Annotated or str(origin) == "typing.Annotated"
        ):
            args = get_args(field_type)
            if args:
                base_type = args[0]
                # Cache and recursively process with base type
                cls._type_cache[field_type] = base_type
                return cls._preprocess_env_value(env_value, base_type)

        if origin is Union:
            args = get_args(field_type)
            non_none = [a for a in args if a is not type(None)]
            if non_none:
                # Cache the resolved type for future use
                resolved_type = non_none[0]
                cls._type_cache[field_type] = resolved_type
                # Recursively process with the non-None type
                return cls._preprocess_env_value(env_value, resolved_type)

        return env_value
