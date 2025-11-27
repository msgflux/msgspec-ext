"""
Using env_prefix to namespace environment variables.

This example shows how to use env_prefix to avoid naming conflicts
when multiple applications share the same environment.
"""

import os

from msgspec_ext import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database settings with DB_ prefix."""

    model_config = SettingsConfigDict(env_prefix="DB_")

    host: str = "localhost"
    port: int = 5432
    username: str = "admin"
    password: str = "secret"
    database: str = "myapp"


class RedisSettings(BaseSettings):
    """Redis settings with REDIS_ prefix."""

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = "localhost"
    port: int = 6379
    database: int = 0


def main():
    print("=" * 60)
    print("Example 2: Environment Variable Prefixes")
    print("=" * 60)
    print()

    # Set environment variables with different prefixes
    os.environ["DB_HOST"] = "db.example.com"
    os.environ["DB_PORT"] = "5433"
    os.environ["DB_USERNAME"] = "dbuser"
    os.environ["DB_PASSWORD"] = "dbpass123"
    os.environ["DB_DATABASE"] = "production"

    os.environ["REDIS_HOST"] = "redis.example.com"
    os.environ["REDIS_PORT"] = "6380"
    os.environ["REDIS_DATABASE"] = "1"

    try:
        # Load database settings
        db_settings = DatabaseSettings()
        print("Database Settings (DB_ prefix):")
        print(f"  Host: {db_settings.host}")
        print(f"  Port: {db_settings.port}")
        print(f"  Username: {db_settings.username}")
        print(f"  Password: {db_settings.password}")
        print(f"  Database: {db_settings.database}")
        print()

        # Load Redis settings
        redis_settings = RedisSettings()
        print("Redis Settings (REDIS_ prefix):")
        print(f"  Host: {redis_settings.host}")
        print(f"  Port: {redis_settings.port}")
        print(f"  Database: {redis_settings.database}")
        print()

        print("✅ Environment prefixes working correctly!")
        print()
        print("💡 Tip: Use prefixes to organize settings for different")
        print("   services in microservice architectures.")

    finally:
        # Clean up
        for key in [
            "DB_HOST",
            "DB_PORT",
            "DB_USERNAME",
            "DB_PASSWORD",
            "DB_DATABASE",
            "REDIS_HOST",
            "REDIS_PORT",
            "REDIS_DATABASE",
        ]:
            os.environ.pop(key, None)


if __name__ == "__main__":
    main()
