#!/usr/bin/env python3
"""Profile msgspec-ext to find bottlenecks."""

import cProfile
import os
import pstats

from msgspec_ext import BaseSettings, SettingsConfigDict

# Create test .env
with open(".env.profile", "w") as f:
    f.write("""APP_NAME=test
DEBUG=true
API_KEY=key123
MAX_CONNECTIONS=100
TIMEOUT=30.0
DATABASE__HOST=localhost
DATABASE__PORT=5432
REDIS__HOST=localhost
REDIS__PORT=6379
""")


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.profile", env_nested_delimiter="__"
    )

    app_name: str
    debug: bool = False
    api_key: str = "default"
    max_connections: int = 100
    timeout: float = 30.0
    database__host: str = "localhost"
    database__port: int = 5432
    redis__host: str = "localhost"
    redis__port: int = 6379


def profile_run():
    """Run 1000 iterations."""
    for _ in range(1000):
        TestSettings()


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    profile_run()
    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumulative")

    print("\n" + "=" * 80)
    print("TOP 20 FUNCTIONS BY CUMULATIVE TIME")
    print("=" * 80)
    stats.print_stats(20)

    print("\n" + "=" * 80)
    print("SETTINGS-RELATED FUNCTIONS")
    print("=" * 80)
    stats.print_stats("msgspec_ext")

    os.unlink(".env.profile")
