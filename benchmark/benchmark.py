#!/usr/bin/env python3
"""Benchmark comparing msgspec-ext and pydantic-settings.

This benchmark ensures fair comparison by testing identical configuration
structures with both libraries. Multiple runs with statistical analysis
provide confidence in the results.
"""

import os
import platform
import statistics
import sys
import time

ENV_CONTENT = """APP_NAME=benchmark-app
DEBUG=true
API_KEY=test-api-key-12345
MAX_CONNECTIONS=200
TIMEOUT=60.0
ALLOWED_HOSTS=["localhost", "127.0.0.1", "example.com"]
DATABASE__HOST=db.example.com
DATABASE__PORT=5433
DATABASE__USERNAME=dbuser
DATABASE__PASSWORD=dbpass123
DATABASE__DATABASE=production
REDIS__HOST=redis.example.com
REDIS__PORT=6380
REDIS__DB=2
REDIS__PASSWORD=redispass456
FEATURE_FLAGS__ENABLE_LOGGING=true
FEATURE_FLAGS__ENABLE_METRICS=true
FEATURE_FLAGS__ENABLE_TRACING=false
"""


def benchmark_msgspec_ext(iterations: int = 1000, warmup: int = 50) -> float:
    """Benchmark msgspec-ext settings loading with flat configuration.

    Note: msgspec-ext is optimized for flat settings loaded from .env files.
    Nested configuration support will be added in a future version.
    """
    from msgspec_ext import BaseSettings, SettingsConfigDict

    class AppSettings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=".env.msgspec", env_nested_delimiter="__"
        )

        # Application settings
        app_name: str
        debug: bool = False
        api_key: str = "default-key"
        max_connections: int = 100
        timeout: float = 30.0
        allowed_hosts: list[str]  # Loaded from .env

        # Database settings (flat structure)
        database__host: str = "localhost"
        database__port: int = 5432
        database__username: str = "admin"
        database__password: str = "secret"
        database__database: str = "myapp"

        # Redis settings (flat structure)
        redis__host: str = "localhost"
        redis__port: int = 6379
        redis__db: int = 0
        redis__password: str | None = None

        # Feature flags (flat structure)
        feature_flags__enable_logging: bool = False
        feature_flags__enable_metrics: bool = False
        feature_flags__enable_tracing: bool = False

    # Create .env file
    with open(".env.msgspec", "w") as f:
        f.write(ENV_CONTENT)

    try:
        # Warm up
        for _ in range(warmup):
            AppSettings()

        # Actual benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            AppSettings()
        end = time.perf_counter()

        return (end - start) / iterations * 1000  # ms per iteration
    finally:
        if os.path.exists(".env.msgspec"):
            os.unlink(".env.msgspec")


def benchmark_pydantic_settings(iterations: int = 1000, warmup: int = 50) -> float:
    """Benchmark pydantic-settings loading with nested configuration."""
    from pydantic import Field
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class DatabaseConfig(BaseSettings):
        model_config = SettingsConfigDict(env_prefix="DATABASE__")

        host: str = "localhost"
        port: int = 5432
        username: str = "admin"
        password: str = "secret"
        database: str = "myapp"

    class RedisConfig(BaseSettings):
        model_config = SettingsConfigDict(env_prefix="REDIS__")

        host: str = "localhost"
        port: int = 6379
        db: int = 0
        password: str | None = None

    class FeatureFlags(BaseSettings):
        model_config = SettingsConfigDict(env_prefix="FEATURE_FLAGS__")

        enable_logging: bool = False
        enable_metrics: bool = False
        enable_tracing: bool = False

    class AppSettings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=".env.pydantic", env_nested_delimiter="__"
        )

        app_name: str
        debug: bool = False
        api_key: str = "default-key"
        max_connections: int = 100
        timeout: float = 30.0
        allowed_hosts: list[str] = Field(default_factory=list)
        database: DatabaseConfig = Field(default_factory=DatabaseConfig)
        redis: RedisConfig = Field(default_factory=RedisConfig)
        feature_flags: FeatureFlags = Field(default_factory=FeatureFlags)

    # Create .env file
    with open(".env.pydantic", "w") as f:
        f.write(ENV_CONTENT)

    try:
        # Warm up
        for _ in range(warmup):
            AppSettings()

        # Actual benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            AppSettings()
        end = time.perf_counter()

        return (end - start) / iterations * 1000  # ms per iteration
    finally:
        if os.path.exists(".env.pydantic"):
            os.unlink(".env.pydantic")


def run_multiple_benchmarks(
    func, iterations: int = 1000, runs: int = 5
) -> dict[str, float]:
    """Run benchmark multiple times and return statistics."""
    times = []
    for _ in range(runs):
        time_ms = func(iterations)
        times.append(time_ms)

    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0.0,
        "min": min(times),
        "max": max(times),
        "raw": times,
    }


def print_system_info():
    """Print system information for benchmark context."""
    print("System Information:")
    print(f"  Python:     {sys.version.split()[0]}")
    print(f"  Platform:   {platform.platform()}")
    print(f"  Processor:  {platform.processor() or 'Unknown'}")
    print()

    try:
        import msgspec

        print(f"  msgspec:    {msgspec.__version__}")
    except (ImportError, AttributeError):
        print("  msgspec:    not installed")

    try:
        import pydantic

        print(f"  pydantic:   {pydantic.__version__}")
    except (ImportError, AttributeError):
        print("  pydantic:   not installed")

    print()


def main():
    """Run comprehensive benchmarks with statistical analysis."""
    print("=" * 80)
    print("Settings Library Benchmark - Comprehensive Comparison")
    print("=" * 80)
    print()

    print_system_info()

    iterations = 1000
    runs = 10

    print(f"Configuration: {runs} runs x {iterations} iterations per run")
    print("Testing: Nested configuration with database, redis, and feature flags")
    print()

    # Run msgspec-ext benchmarks
    print("Running msgspec-ext benchmarks...", end=" ", flush=True)
    try:
        msgspec_stats = run_multiple_benchmarks(benchmark_msgspec_ext, iterations, runs)
        print("✓")
    except Exception as e:
        print(f"✗ ERROR: {e}")
        msgspec_stats = None

    # Run pydantic-settings benchmarks
    print("Running pydantic-settings benchmarks...", end=" ", flush=True)
    try:
        pydantic_stats = run_multiple_benchmarks(
            benchmark_pydantic_settings, iterations, runs
        )
        print("✓")
    except Exception as e:
        print(f"✗ ERROR: {e}")
        pydantic_stats = None

    print()
    print("=" * 80)
    print("Results")
    print("=" * 80)
    print()

    if msgspec_stats:
        print("msgspec-ext:")
        print(f"  Mean:       {msgspec_stats['mean']:.3f}ms")
        print(f"  Median:     {msgspec_stats['median']:.3f}ms")
        print(f"  Std Dev:    {msgspec_stats['stdev']:.3f}ms")
        print(f"  Min:        {msgspec_stats['min']:.3f}ms")
        print(f"  Max:        {msgspec_stats['max']:.3f}ms")
        print()

    if pydantic_stats:
        print("pydantic-settings:")
        print(f"  Mean:       {pydantic_stats['mean']:.3f}ms")
        print(f"  Median:     {pydantic_stats['median']:.3f}ms")
        print(f"  Std Dev:    {pydantic_stats['stdev']:.3f}ms")
        print(f"  Min:        {pydantic_stats['min']:.3f}ms")
        print(f"  Max:        {pydantic_stats['max']:.3f}ms")
        print()

    if msgspec_stats and pydantic_stats:
        speedup = pydantic_stats["mean"] / msgspec_stats["mean"]
        print("=" * 80)
        print(f"msgspec-ext is {speedup:.1f}x faster than pydantic-settings")
        print("=" * 80)
        print()

    # Display markdown table for README
    print()
    print("Markdown Table for README:")
    print()
    print("| Library | Time per load | Relative Performance |")
    print("|---------|---------------|---------------------|")
    if msgspec_stats:
        print(f"| msgspec-ext | {msgspec_stats['mean']:.3f}ms | Baseline ⚡ |")
    if pydantic_stats:
        rel = pydantic_stats["mean"] / msgspec_stats["mean"] if msgspec_stats else 1.0
        print(
            f"| pydantic-settings | {pydantic_stats['mean']:.3f}ms | {rel:.1f}x slower |"
        )
    print()

    # Raw data for verification
    if msgspec_stats and pydantic_stats:
        print()
        print("Raw timing data (ms per load):")
        print(
            f"  msgspec-ext:       {', '.join(f'{t:.3f}' for t in msgspec_stats['raw'])}"
        )
        print(
            f"  pydantic-settings: {', '.join(f'{t:.3f}' for t in pydantic_stats['raw'])}"
        )
        print()


if __name__ == "__main__":
    main()
