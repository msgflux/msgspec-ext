#!/usr/bin/env python3
"""Benchmark cold start vs warm performance for both libraries."""

import os
import statistics
import subprocess
import sys
import time

ENV_CONTENT = """APP_NAME=test
DEBUG=true
API_KEY=key123
MAX_CONNECTIONS=100
TIMEOUT=30.0
DATABASE__HOST=localhost
DATABASE__PORT=5432
"""


def benchmark_msgspec_cold():
    """Measure msgspec cold start."""
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

start = time.perf_counter()
TestSettings()
end = time.perf_counter()
print((end - start) * 1000)
"""
    with open(".env.test", "w") as f:
        f.write(ENV_CONTENT)
    try:
        result = subprocess.run(
            ["uv", "run", "python", "-c", code],
            capture_output=True,
            text=True,
            check=True,
        )
        return float(result.stdout.strip())
    finally:
        if os.path.exists(".env.test"):
            os.unlink(".env.test")


def benchmark_pydantic_cold():
    """Measure pydantic cold start."""
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

    class Config:
        env_file = ".env.test"

start = time.perf_counter()
TestSettings()
end = time.perf_counter()
print((end - start) * 1000)
"""
    with open(".env.test", "w") as f:
        f.write(ENV_CONTENT)
    try:
        result = subprocess.run(
            ["uv", "run", "--with", "pydantic-settings", "python", "-c", code],
            capture_output=True,
            text=True,
            check=True,
        )
        return float(result.stdout.strip())
    finally:
        if os.path.exists(".env.test"):
            os.unlink(".env.test")


def benchmark_msgspec_warm(iterations=100):
    """Measure msgspec warm (cached)."""
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

    with open(".env.warm", "w") as f:
        f.write(ENV_CONTENT)

    try:
        TestSettings()  # Warmup
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            TestSettings()
            end = time.perf_counter()
            times.append((end - start) * 1000)
        return statistics.mean(times)
    finally:
        os.unlink(".env.warm")


def benchmark_pydantic_warm(iterations=100):
    """Measure pydantic warm."""
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

    class Config:
        env_file = ".env.pwarm"

TestSettings()  # Warmup
times = []
for _ in range({iterations}):
    start = time.perf_counter()
    TestSettings()
    end = time.perf_counter()
    times.append((end - start) * 1000)

print(statistics.mean(times))
"""
    try:
        result = subprocess.run(
            ["uv", "run", "--with", "pydantic-settings", "python", "-c", code],
            capture_output=True,
            text=True,
            check=True,
        )
        return float(result.stdout.strip())
    finally:
        if os.path.exists(".env.pwarm"):
            os.unlink(".env.pwarm")


if __name__ == "__main__":
    print("=" * 70)
    print("Cold Start vs Warm Performance Comparison")
    print("=" * 70)
    print()

    print("Benchmarking msgspec-ext...")
    msgspec_cold_times = [benchmark_msgspec_cold() for _ in range(3)]
    msgspec_cold = statistics.mean(msgspec_cold_times)
    msgspec_warm = benchmark_msgspec_warm(100)

    print("Benchmarking pydantic-settings...")
    pydantic_cold_times = [benchmark_pydantic_cold() for _ in range(3)]
    pydantic_cold = statistics.mean(pydantic_cold_times)
    pydantic_warm = benchmark_pydantic_warm(100)

    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    print(f"{'Library':<20} {'Cold Start':<15} {'Warm (Cached)':<15} {'Speedup':<10}")
    print("-" * 70)
    print(
        f"{'msgspec-ext':<20} {msgspec_cold:>8.3f}ms     {msgspec_warm:>8.3f}ms     {msgspec_cold / msgspec_warm:>6.1f}x"
    )
    print(
        f"{'pydantic-settings':<20} {pydantic_cold:>8.3f}ms     {pydantic_warm:>8.3f}ms     {pydantic_cold / pydantic_warm:>6.1f}x"
    )
    print()
    print("-" * 70)
    print("msgspec vs pydantic:")
    print(f"  Cold:  {pydantic_cold / msgspec_cold:.1f}x faster")
    print(f"  Warm:  {pydantic_warm / msgspec_warm:.1f}x faster")
    print()
