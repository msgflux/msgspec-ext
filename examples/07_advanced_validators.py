"""Example demonstrating advanced validators.

This example shows advanced validators:
- IPv4Address, IPv6Address, IPvAnyAddress for IP validation
- MacAddress for MAC address validation
- ConStr for constrained strings
- ByteSize for storage size parsing
- PastDate, FutureDate for date validation
"""

import os
from datetime import date, timedelta

from msgspec_ext import (
    BaseSettings,
    ByteSize,
    ConStr,
    FutureDate,
    IPv4Address,
    IPv6Address,
    IPvAnyAddress,
    MacAddress,
    PastDate,
    SettingsConfigDict,
)


# Example 1: IP Address validation
class NetworkSettings(BaseSettings):
    """Settings with IP address validation."""

    model_config = SettingsConfigDict(env_prefix="NET_")

    server_ipv4: IPv4Address
    server_ipv6: IPv6Address
    proxy_ip: IPvAnyAddress  # Accepts both IPv4 and IPv6


# Example 2: MAC Address validation
class DeviceSettings(BaseSettings):
    """Settings with MAC address validation."""

    model_config = SettingsConfigDict(env_prefix="DEVICE_")

    primary_mac: MacAddress
    backup_mac: MacAddress


# Example 3: Constrained String validation
class UsernameSettings(BaseSettings):
    """Settings with constrained strings."""

    model_config = SettingsConfigDict(env_prefix="USER_")

    username: ConStr  # Can add min_length, max_length, pattern constraints


# Example 4: ByteSize validation
class StorageSettings(BaseSettings):
    """Settings with storage size validation."""

    model_config = SettingsConfigDict(env_prefix="STORAGE_")

    max_file_size: ByteSize
    cache_size: ByteSize
    upload_limit: ByteSize


# Example 5: Date validation
class EventSettings(BaseSettings):
    """Settings with date validation."""

    model_config = SettingsConfigDict(env_prefix="EVENT_")

    launch_date: FutureDate  # Must be in the future
    founding_date: PastDate  # Must be in the past


# Example 6: Combined advanced validators
class AppSettings(BaseSettings):
    """Real-world app settings with advanced validators."""

    # Network
    api_server: IPv4Address
    dns_server: IPvAnyAddress

    # MAC Address
    server_mac: MacAddress

    # Storage
    max_upload: ByteSize
    cache_limit: ByteSize

    # Dates
    release_date: FutureDate


def main():  # noqa: PLR0915
    print("=" * 60)
    print("msgspec-ext Advanced Validators Demo")
    print("=" * 60)

    # Example 1: IP Address validation
    print("\n1. IP Address Validation")
    print("-" * 60)

    os.environ.update(
        {
            "NET_SERVER_IPV4": "192.168.1.100",
            "NET_SERVER_IPV6": "2001:db8::1",
            "NET_PROXY_IP": "10.0.0.1",  # Can be IPv4 or IPv6
        }
    )

    net_settings = NetworkSettings()
    print(f"Server IPv4: {net_settings.server_ipv4}")
    print(f"Server IPv6: {net_settings.server_ipv6}")
    print(f"Proxy IP: {net_settings.proxy_ip}")

    # Try invalid IPv4
    try:
        IPv4Address("256.1.1.1")
    except ValueError as e:
        print(f"✓ IPv4 validation works: {e}")

    # Try invalid IPv6
    try:
        IPv6Address("gggg::1")
    except ValueError as e:
        print(f"✓ IPv6 validation works: {e}")

    # Example 2: MAC Address validation
    print("\n2. MAC Address Validation")
    print("-" * 60)

    os.environ.update(
        {
            "DEVICE_PRIMARY_MAC": "00:1B:44:11:3A:B7",
            "DEVICE_BACKUP_MAC": "001B.4411.3AB7",  # Different format
        }
    )

    device_settings = DeviceSettings()
    print(f"Primary MAC: {device_settings.primary_mac}")
    print(f"Backup MAC: {device_settings.backup_mac}")

    # Try invalid MAC
    try:
        MacAddress("GG:1B:44:11:3A:B7")
    except ValueError as e:
        print(f"✓ MAC validation works: {e}")

    # Example 3: Constrained String
    print("\n3. Constrained String Validation")
    print("-" * 60)

    # ConStr with no constraints
    username1 = ConStr("john_doe")
    print(f"Username (no constraints): {username1}")

    # ConStr with min/max length
    username2 = ConStr("alice", min_length=3, max_length=20)
    print(f"Username (with length): {username2}")

    # ConStr with pattern
    username3 = ConStr("bob123", pattern=r"^[a-z0-9]+$")
    print(f"Username (with pattern): {username3}")

    # Try too short
    try:
        ConStr("ab", min_length=5)
    except ValueError as e:
        print(f"✓ Min length validation works: {e}")

    # Try pattern mismatch
    try:
        ConStr("ABC", pattern=r"^[a-z]+$")
    except ValueError as e:
        print(f"✓ Pattern validation works: {e}")

    # Example 4: ByteSize validation
    print("\n4. Byte Size Validation")
    print("-" * 60)

    os.environ.update(
        {
            "STORAGE_MAX_FILE_SIZE": "10MB",
            "STORAGE_CACHE_SIZE": "500MB",
            "STORAGE_UPLOAD_LIMIT": "1GB",
        }
    )

    storage_settings = StorageSettings()
    print(f"Max File Size: {storage_settings.max_file_size} bytes = 10MB")
    print(f"Cache Size: {storage_settings.cache_size} bytes = 500MB")
    print(f"Upload Limit: {storage_settings.upload_limit} bytes = 1GB")

    # Different units
    print(f"\n1KB = {ByteSize('1KB')} bytes")
    print(f"1MB = {ByteSize('1MB')} bytes")
    print(f"1GB = {ByteSize('1GB')} bytes")
    print(f"1KiB = {ByteSize('1KiB')} bytes (binary)")
    print(f"1MiB = {ByteSize('1MiB')} bytes (binary)")

    # Try invalid size
    try:
        ByteSize("100XB")
    except ValueError as e:
        print(f"✓ ByteSize validation works: {e}")

    # Example 5: Date validation
    print("\n5. Past/Future Date Validation")
    print("-" * 60)

    yesterday = date.today() - timedelta(days=1)  # noqa: DTZ011
    tomorrow = date.today() + timedelta(days=1)  # noqa: DTZ011

    os.environ.update(
        {
            "EVENT_FOUNDING_DATE": yesterday.isoformat(),
            "EVENT_LAUNCH_DATE": tomorrow.isoformat(),
        }
    )

    event_settings = EventSettings()
    print(f"Founding Date (past): {event_settings.founding_date}")
    print(f"Launch Date (future): {event_settings.launch_date}")

    # Try future date as past (invalid)
    try:
        PastDate(tomorrow)
    except ValueError as e:
        print(f"✓ PastDate validation works: {e}")

    # Try past date as future (invalid)
    try:
        FutureDate(yesterday)
    except ValueError as e:
        print(f"✓ FutureDate validation works: {e}")

    # Example 6: Real-World Combined validators
    print("\n6. Real-World App Settings")
    print("-" * 60)

    os.environ.update(
        {
            "API_SERVER": "192.168.1.50",
            "DNS_SERVER": "8.8.8.8",
            "SERVER_MAC": "AA:BB:CC:DD:EE:FF",
            "MAX_UPLOAD": "50MB",
            "CACHE_LIMIT": "1GB",
            "RELEASE_DATE": tomorrow.isoformat(),
        }
    )

    app_settings = AppSettings()
    print(f"API Server: {app_settings.api_server}")
    print(f"DNS Server: {app_settings.dns_server}")
    print(f"Server MAC: {app_settings.server_mac}")
    print(f"Max Upload: {app_settings.max_upload} bytes")
    print(f"Cache Limit: {app_settings.cache_limit} bytes")
    print(f"Release Date: {app_settings.release_date}")

    print("\n" + "=" * 60)
    print("All advanced validator examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
