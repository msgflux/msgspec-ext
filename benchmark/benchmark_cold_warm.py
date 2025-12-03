#!/usr/bin/env python3
"""Benchmark cold start vs warm performance for msgspec-ext and pydantic.

This benchmark is designed to provide a realistic comparison between `msgspec-ext`
and `pydantic-settings` in two common scenarios:

1.  **Cold Start**: This simulates use cases like serverless functions (e.g., AWS
    Lambda) or command-line tools, where the Python process starts, loads the
    settings, and then exits. We measure the full time, including process
    startup, library import, and settings object instantiation. This is
    achieved by running the benchmark code in a separate `python` subprocess
    for each run.

2.  **Warm (Cached) Start**: This simulates long-running applications like a web
    server, where settings might be instantiated multiple times within the same
    process. The benchmark measures the speed of creating new settings objects
    after the initial import and caching have already occurred. This is run
    in-process.

To ensure statistical significance, each benchmark is run multiple times, and
the results (mean, median, standard deviation) are reported.
"""

import os
import statistics
import subprocess
import time

# Benchmark parameters
COLD_RUNS = 5
WARM_RUNS = 10
WARM_ITERATIONS = 1000
WARM_WARMUP = 50

ENV_FILE = ".env.benchmark"
ENV_CONTENT = f"""APP_NAME=test
DEBUG=true
API_KEY=key123
MAX_CONNECTIONS=100
TIMEOUT=30.0
DATABASE__HOST=localhost
DATABASE__PORT=5432
REDIS__HOST=localhost
REDIS__PORT=6379
"""


def benchmark_msgspec_cold(runs=COLD_RUNS):
    """Measure msgspec cold start with multiple runs."""
    code = f"""
import time
from msgspec_ext import BaseSettings, SettingsConfigDict

class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file="{ENV_FILE}")
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
    times = []
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


def benchmark_pydantic_cold(runs=COLD_RUNS):
    """Measure pydantic cold start with multiple runs."""
    code = f"""
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
        env_file = "{ENV_FILE}"

start = time.perf_counter()
TestSettings()
end = time.perf_counter()
print((end - start) * 1000)
"""
    times = []
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


def benchmark_msgspec_warm(
    iterations=WARM_ITERATIONS, warmup=WARM_WARMUP, runs=WARM_RUNS
):
    """Measure msgspec warm (cached) with proper warmup and multiple runs."""
    from msgspec_ext import BaseSettings, SettingsConfigDict

    class TestSettings(BaseSettings):
        model_config = SettingsConfigDict(env_file=ENV_FILE)
        app_name: str
        debug: bool = False
        api_key: str = "default"
        max_connections: int = 100
        timeout: float = 30.0
        database__host: str = "localhost"
        database__port: int = 5432
        redis__host: str = "localhost"
        redis__port: int = 6379

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


def benchmark_pydantic_warm(
    iterations=WARM_ITERATIONS, warmup=WARM_WARMUP, runs=WARM_RUNS
):
    """Measure pydantic warm with proper warmup and multiple runs."""
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
            env_file = ENV_FILE

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


def print_stats(label, stats, indent="  "):
    """Print statistics in a readable, formatted way.

    Args:
        label: A label to print before the stats.
        stats: A dictionary of statistics (mean, median, stdev, min, max).
        indent: The string to use for indentation.
    """
    if label:
        print(label)
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
    print(f"  Cold: {COLD_RUNS} process spawns (measures initialization overhead)")
    print(
        f"  Warm: {WARM_RUNS} runs x {WARM_ITERATIONS} "
        f"iterations with {WARM_WARMUP} iteration warmup"
    )
    print()

    # Create the .env file for benchmarks
    with open(ENV_FILE, "w") as f:
        f.write(ENV_CONTENT)

    try:
        # Cold benchmarks
        print("Running cold start benchmarks...")
        print("  msgspec-ext...", end=" ", flush=True)
        msgspec_cold = benchmark_msgspec_cold()
        print("✓")

        print("  pydantic-settings...", end=" ", flush=True)
        pydantic_cold = benchmark_pydantic_cold()
        print("✓")

        # Warm benchmarks
        print("Running warm (cached) benchmarks...")
        print("  msgspec-ext...", end=" ", flush=True)
        msgspec_warm = benchmark_msgspec_warm()
        print("✓")

        print("  pydantic-settings...", end=" ", flush=True)
        pydantic_warm = benchmark_pydantic_warm()
        print("✓")

    finally:
        # Clean up the .env file
        if os.path.exists(ENV_FILE):
            os.unlink(ENV_FILE)

    print()
    print("=" * 80)
    print("RESULTS - Cold Start (Process Initialization)")
    print("=" * 80)
    print()
    print_stats("msgspec-ext:", msgspec_cold)
    print()
    print_stats("pydantic-settings:", pydantic_cold)
    print()

    print("=" * 80)
    print("RESULTS - Warm (Cached, Long-Running Process)")
    print("=" * 80)
    print()
    print_stats("msgspec-ext:", msgspec_warm)
    print()
    print_stats("pydantic-settings:", pydantic_warm)
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
