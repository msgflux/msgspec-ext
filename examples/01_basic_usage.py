"""
Basic usage of msgspec-ext for settings management.

This example shows the simplest use case: defining settings with defaults
and loading from environment variables.
"""

import os

from msgspec_ext import BaseSettings


class AppSettings(BaseSettings):
    """Application settings with sensible defaults."""

    app_name: str = "my-app"
    debug: bool = False
    port: int = 8000
    host: str = "0.0.0.0"


def main():
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    print()

    # Create settings with defaults
    print("1. Using defaults:")
    settings = AppSettings()
    print(f"   App Name: {settings.app_name}")
    print(f"   Debug: {settings.debug}")
    print(f"   Port: {settings.port}")
    print(f"   Host: {settings.host}")
    print()

    # Override with environment variables
    print("2. Override with environment variables:")
    os.environ["APP_NAME"] = "production-app"
    os.environ["PORT"] = "9000"
    os.environ["DEBUG"] = "true"

    settings2 = AppSettings()
    print(f"   App Name: {settings2.app_name}")
    print(f"   Debug: {settings2.debug}")
    print(f"   Port: {settings2.port}")
    print(f"   Host: {settings2.host}")
    print()

    # Clean up
    os.environ.pop("APP_NAME", None)
    os.environ.pop("PORT", None)
    os.environ.pop("DEBUG", None)

    # Override with explicit values
    print("3. Override with explicit values:")
    settings3 = AppSettings(app_name="test-app", port=3000, debug=True)
    print(f"   App Name: {settings3.app_name}")
    print(f"   Debug: {settings3.debug}")
    print(f"   Port: {settings3.port}")
    print()

    print("✅ Basic usage complete!")


if __name__ == "__main__":
    main()
