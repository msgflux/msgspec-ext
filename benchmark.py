#!/usr/bin/env python3
"""Benchmark comparing msgspec-ext and pydantic-settings."""

import os
import time


# Test with msgspec-ext
def benchmark_msgspec_ext(iterations: int = 1000) -> float:
    """Benchmark msgspec-ext settings loading."""
    from msgspec_ext import BaseSettings, SettingsConfigDict

    class AppSettings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=".env.msgspec", env_nested_delimiter="__"
        )

        app_name: str
        debug: bool = False
        api_key: str = "default-key"
        max_connections: int = 100
        timeout: float = 30.0

    # Create .env file
    with open(".env.msgspec", "w") as f:
        f.write("""APP_NAME=benchmark-app
DEBUG=true
API_KEY=test-api-key-12345
MAX_CONNECTIONS=200
TIMEOUT=60.0
""")

    try:
        # Warm up
        for _ in range(10):
            settings = AppSettings()

        # Actual benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            settings = AppSettings()
        end = time.perf_counter()

        return (end - start) / iterations * 1000  # ms per iteration
    finally:
        if os.path.exists(".env.msgspec"):
            os.unlink(".env.msgspec")


def benchmark_pydantic_settings(iterations: int = 1000) -> float:
    """Benchmark pydantic-settings loading."""
    from pydantic import Field
    from pydantic_settings import BaseSettings

    class DatabaseConfig(BaseSettings):
        host: str = "localhost"
        port: int = 5432
        username: str = "admin"
        password: str = "secret"
        database: str = "myapp"

        class Config:
            env_prefix = "DATABASE__"

    class AppSettings(BaseSettings):
        app_name: str
        debug: bool = False
        api_key: str = "default-key"
        max_connections: int = 100
        timeout: float = 30.0
        allowed_hosts: list[str] = Field(default_factory=list)
        database: DatabaseConfig = Field(default_factory=DatabaseConfig)

        class Config:
            env_file = ".env.benchmark"
            env_nested_delimiter = "__"

    # Create .env file
    with open(".env.benchmark", "w") as f:
        f.write("""
APP_NAME=benchmark-app
DEBUG=true
API_KEY=test-api-key-12345
MAX_CONNECTIONS=200
TIMEOUT=60.0
ALLOWED_HOSTS=["localhost", "127.0.0.1"]
DATABASE__HOST=db.example.com
DATABASE__PORT=5433
DATABASE__USERNAME=dbuser
DATABASE__PASSWORD=dbpass123
DATABASE__DATABASE=production
""")

    try:
        # Warm up
        for _ in range(10):
            settings = AppSettings()

        # Actual benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            settings = AppSettings()
        end = time.perf_counter()

        return (end - start) / iterations * 1000  # ms per iteration
    finally:
        if os.path.exists(".env.benchmark"):
            os.unlink(".env.benchmark")




def main():
    """Run benchmarks and display results."""
    print("=" * 70)
    print("Settings Library Benchmark Comparison")
    print("=" * 70)
    print()
    print("Running benchmarks (1000 iterations each)...")
    print()

    # Run benchmarks
    try:
        print("⏱  msgspec-ext...", end=" ", flush=True)
        msgspec_time = benchmark_msgspec_ext()
        print(f"{msgspec_time:.3f}ms")
    except Exception as e:
        print(f"ERROR: {e}")
        msgspec_time = None

    try:
        print("⏱  pydantic-settings...", end=" ", flush=True)
        pydantic_time = benchmark_pydantic_settings()
        print(f"{pydantic_time:.3f}ms")
    except Exception as e:
        print(f"ERROR: {e}")
        pydantic_time = None

    print()
    print("=" * 70)
    print("Results Summary")
    print("=" * 70)
    print()

    if msgspec_time:
        print(f"msgspec-ext:        {msgspec_time:.3f}ms per load")
    if pydantic_time:
        print(f"pydantic-settings:  {pydantic_time:.3f}ms per load")

    print()

    if msgspec_time and pydantic_time:
        speedup = pydantic_time / msgspec_time
        print(f"msgspec-ext is {speedup:.1f}x faster than pydantic-settings")

    print()
    print("=" * 70)

    # Display as markdown table
    print()
    print("Markdown Table for README:")
    print()
    print("| Library | Time per load | Relative Performance |")
    print("|---------|---------------|---------------------|")
    if msgspec_time:
        print(f"| msgspec-ext | {msgspec_time:.3f}ms | 1.0x (baseline) |")
    if pydantic_time:
        rel = pydantic_time / msgspec_time if msgspec_time else 1.0
        print(f"| pydantic-settings | {pydantic_time:.3f}ms | {rel:.1f}x slower |")
    print()


if __name__ == "__main__":
    main()
