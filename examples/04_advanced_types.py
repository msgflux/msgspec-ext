"""
Advanced type handling with msgspec-ext.

This example shows how to use complex types like lists, dicts,
and optional fields in your settings.
"""

import os

from msgspec_ext import BaseSettings


class AdvancedSettings(BaseSettings):
    """Settings with advanced type annotations."""

    # Basic types
    app_name: str = "advanced-app"
    port: int = 8000

    # Optional types
    api_key: str | None = None
    timeout: float | None = None

    # List types
    allowed_hosts: list[str] | None = None
    ports: list[int] | None = None

    # Dict types
    feature_flags: dict | None = None


def main():
    print("=" * 60)
    print("Example 4: Advanced Type Handling")
    print("=" * 60)
    print()

    # Example 1: Using None defaults
    print("1. Optional fields (defaults to None):")
    settings1 = AdvancedSettings()
    print(f"   API Key: {settings1.api_key}")
    print(f"   Timeout: {settings1.timeout}")
    print(f"   Allowed Hosts: {settings1.allowed_hosts}")
    print()

    # Example 2: Loading lists from JSON env vars
    print("2. Loading lists from environment:")
    os.environ["ALLOWED_HOSTS"] = '["localhost", "127.0.0.1", "example.com"]'
    os.environ["PORTS"] = "[8000, 8001, 8002]"

    settings2 = AdvancedSettings()
    print(f"   Allowed Hosts: {settings2.allowed_hosts}")
    print(f"   Ports: {settings2.ports}")
    print()

    # Clean up
    os.environ.pop("ALLOWED_HOSTS", None)
    os.environ.pop("PORTS", None)

    # Example 3: Loading dicts from JSON env vars
    print("3. Loading dicts from environment:")
    os.environ["FEATURE_FLAGS"] = '{"new_ui": true, "beta_features": false, "max_upload_mb": 100}'

    settings3 = AdvancedSettings()
    print(f"   Feature Flags: {settings3.feature_flags}")
    if settings3.feature_flags:
        for key, value in settings3.feature_flags.items():
            print(f"     - {key}: {value}")
    print()

    # Clean up
    os.environ.pop("FEATURE_FLAGS", None)

    # Example 4: Explicit values with complex types
    print("4. Using explicit complex values:")
    settings4 = AdvancedSettings(
        app_name="explicit-app",
        api_key="sk-123456",
        timeout=30.5,
        allowed_hosts=["api.example.com", "cdn.example.com"],
        feature_flags={"debug": True, "cache_enabled": False},
    )
    print(f"   App Name: {settings4.app_name}")
    print(f"   API Key: {settings4.api_key}")
    print(f"   Timeout: {settings4.timeout}s")
    print(f"   Allowed Hosts: {settings4.allowed_hosts}")
    print(f"   Feature Flags: {settings4.feature_flags}")
    print()

    print("✅ Advanced types working correctly!")
    print()
    print("💡 Tip: Use JSON format in env vars for complex types:")
    print('   ALLOWED_HOSTS=\'["host1", "host2"]\'')
    print('   FEATURE_FLAGS=\'{"key": "value"}\'')


if __name__ == "__main__":
    main()
