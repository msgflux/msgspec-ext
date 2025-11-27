"""
Loading settings from .env files.

This example shows how to load settings from .env files,
which is useful for local development and deployment.
"""

import tempfile
from pathlib import Path

from msgspec_ext import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application settings loaded from .env file."""

    model_config = SettingsConfigDict(
        env_file=".env.example", env_file_encoding="utf-8"
    )

    app_name: str
    environment: str = "development"
    api_key: str
    database_url: str
    max_connections: int = 100
    enable_logging: bool = True


def main():
    print("=" * 60)
    print("Example 3: Loading from .env Files")
    print("=" * 60)
    print()

    # Create a temporary .env file
    env_content = """# Application Configuration
APP_NAME=my-awesome-app
ENVIRONMENT=production
API_KEY=sk-1234567890abcdef
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
MAX_CONNECTIONS=200
ENABLE_LOGGING=false
"""

    env_file = Path(".env.example")
    env_file.write_text(env_content)

    try:
        print("Created .env.example file:")
        print("-" * 60)
        print(env_content)
        print("-" * 60)
        print()

        # Load settings from .env file
        settings = AppSettings()

        print("Loaded Settings:")
        print(f"  App Name: {settings.app_name}")
        print(f"  Environment: {settings.environment}")
        print(f"  API Key: {settings.api_key}")
        print(f"  Database URL: {settings.database_url}")
        print(f"  Max Connections: {settings.max_connections}")
        print(f"  Enable Logging: {settings.enable_logging}")
        print()

        print("✅ Settings loaded from .env file!")
        print()
        print("💡 Tips:")
        print("   - Use .env.local for local overrides (add to .gitignore)")
        print("   - Use .env.production for production settings")
        print("   - Never commit secrets to version control")

    finally:
        # Clean up
        env_file.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
