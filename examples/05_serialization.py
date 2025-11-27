"""
Serialization and schema generation.

This example shows how to serialize settings to JSON and generate
JSON schemas for documentation and validation.
"""

import json

from msgspec_ext import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """API service configuration."""

    model_config = SettingsConfigDict(env_prefix="API_")

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # Security
    api_key: str
    enable_cors: bool = False
    allowed_origins: list[str] | None = None

    # Performance
    timeout: float = 30.0
    max_connections: int = 100
    enable_caching: bool = True


def main():
    print("=" * 60)
    print("Example 5: Serialization and Schema Generation")
    print("=" * 60)
    print()

    # Create settings instance
    settings = APISettings(
        api_key="sk-test-123456",
        enable_cors=True,
        allowed_origins=["https://example.com", "https://app.example.com"],
        workers=8,
    )

    # Example 1: model_dump() - Convert to dict
    print("1. model_dump() - Convert to dictionary:")
    settings_dict = settings.model_dump()
    for key, value in settings_dict.items():
        print(f"   {key}: {value}")
    print()

    # Example 2: model_dump_json() - Convert to JSON string
    print("2. model_dump_json() - Serialize to JSON:")
    json_str = settings.model_dump_json()
    print(f"   {json_str}")
    print()

    # Example 3: Pretty-print JSON
    print("3. Pretty-print JSON:")
    json_dict = json.loads(json_str)
    print(json.dumps(json_dict, indent=2))
    print()

    # Example 4: Generate JSON Schema
    print("4. schema() - Generate JSON Schema:")
    schema = type(settings).schema()
    print(json.dumps(schema, indent=2))
    print()

    # Example 5: Use schema for documentation
    print("5. Schema can be used for:")
    print("   ✓ API documentation generation")
    print("   ✓ Configuration validation")
    print("   ✓ IDE autocomplete")
    print("   ✓ Type checking tools")
    print()

    print("✅ Serialization complete!")
    print()
    print("💡 Tips:")
    print("   - Use model_dump() to convert to dict for logging")
    print("   - Use model_dump_json() for API responses")
    print("   - Use schema() to generate OpenAPI specs")


if __name__ == "__main__":
    main()
