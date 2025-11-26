import json
import os
from typing import Any, Dict, Optional, Type
from pathlib import Path
import msgspec
from dotenv import load_dotenv


__all__ = ["SettingsConfigDict", "BaseSettings"]


class SettingsConfigDict(msgspec.Struct):
    env_file: Optional[str] = None
    env_file_encoding: str = "utf-8"
    case_sensitive: bool = False
    env_prefix: str = ""
    env_nested_delimiter: str = "__"


class BaseSettings:
    model_config: SettingsConfigDict = SettingsConfigDict()

    def __init__(self, **values: Any):
        self._load_env_files()
        self._fields = self._get_fields_info()
        env_vars = self._get_env_vars()
        final_values = {**values, **env_vars}
        self._validate_and_set_values(final_values)

    @classmethod
    def _load_env_files(cls):
        """Loads environment variables from the .env file if specified."""
        if cls.model_config.env_file:
            env_path = Path(cls.model_config.env_file)
            if env_path.exists():
                load_dotenv(
                    dotenv_path=env_path, encoding=cls.model_config.env_file_encoding
                )

    def _get_env_vars(self) -> Dict[str, Any]:
        """Gets relevant environment variables based on type annotations."""
        env_vars = {}

        for field_name, field_type in self.__annotations__.items():
            if field_name == "model_config":
                continue

            env_name = self._get_env_name(field_name)
            env_value = os.environ.get(env_name)

            if env_value is not None:
                # Convert the string value to the appropriate type
                try:
                    converted_value = self._convert_env_value(env_value, field_type)
                    env_vars[field_name] = converted_value
                except (ValueError, json.JSONDecodeError) as e:
                    raise ValueError(
                        f"Error parsing environment variable {env_name}: {str(e)}"
                    )

        return env_vars

    def _get_fields_info(self) -> Dict[str, Any]:
        """Gets information about fields, including Field settings."""
        fields = {}
        for field_name in self.__annotations__:
            if field_name == "model_config":
                continue

            # Checks if there is a default value defined with Field
            field_value = getattr(self.__class__, field_name, None)
            if isinstance(field_value, msgspec.inspect.Field):
                fields[field_name] = {
                    "type": self.__annotations__[field_name],
                    "field": field_value,
                    "name": field_value.name or field_name,
                    "has_default": field_value.default is not msgspec.NODEFAULT,
                    "default": field_value.default
                    if field_value.default is not msgspec.NODEFAULT
                    else None,
                    "has_default_factory": field_value.default_factory
                    is not msgspec.NODEFAULT,
                    "default_factory": field_value.default_factory
                    if field_value.default_factory is not msgspec.NODEFAULT
                    else None,
                }
            else:
                fields[field_name] = {
                    "type": self.__annotations__[field_name],
                    "field": None,
                    "name": field_name,
                    "has_default": hasattr(self.__class__, field_name),
                    "default": field_value
                    if hasattr(self.__class__, field_name)
                    else None,
                    "has_default_factory": False,
                    "default_factory": None,
                }
        return fields

    def _get_env_name(self, field_name: str) -> str:
        """Generates the environment variable name for a field."""
        field_info = self._fields[field_name]
        name = field_info["name"]
        if not self.model_config.case_sensitive:
            name = name.upper()
        if self.model_config.env_prefix:
            name = f"{self.model_config.env_prefix}{name}"
        return name

    def _convert_env_value(self, value: str, field_type: Type) -> Any:
        """Converts an environment variable string to the appropriate type."""
        if field_type == bool:
            return value.lower() in ("true", "1", "t", "y", "yes")
        elif field_type == int or str(field_type).startswith("typing.Optional[int]"):
            return int(value)
        elif field_type == float or str(field_type).startswith(
            "typing.Optional[float]"
        ):
            return float(value)
        elif field_type == list or str(field_type).startswith("typing.List"):
            if value.startswith("[") and value.endswith("]"):
                return msgspec.json.decode(value.encode())
            return value.split(",")
        elif field_type == dict or str(field_type).startswith("typing.Dict"):
            return msgspec.json.decode(value.encode())
        # For complex types (like msgspec Structs)
        elif isinstance(
            msgspec.inspect.type_info(field_type), msgspec.inspect.StructType
        ):
            return msgspec.json.decode(value.encode(), type=field_type)
        # For other types, returns the original string
        return value

    def _get_field_default(self, field_name: str) -> Any:
        """Gets the default value for a field, considering default and default_factory."""
        field_info = self._fields[field_name]
        if field_info["has_default_factory"]:
            return field_info["default_factory"]()
        elif field_info["has_default"]:
            return field_info["default"]
        return None

    def _validate_and_set_values(self, values: Dict[str, Any]):
        """Validate and set values using msgspec."""
        for field_name, field_info in self._fields.items():
            value = values.get(field_name)

            if value is None:
                value = self._get_field_default(field_name)

            if value is not None:
                try:
                    validated_value = msgspec.convert(value, field_info["type"])
                    setattr(self, field_name, validated_value)
                except msgspec.ValidationError as e:
                    raise ValueError(
                        f"Validation error for field {field_name}: {str(e)}"
                    )
            elif (
                not field_info["has_default"] and not field_info["has_default_factory"]
            ):
                raise ValueError(f"Missing required field: {field_name}")

        # Stores schema after validation
        self._schema = self._generate_schema()

    def _generate_schema(self) -> Dict[str, Any]:
        """Generates the JSON Schema for the class."""

        def schema_hook(typ):
            if typ is self.__class__:
                return {
                    "type": "object",
                    "properties": {
                        field_name: msgspec.json.schema(
                            field_info["type"], schema_hook=schema_hook
                        )
                        for field_name, field_info in self._fields.items()
                    },
                    "required": [
                        field_name
                        for field_name, field_info in self._fields.items()
                        if not field_info["has_default"]
                        and not field_info["has_default_factory"]
                    ],
                }
            return None

        return msgspec.json.schema(self.__class__, schema_hook=schema_hook)

    def model_dump(self) -> Dict[str, Any]:
        """Returns data as a dict."""
        return {
            field_name: getattr(self, field_name)
            for field_name in self._fields
            if hasattr(self, field_name)
        }

    def model_dump_json(self) -> str:
        """Returns data as a JSON string."""
        return msgspec.json.encode(self.model_dump()).decode()

    def schema(self) -> Dict[str, Any]:
        """Returns the JSON schema of the data."""
        return self._schema
