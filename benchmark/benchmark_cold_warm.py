#!/usr/bin/env python3
"""Benchmark cold start vs warm performance for both libraries.

This benchmark compares:
1. Cold start: Complete process initialization (realistic for serverless/CLI)
2. Warm: Cached in-process loading (realistic for long-running servers)

Methodology improvements:
- Multiple runs (5-10) for statistical significance
- Proper warmup for warm benchmarks (50 iterations)
- Higher iteration count for warm (1000 iterations)
- Statistical analysis (mean, median, stdev)
"""

import os
import statistics
import subprocess
import time

ENV_CONTENT = """APP_NAME=test
DEBUG=true
API_KEY=key123
MAX_CONNECTIONS=100
TIMEOUT=30.0
DATABASE__HOST=localhost
DATABASE__PORT=5432
REDIS__HOST=localhost
REDIS__PORT=6379
"""


def benchmark_msgspec_cold(runs=5):
    """Measure msgspec cold start with multiple runs."""
    code = """
import time
from msgspec_ext import BaseSettings, SettingsConfigDict

class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.test")
    app_name: str
    debug: bool = False
    api_key: str = "default"
    max_connections: int = 100
    timeout: float = 30.0
    database__host: str = "localhost"
    database__port: int = 5432
    redis__host: str = "localhost"
    redis__port: int = 6379

start = time.perf_counter()
TestSettings()
end = time.perf_counter()
print((end - start) * 1000)
"""
    with open(".env.test", "w") as f:
        f.write(ENV_CONTENT)

    times = []
    try:
        for _ in range(runs):
            result = subprocess.run(
                ["uv", "run", "python", "-c", code],
                capture_output=True,
                text=True,
                check=True,
            )
            times.append(float(result.stdout.strip()))

        return {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0.0,
            "min": min(times),
            "max": max(times),
            "raw": times,
        }
    finally:
        if os.path.exists(".env.test"):
            os.unlink(".env.test")


def benchmark_pydantic_cold(runs=5):
    """Measure pydantic cold start with multiple runs."""
    code = """
import time
from pydantic_settings import BaseSettings

class TestSettings(BaseSettings):
    app_name: str
    debug: bool = False
    api_key: str = "default"
    max_connections: int = 100
    timeout: float = 30.0
    database__host: str = "localhost"
    database__port: int = 5432
    redis__host: str = "localhost"
    redis__port: int = 6379

    class Config:
        env_file = ".env.test"

start = time.perf_counter()
TestSettings()
end = time.perf_counter()
print((end - start) * 1000)
"""
    with open(".env.test", "w") as f:
        f.write(ENV_CONTENT)

    times = []
    try:
        for _ in range(runs):
            result = subprocess.run(
                ["uv", "run", "--with", "pydantic-settings", "python", "-c", code],
                capture_output=True,
                text=True,
                check=True,
            )
            times.append(float(result.stdout.strip()))

        return {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0.0,
            "min": min(times),
            "max": max(times),
            "raw": times,
        }
    finally:
        if os.path.exists(".env.test"):
            os.unlink(".env.test")


def benchmark_msgspec_warm(iterations=1000, warmup=50, runs=10):
    """Measure msgspec warm (cached) with proper warmup and multiple runs."""
    from msgspec_ext import BaseSettings, SettingsConfigDict

    class TestSettings(BaseSettings):
        model_config = SettingsConfigDict(env_file=".env.warm")
        app_name: str
        debug: bool = False
        api_key: str = "default"
        max_connections: int = 100
        timeout: float = 30.0
        database__host: str = "localhost"
        database__port: int = 5432
        redis__host: str = "localhost"
        redis__port: int = 6379

    with open(".env.warm", "w") as f:
        f.write(ENV_CONTENT)

    try:
        # Warmup
        for _ in range(warmup):
            TestSettings()

        # Multiple runs
        run_times = []
        for _ in range(runs):
            start = time.perf_counter()
            for _ in range(iterations):
                TestSettings()
            end = time.perf_counter()
            run_times.append((end - start) / iterations * 1000)

        return {
            "mean": statistics.mean(run_times),
            "median": statistics.median(run_times),
            "stdev": statistics.stdev(run_times) if len(run_times) > 1 else 0.0,
            "min": min(run_times),
            "max": max(run_times),
            "raw": run_times,
        }
    finally:
        os.unlink(".env.warm")


def benchmark_pydantic_warm(iterations=1000, warmup=50, runs=10):
    """Measure pydantic warm with proper warmup and multiple runs."""
    code = f"""
import time
import statistics
from pydantic_settings import BaseSettings

ENV = '''{ENV_CONTENT}'''

with open('.env.pwarm', 'w') as f:
    f.write(ENV)

class TestSettings(BaseSettings):
    app_name: str
    debug: bool = False
    api_key: str = "default"
    max_connections: int = 100
    timeout: float = 30.0
    database__host: str = "localhost"
    database__port: int = 5432
    redis__host: str = "localhost"
    redis__port: int = 6379

    class Config:
        env_file = ".env.pwarm"

# Warmup
for _ in range({warmup}):
    TestSettings()

# Multiple runs
run_times = []
for _ in range({runs}):
    start = time.perf_counter()
    for _ in range({iterations}):
        TestSettings()
    end = time.perf_counter()
    run_times.append((end - start) / {iterations} * 1000)

# Output statistics
print(statistics.mean(run_times))
print(statistics.median(run_times))
print(statistics.stdev(run_times) if len(run_times) > 1 else 0.0)
print(min(run_times))
print(max(run_times))
"""
    try:
        result = subprocess.run(
            ["uv", "run", "--with", "pydantic-settings", "python", "-c", code],
            capture_output=True,
            text=True,
            check=True,
        )
        lines = result.stdout.strip().split("\n")
        return {
            "mean": float(lines[0]),
            "median": float(lines[1]),
            "stdev": float(lines[2]),
            "min": float(lines[3]),
            "max": float(lines[4]),
        }
    finally:
        if os.path.exists(".env.pwarm"):
            os.unlink(".env.pwarm")


def print_stats(label, stats, indent="  "):
    """Print statistics in a formatted way."""
    print(f"{indent}Mean:     {stats['mean']:>8.3f}ms")
    print(f"{indent}Median:   {stats['median']:>8.3f}ms")
    print(f"{indent}Std Dev:  {stats['stdev']:>8.3f}ms")
    print(f"{indent}Min:      {stats['min']:>8.3f}ms")
    print(f"{indent}Max:      {stats['max']:>8.3f}ms")


if __name__ == "__main__":
    print("=" * 80)
    print("Cold Start vs Warm Performance Comparison")
    print("=" * 80)
    print()
    print("Configuration:")
    print("  Cold: 5 process spawns (measures initialization overhead)")
    print("  Warm: 10 runs x 1000 iterations with 50 iteration warmup")
    print()

    # Cold benchmarks
    print("Running cold start benchmarks...")
    print("  msgspec-ext...", end=" ", flush=True)
    msgspec_cold = benchmark_msgspec_cold(runs=5)
    print("✓")

    print("  pydantic-settings...", end=" ", flush=True)
    pydantic_cold = benchmark_pydantic_cold(runs=5)
    print("✓")

    # Warm benchmarks
    print("Running warm (cached) benchmarks...")
    print("  msgspec-ext...", end=" ", flush=True)
    msgspec_warm = benchmark_msgspec_warm(iterations=1000, warmup=50, runs=10)
    print("✓")

    print("  pydantic-settings...", end=" ", flush=True)
    pydantic_warm = benchmark_pydantic_warm(iterations=1000, warmup=50, runs=10)
    print("✓")

    print()
    print("=" * 80)
    print("RESULTS - Cold Start (Process Initialization)")
    print("=" * 80)
    print()
    print("msgspec-ext:")
    print_stats("", msgspec_cold)
    print()
    print("pydantic-settings:")
    print_stats("", pydantic_cold)
    print()

    print("=" * 80)
    print("RESULTS - Warm (Cached, Long-Running Process)")
    print("=" * 80)
    print()
    print("msgspec-ext:")
    print_stats("", msgspec_warm)
    print()
    print("pydantic-settings:")
    print_stats("", pydantic_warm)
    print()

    print("=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print()

    cold_speedup = pydantic_cold["mean"] / msgspec_cold["mean"]
    warm_speedup = pydantic_warm["mean"] / msgspec_warm["mean"]

    print(f"{'Scenario':<30} {'msgspec-ext':<15} {'pydantic':<15} {'Advantage':<15}")
    print("-" * 80)
    print(
        f"{'Cold start (mean)':<30} {msgspec_cold['mean']:>8.3f}ms     {pydantic_cold['mean']:>8.3f}ms     {cold_speedup:>6.1f}x faster"
    )
    print(
        f"{'Warm cached (mean)':<30} {msgspec_warm['mean']:>8.3f}ms     {pydantic_warm['mean']:>8.3f}ms     {warm_speedup:>6.1f}x faster"
    )
    print()

    # Self-speedup (cold vs warm)
    msgspec_self_speedup = msgspec_cold["mean"] / msgspec_warm["mean"]
    pydantic_self_speedup = pydantic_cold["mean"] / pydantic_warm["mean"]

    print("Internal speedup (cold → warm caching benefit):")
    print(f"  msgspec-ext:       {msgspec_self_speedup:>6.1f}x faster when cached")
    print(f"  pydantic-settings: {pydantic_self_speedup:>6.1f}x faster when cached")
    print()

    print("Key insight:")
    if warm_speedup > cold_speedup * 1.5:
        print(
            f"  msgspec-ext caching is {warm_speedup / cold_speedup:.1f}x more effective than pydantic"
        )
    else:
        print("  Both libraries benefit from caching similarly")
    print()
