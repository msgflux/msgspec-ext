"""Integration tests for validators with BaseSettings.

Tests that all custom validator types work correctly when used with BaseSettings,
ensuring proper environment variable parsing and validation.
"""

import os
import tempfile
from datetime import date, timedelta

import pytest

from msgspec_ext import (
    AnyUrl,
    BaseSettings,
    ByteSize,
    DirectoryPath,
    EmailStr,
    FilePath,
    FutureDate,
    HttpUrl,
    IPv4Address,
    IPv6Address,
    IPvAnyAddress,
    MacAddress,
    NegativeFloat,
    NegativeInt,
    NonNegativeFloat,
    NonNegativeInt,
    NonPositiveFloat,
    NonPositiveInt,
    PastDate,
    PaymentCardNumber,
    PositiveFloat,
    PositiveInt,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    SettingsConfigDict,
)


class TestNumericTypesIntegration:
    """Integration tests for numeric validators with BaseSettings."""

    def test_positive_int_from_env(self):
        """PositiveInt should work with environment variables."""

        class Settings(BaseSettings):
            port: PositiveInt

        os.environ["PORT"] = "8080"
        settings = Settings()
        assert settings.port == 8080

    def test_negative_int_from_env(self):
        """NegativeInt should work with environment variables."""

        class Settings(BaseSettings):
            offset: NegativeInt

        os.environ["OFFSET"] = "-10"
        settings = Settings()
        assert settings.offset == -10

    def test_positive_float_from_env(self):
        """PositiveFloat should work with environment variables."""

        class Settings(BaseSettings):
            rate: PositiveFloat

        os.environ["RATE"] = "1.5"
        settings = Settings()
        assert settings.rate == 1.5


class TestStringValidatorsIntegration:
    """Integration tests for string validators with BaseSettings."""

    def test_email_from_env(self):
        """EmailStr should validate from environment variables."""

        class Settings(BaseSettings):
            email: EmailStr

        os.environ["EMAIL"] = "admin@example.com"
        settings = Settings()
        assert str(settings.email) == "admin@example.com"

    def test_http_url_from_env(self):
        """HttpUrl should validate from environment variables."""

        class Settings(BaseSettings):
            api_url: HttpUrl

        os.environ["API_URL"] = "https://api.example.com"
        settings = Settings()
        assert str(settings.api_url) == "https://api.example.com"

    def test_secret_str_from_env(self):
        """SecretStr should mask value when printed."""

        class Settings(BaseSettings):
            api_key: SecretStr

        os.environ["API_KEY"] = "secret123"
        settings = Settings()
        assert str(settings.api_key) == "**********"
        assert settings.api_key.get_secret_value() == "secret123"


class TestDatabaseDsnIntegration:
    """Integration tests for DSN validators with BaseSettings."""

    def test_postgres_dsn_from_env(self):
        """PostgresDsn should validate from environment variables."""

        class Settings(BaseSettings):
            database_url: PostgresDsn

        os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
        settings = Settings()
        assert str(settings.database_url).startswith("postgresql://")

    def test_redis_dsn_from_env(self):
        """RedisDsn should validate from environment variables."""

        class Settings(BaseSettings):
            redis_url: RedisDsn

        os.environ["REDIS_URL"] = "redis://localhost:6379/0"
        settings = Settings()
        assert str(settings.redis_url).startswith("redis://")


class TestPathValidatorsIntegration:
    """Integration tests for path validators with BaseSettings."""

    def test_file_path_from_env(self, tmp_path):
        """FilePath should validate existing files from env."""

        class Settings(BaseSettings):
            config_file: FilePath

        test_file = tmp_path / "config.txt"
        test_file.write_text("test")

        os.environ["CONFIG_FILE"] = str(test_file)
        settings = Settings()
        assert str(settings.config_file) == str(test_file)

    def test_directory_path_from_env(self, tmp_path):
        """DirectoryPath should validate existing directories from env."""

        class Settings(BaseSettings):
            data_dir: DirectoryPath

        os.environ["DATA_DIR"] = str(tmp_path)
        settings = Settings()
        assert str(settings.data_dir) == str(tmp_path)


class TestNetworkValidatorsIntegration:
    """Integration tests for network validators with BaseSettings."""

    def test_ipv4_from_env(self):
        """IPv4Address should validate from environment variables."""

        class Settings(BaseSettings):
            server_ip: IPv4Address

        os.environ["SERVER_IP"] = "192.168.1.100"
        settings = Settings()
        assert str(settings.server_ip) == "192.168.1.100"

    def test_ipv6_from_env(self):
        """IPv6Address should validate from environment variables."""

        class Settings(BaseSettings):
            server_ipv6: IPv6Address

        os.environ["SERVER_IPV6"] = "::1"
        settings = Settings()
        assert str(settings.server_ipv6) == "::1"

    def test_ipvany_from_env(self):
        """IPvAnyAddress should accept both IPv4 and IPv6."""

        class Settings(BaseSettings):
            proxy_ip: IPvAnyAddress

        # Test IPv4
        os.environ["PROXY_IP"] = "10.0.0.1"
        settings = Settings()
        assert str(settings.proxy_ip) == "10.0.0.1"

        # Test IPv6
        os.environ["PROXY_IP"] = "2001:db8::1"
        settings = Settings()
        assert str(settings.proxy_ip) == "2001:db8::1"

    def test_mac_address_from_env(self):
        """MacAddress should validate from environment variables."""

        class Settings(BaseSettings):
            device_mac: MacAddress

        os.environ["DEVICE_MAC"] = "AA:BB:CC:DD:EE:FF"
        settings = Settings()
        assert str(settings.device_mac) == "AA:BB:CC:DD:EE:FF"


class TestStorageAndDateValidatorsIntegration:
    """Integration tests for storage and date validators with BaseSettings."""

    def test_bytesize_from_env(self):
        """ByteSize should parse storage units from environment variables."""

        class Settings(BaseSettings):
            max_upload: ByteSize
            cache_size: ByteSize

        os.environ["MAX_UPLOAD"] = "10MB"
        os.environ["CACHE_SIZE"] = "1GB"
        settings = Settings()
        assert int(settings.max_upload) == 10 * 1000**2
        assert int(settings.cache_size) == 1000**3

    def test_past_date_from_env(self):
        """PastDate should validate from environment variables."""

        class Settings(BaseSettings):
            founding_date: PastDate

        yesterday = date.today() - timedelta(days=1)
        os.environ["FOUNDING_DATE"] = yesterday.isoformat()
        settings = Settings()
        assert settings.founding_date == yesterday

    def test_future_date_from_env(self):
        """FutureDate should validate from environment variables."""

        class Settings(BaseSettings):
            launch_date: FutureDate

        tomorrow = date.today() + timedelta(days=1)
        os.environ["LAUNCH_DATE"] = tomorrow.isoformat()
        settings = Settings()
        assert settings.launch_date == tomorrow


class TestCompleteIntegration:
    """Integration test with all validator types combined."""

    def test_all_validators_together(self, tmp_path):
        """All validators should work together in one settings class."""

        class AppSettings(BaseSettings):
            # Numeric
            port: PositiveInt
            max_connections: NonNegativeInt
            timeout: PositiveFloat

            # String validators
            admin_email: EmailStr
            api_url: HttpUrl
            api_key: SecretStr

            # Network
            server_ip: IPv4Address
            device_mac: MacAddress

            # Storage & Dates
            max_upload: ByteSize
            founding_date: PastDate

        # Create temp file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        yesterday = date.today() - timedelta(days=1)

        os.environ.update(
            {
                "PORT": "8000",
                "MAX_CONNECTIONS": "100",
                "TIMEOUT": "30.5",
                "ADMIN_EMAIL": "admin@example.com",
                "API_URL": "https://api.example.com",
                "API_KEY": "secret123",
                "SERVER_IP": "192.168.1.1",
                "DEVICE_MAC": "AA:BB:CC:DD:EE:FF",
                "MAX_UPLOAD": "50MB",
                "FOUNDING_DATE": yesterday.isoformat(),
            }
        )

        settings = AppSettings()

        # Verify all fields
        assert settings.port == 8000
        assert settings.max_connections == 100
        assert settings.timeout == 30.5
        assert str(settings.admin_email) == "admin@example.com"
        assert str(settings.api_url) == "https://api.example.com"
        assert settings.api_key.get_secret_value() == "secret123"
        assert str(settings.server_ip) == "192.168.1.1"
        assert str(settings.device_mac) == "AA:BB:CC:DD:EE:FF"
        assert int(settings.max_upload) == 50 * 1000**2
        assert settings.founding_date == yesterday
