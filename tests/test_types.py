"""Tests for custom types and validators in msgspec_ext.types."""

from datetime import date, timedelta

import pytest

from msgspec_ext.types import (
    AnyUrl,
    ByteSize,
    ConStr,
    DirectoryPath,
    EmailStr,
    FilePath,
    FutureDate,
    HttpUrl,
    IPv4Address,
    IPv6Address,
    IPvAnyAddress,
    Json,
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
)

# ==============================================================================
# Numeric Type Tests
# ==============================================================================


class TestPositiveInt:
    """Tests for PositiveInt type."""

    def test_valid_positive_integers(self):
        """Should accept positive integers."""
        import msgspec

        assert msgspec.json.decode(b"1", type=PositiveInt) == 1
        assert msgspec.json.decode(b"100", type=PositiveInt) == 100
        assert msgspec.json.decode(b"999999", type=PositiveInt) == 999999

    def test_reject_zero(self):
        """Should reject zero (not strictly positive)."""
        import msgspec

        with pytest.raises(msgspec.ValidationError, match="Expected `int` >= 1"):
            msgspec.json.decode(b"0", type=PositiveInt)

    def test_reject_negative(self):
        """Should reject negative integers."""
        import msgspec

        with pytest.raises(msgspec.ValidationError):
            msgspec.json.decode(b"-1", type=PositiveInt)
        with pytest.raises(msgspec.ValidationError):
            msgspec.json.decode(b"-100", type=PositiveInt)


class TestNegativeInt:
    """Tests for NegativeInt type."""

    def test_valid_negative_integers(self):
        """Should accept negative integers."""
        import msgspec

        assert msgspec.json.decode(b"-1", type=NegativeInt) == -1
        assert msgspec.json.decode(b"-100", type=NegativeInt) == -100

    def test_reject_zero(self):
        """Should reject zero (not strictly negative)."""
        import msgspec

        with pytest.raises(msgspec.ValidationError):
            msgspec.json.decode(b"0", type=NegativeInt)

    def test_reject_positive(self):
        """Should reject positive integers."""
        import msgspec

        with pytest.raises(msgspec.ValidationError):
            msgspec.json.decode(b"1", type=NegativeInt)


class TestNonNegativeInt:
    """Tests for NonNegativeInt type."""

    def test_valid_non_negative_integers(self):
        """Should accept zero and positive integers."""
        import msgspec

        assert msgspec.json.decode(b"0", type=NonNegativeInt) == 0
        assert msgspec.json.decode(b"1", type=NonNegativeInt) == 1
        assert msgspec.json.decode(b"100", type=NonNegativeInt) == 100

    def test_reject_negative(self):
        """Should reject negative integers."""
        import msgspec

        with pytest.raises(msgspec.ValidationError):
            msgspec.json.decode(b"-1", type=NonNegativeInt)


class TestNonPositiveInt:
    """Tests for NonPositiveInt type."""

    def test_valid_non_positive_integers(self):
        """Should accept zero and negative integers."""
        import msgspec

        assert msgspec.json.decode(b"0", type=NonPositiveInt) == 0
        assert msgspec.json.decode(b"-1", type=NonPositiveInt) == -1
        assert msgspec.json.decode(b"-100", type=NonPositiveInt) == -100

    def test_reject_positive(self):
        """Should reject positive integers."""
        import msgspec

        with pytest.raises(msgspec.ValidationError):
            msgspec.json.decode(b"1", type=NonPositiveInt)


class TestPositiveFloat:
    """Tests for PositiveFloat type."""

    def test_valid_positive_floats(self):
        """Should accept positive floats."""
        import msgspec

        assert msgspec.json.decode(b"0.1", type=PositiveFloat) == 0.1
        assert msgspec.json.decode(b"1.0", type=PositiveFloat) == 1.0
        assert msgspec.json.decode(b"99.99", type=PositiveFloat) == 99.99

    def test_reject_zero(self):
        """Should reject zero (not strictly positive)."""
        import msgspec

        with pytest.raises(msgspec.ValidationError):
            msgspec.json.decode(b"0.0", type=PositiveFloat)

    def test_reject_negative(self):
        """Should reject negative floats."""
        import msgspec

        with pytest.raises(msgspec.ValidationError):
            msgspec.json.decode(b"-0.1", type=PositiveFloat)


class TestNegativeFloat:
    """Tests for NegativeFloat type."""

    def test_valid_negative_floats(self):
        """Should accept negative floats."""
        import msgspec

        assert msgspec.json.decode(b"-0.1", type=NegativeFloat) == -0.1
        assert msgspec.json.decode(b"-99.99", type=NegativeFloat) == -99.99

    def test_reject_zero(self):
        """Should reject zero (not strictly negative)."""
        import msgspec

        with pytest.raises(msgspec.ValidationError):
            msgspec.json.decode(b"0.0", type=NegativeFloat)

    def test_reject_positive(self):
        """Should reject positive floats."""
        import msgspec

        with pytest.raises(msgspec.ValidationError):
            msgspec.json.decode(b"0.1", type=NegativeFloat)


class TestNonNegativeFloat:
    """Tests for NonNegativeFloat type."""

    def test_valid_non_negative_floats(self):
        """Should accept zero and positive floats."""
        import msgspec

        assert msgspec.json.decode(b"0.0", type=NonNegativeFloat) == 0.0
        assert msgspec.json.decode(b"0.1", type=NonNegativeFloat) == 0.1
        assert msgspec.json.decode(b"99.99", type=NonNegativeFloat) == 99.99

    def test_reject_negative(self):
        """Should reject negative floats."""
        import msgspec

        with pytest.raises(msgspec.ValidationError):
            msgspec.json.decode(b"-0.1", type=NonNegativeFloat)


class TestNonPositiveFloat:
    """Tests for NonPositiveFloat type."""

    def test_valid_non_positive_floats(self):
        """Should accept zero and negative floats."""
        import msgspec

        assert msgspec.json.decode(b"0.0", type=NonPositiveFloat) == 0.0
        assert msgspec.json.decode(b"-0.1", type=NonPositiveFloat) == -0.1
        assert msgspec.json.decode(b"-99.99", type=NonPositiveFloat) == -99.99

    def test_reject_positive(self):
        """Should reject positive floats."""
        import msgspec

        with pytest.raises(msgspec.ValidationError):
            msgspec.json.decode(b"0.1", type=NonPositiveFloat)


# ==============================================================================
# EmailStr Tests
# ==============================================================================


class TestEmailStr:
    """Tests for EmailStr type."""

    def test_valid_emails(self):
        """Should accept valid email formats."""
        valid_emails = [
            "user@example.com",
            "test.user@example.com",
            "user+tag@example.co.uk",
            "user123@test-domain.com",
            "a@b.co",
        ]
        for email in valid_emails:
            result = EmailStr(email)
            assert str(result) == email.strip()

    def test_email_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        assert str(EmailStr("  user@example.com  ")) == "user@example.com"

    def test_reject_invalid_emails(self):
        """Should reject invalid email formats."""
        invalid_emails = [
            "",
            "not-an-email",
            "@example.com",
            "user@",
            "user @example.com",
            "user@.com",
            "user@domain",
            "a" * 321,  # Too long (> 320 chars)
        ]
        for email in invalid_emails:
            with pytest.raises(ValueError):
                EmailStr(email)

    def test_email_too_short(self):
        """Should reject emails shorter than 3 characters."""
        with pytest.raises(ValueError, match="at least 3 characters"):
            EmailStr("a@")

    def test_email_too_long(self):
        """Should reject emails longer than 320 characters."""
        long_email = "a" * 310 + "@example.com"  # 310 + 12 = 322 chars
        with pytest.raises(ValueError, match="at most 320 characters"):
            EmailStr(long_email)

    def test_email_type_error(self):
        """Should reject non-string inputs."""
        with pytest.raises(TypeError):
            EmailStr(123)  # type: ignore


# ==============================================================================
# HttpUrl Tests
# ==============================================================================


class TestHttpUrl:
    """Tests for HttpUrl type."""

    def test_valid_http_urls(self):
        """Should accept valid HTTP URLs."""
        valid_urls = [
            "http://example.com",
            "https://example.com",
            "http://example.com/path",
            "https://example.com/path?query=value",
            "http://subdomain.example.com:8080/path",
        ]
        for url in valid_urls:
            result = HttpUrl(url)
            assert str(result) == url.strip()

    def test_url_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        assert str(HttpUrl("  https://example.com  ")) == "https://example.com"

    def test_reject_non_http_schemes(self):
        """Should reject non-HTTP/HTTPS schemes."""
        invalid_urls = [
            "ftp://example.com",
            "ws://example.com",
            "file:///path/to/file",
        ]
        for url in invalid_urls:
            with pytest.raises(ValueError):
                HttpUrl(url)

    def test_reject_invalid_urls(self):
        """Should reject invalid URL formats."""
        invalid_urls = [
            "",
            "not a url",
            "http://",
            "://example.com",
        ]
        for url in invalid_urls:
            with pytest.raises(ValueError):
                HttpUrl(url)

    def test_url_too_long(self):
        """Should reject URLs longer than 2083 characters."""
        long_url = "http://example.com/" + "a" * 2100
        with pytest.raises(ValueError, match="at most 2083 characters"):
            HttpUrl(long_url)

    def test_url_type_error(self):
        """Should reject non-string inputs."""
        with pytest.raises(TypeError):
            HttpUrl(123)  # type: ignore


# ==============================================================================
# AnyUrl Tests
# ==============================================================================


class TestAnyUrl:
    """Tests for AnyUrl type."""

    def test_valid_any_urls(self):
        """Should accept URLs with any valid scheme."""
        valid_urls = [
            "http://example.com",
            "https://example.com",
            "ftp://ftp.example.com",
            "ws://websocket.example.com",
            "wss://secure.websocket.com",
            "file:///path/to/file",
            "mailto:user@example.com",
        ]
        for url in valid_urls:
            result = AnyUrl(url)
            assert str(result) == url.strip()

    def test_url_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        assert str(AnyUrl("  ftp://example.com  ")) == "ftp://example.com"

    def test_reject_invalid_urls(self):
        """Should reject invalid URL formats."""
        invalid_urls = [
            "",
            "not a url",
            "://example.com",
            "http//example.com",  # Missing colon
        ]
        for url in invalid_urls:
            with pytest.raises(ValueError):
                AnyUrl(url)

    def test_url_type_error(self):
        """Should reject non-string inputs."""
        with pytest.raises(TypeError):
            AnyUrl(123)  # type: ignore


# ==============================================================================
# SecretStr Tests
# ==============================================================================


class TestSecretStr:
    """Tests for SecretStr type."""

    def test_create_secret(self):
        """Should create secret string from regular string."""
        secret = SecretStr("my-secret-password")
        assert isinstance(secret, str)
        assert secret.get_secret_value() == "my-secret-password"

    def test_repr_masking(self):
        """Should mask value in repr."""
        secret = SecretStr("my-secret-password")
        assert repr(secret) == "SecretStr('**********')"
        assert "my-secret-password" not in repr(secret)

    def test_str_masking(self):
        """Should mask value in str()."""
        secret = SecretStr("my-secret-password")
        assert str(secret) == "**********"
        assert "my-secret-password" not in str(secret)

    def test_get_secret_value(self):
        """Should allow accessing actual secret value."""
        secret = SecretStr("my-secret-password")
        assert secret.get_secret_value() == "my-secret-password"

    def test_empty_secret(self):
        """Should allow empty secrets."""
        secret = SecretStr("")
        assert secret.get_secret_value() == ""
        assert str(secret) == "**********"

    def test_secret_type_error(self):
        """Should reject non-string inputs."""
        with pytest.raises(TypeError):
            SecretStr(123)  # type: ignore

    def test_secret_in_print(self):
        """Should be masked when printed."""
        secret = SecretStr("super-secret")
        output = f"Password: {secret}"
        assert output == "Password: **********"
        assert "super-secret" not in output

    def test_secret_in_dict(self):
        """Should be masked in dict repr."""
        config = {"password": SecretStr("secret123")}
        dict_str = str(config)
        assert "**********" in dict_str
        assert "secret123" not in dict_str


# ==============================================================================
# PostgresDsn Tests
# ==============================================================================


class TestPostgresDsn:
    """Tests for PostgresDsn type."""

    def test_valid_postgres_dsn(self):
        """Should accept valid PostgreSQL DSN."""
        valid_dsns = [
            "postgresql://user:pass@localhost:5432/dbname",
            "postgres://user:pass@localhost:5432/dbname",
            "postgresql://user@localhost/dbname",
            "postgres://localhost/db",
        ]
        for dsn in valid_dsns:
            result = PostgresDsn(dsn)
            assert str(result) == dsn.strip()

    def test_dsn_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        dsn = "  postgresql://user:pass@localhost/db  "
        result = PostgresDsn(dsn)
        assert str(result) == "postgresql://user:pass@localhost/db"

    def test_reject_invalid_scheme(self):
        """Should reject non-PostgreSQL schemes."""
        invalid_dsns = [
            "mysql://user:pass@localhost/db",
            "redis://localhost:6379",
            "http://localhost",
        ]
        for dsn in invalid_dsns:
            with pytest.raises(ValueError, match="must start with"):
                PostgresDsn(dsn)

    def test_reject_invalid_format(self):
        """Should reject invalid DSN format."""
        invalid_dsns = [
            "postgresql://",  # Empty
            "postgresql://localhost",  # Missing database (no slash)
        ]
        for dsn in invalid_dsns:
            with pytest.raises(ValueError, match="Invalid PostgreSQL DSN"):
                PostgresDsn(dsn)

    def test_dsn_type_error(self):
        """Should reject non-string inputs."""
        with pytest.raises(TypeError):
            PostgresDsn(123)  # type: ignore


# ==============================================================================
# RedisDsn Tests
# ==============================================================================


class TestRedisDsn:
    """Tests for RedisDsn type."""

    def test_valid_redis_dsn(self):
        """Should accept valid Redis DSN."""
        valid_dsns = [
            "redis://localhost:6379",
            "redis://localhost:6379/0",
            "redis://user:pass@localhost:6379",
            "rediss://localhost:6380",  # SSL
        ]
        for dsn in valid_dsns:
            result = RedisDsn(dsn)
            assert str(result) == dsn.strip()

    def test_dsn_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        dsn = "  redis://localhost:6379  "
        result = RedisDsn(dsn)
        assert str(result) == "redis://localhost:6379"

    def test_reject_invalid_scheme(self):
        """Should reject non-Redis schemes."""
        invalid_dsns = [
            "postgresql://localhost/db",
            "http://localhost",
            "mysql://localhost",
        ]
        for dsn in invalid_dsns:
            with pytest.raises(ValueError, match="must start with"):
                RedisDsn(dsn)

    def test_dsn_type_error(self):
        """Should reject non-string inputs."""
        with pytest.raises(TypeError):
            RedisDsn(123)  # type: ignore


# ==============================================================================
# PaymentCardNumber Tests
# ==============================================================================


class TestPaymentCardNumber:
    """Tests for PaymentCardNumber type."""

    def test_valid_card_numbers(self):
        """Should accept valid card numbers."""
        # Valid test card numbers (Luhn-valid)
        valid_cards = [
            "4532015112830366",  # Visa
            "5425233430109903",  # Mastercard
            "374245455400126",  # Amex
            "6011000991300009",  # Discover
        ]
        for card in valid_cards:
            result = PaymentCardNumber(card)
            assert len(result) >= 13

    def test_card_with_spaces(self):
        """Should accept card numbers with spaces."""
        card = "4532 0151 1283 0366"
        result = PaymentCardNumber(card)
        assert " " not in result  # Spaces removed
        assert len(result) == 16

    def test_card_with_dashes(self):
        """Should accept card numbers with dashes."""
        card = "4532-0151-1283-0366"
        result = PaymentCardNumber(card)
        assert "-" not in result  # Dashes removed
        assert len(result) == 16

    def test_reject_invalid_luhn(self):
        """Should reject card numbers that fail Luhn check."""
        invalid_cards = [
            "4532015112830367",  # Last digit wrong
            "1234567890123456",  # Invalid
        ]
        for card in invalid_cards:
            with pytest.raises(ValueError, match="failed Luhn check"):
                PaymentCardNumber(card)

    def test_reject_non_digits(self):
        """Should reject card numbers with non-digit characters."""
        invalid_cards = [
            "4532-0151-ABCD-0366",
            "card number 123",
        ]
        for card in invalid_cards:
            with pytest.raises(ValueError, match="only digits"):
                PaymentCardNumber(card)

    def test_reject_wrong_length(self):
        """Should reject card numbers with wrong length."""
        invalid_cards = [
            "123",  # Too short
            "12345678901234567890",  # Too long
        ]
        for card in invalid_cards:
            with pytest.raises(ValueError, match="must be"):
                PaymentCardNumber(card)

    def test_card_repr_masking(self):
        """Should mask card number in repr except last 4 digits."""
        card = PaymentCardNumber("4532015112830366")
        card_repr = repr(card)
        assert "0366" in card_repr  # Last 4 visible
        assert "4532" not in card_repr  # First 4 masked
        assert "*" in card_repr

    def test_card_type_error(self):
        """Should reject non-string inputs."""
        with pytest.raises(TypeError):
            PaymentCardNumber(123)  # type: ignore


# ==============================================================================
# FilePath Tests
# ==============================================================================


class TestFilePath:
    """Tests for FilePath type."""

    def test_valid_file_path(self, tmp_path):
        """Should accept existing file paths."""
        # Create a temporary file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        result = FilePath(str(test_file))
        assert str(result) == str(test_file)

    def test_file_strips_whitespace(self, tmp_path):
        """Should strip leading/trailing whitespace."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        result = FilePath(f"  {test_file}  ")
        assert str(result) == str(test_file)

    def test_reject_nonexistent_file(self):
        """Should reject paths that don't exist."""
        with pytest.raises(ValueError, match="does not exist"):
            FilePath("/nonexistent/file.txt")

    def test_reject_directory(self, tmp_path):
        """Should reject directory paths."""
        # tmp_path is a directory
        with pytest.raises(ValueError, match="not a file"):
            FilePath(str(tmp_path))

    def test_file_type_error(self):
        """Should reject non-string inputs."""
        with pytest.raises(TypeError):
            FilePath(123)  # type: ignore


# ==============================================================================
# DirectoryPath Tests
# ==============================================================================


class TestDirectoryPath:
    """Tests for DirectoryPath type."""

    def test_valid_directory_path(self, tmp_path):
        """Should accept existing directory paths."""
        result = DirectoryPath(str(tmp_path))
        assert str(result) == str(tmp_path)

    def test_directory_strips_whitespace(self, tmp_path):
        """Should strip leading/trailing whitespace."""
        result = DirectoryPath(f"  {tmp_path}  ")
        assert str(result) == str(tmp_path)

    def test_reject_nonexistent_directory(self):
        """Should reject paths that don't exist."""
        with pytest.raises(ValueError, match="does not exist"):
            DirectoryPath("/nonexistent/directory")

    def test_reject_file(self, tmp_path):
        """Should reject file paths."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        with pytest.raises(ValueError, match="not a directory"):
            DirectoryPath(str(test_file))

    def test_directory_type_error(self):
        """Should reject non-string inputs."""
        with pytest.raises(TypeError):
            DirectoryPath(123)  # type: ignore


# ==============================================================================
# IPv4Address Tests
# ==============================================================================


class TestIPv4Address:
    """Tests for IPv4Address type."""

    def test_valid_ipv4_addresses(self):
        """Should accept valid IPv4 addresses."""
        valid_ips = [
            "192.168.1.1",
            "10.0.0.1",
            "172.16.0.1",
            "0.0.0.0",
            "255.255.255.255",
        ]
        for ip in valid_ips:
            result = IPv4Address(ip)
            assert str(result) == ip

    def test_ipv4_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        result = IPv4Address("  192.168.1.1  ")
        assert str(result) == "192.168.1.1"

    def test_reject_invalid_ipv4(self):
        """Should reject invalid IPv4 addresses."""
        invalid_ips = [
            "256.1.1.1",  # Out of range
            "192.168.1",  # Too few octets
            "192.168.1.1.1",  # Too many octets
            "192.168.1.a",  # Non-numeric
            "not-an-ip",
        ]
        for ip in invalid_ips:
            with pytest.raises(ValueError, match="Invalid IPv4 address"):
                IPv4Address(ip)

    def test_reject_ipv6(self):
        """Should reject IPv6 addresses."""
        with pytest.raises(ValueError):
            IPv4Address("::1")

    def test_ipv4_type_error(self):
        """Should reject non-string inputs."""
        with pytest.raises(TypeError):
            IPv4Address(123)  # type: ignore


# ==============================================================================
# IPv6Address Tests
# ==============================================================================


class TestIPv6Address:
    """Tests for IPv6Address type."""

    def test_valid_ipv6_addresses(self):
        """Should accept valid IPv6 addresses."""
        valid_ips = [
            "::1",  # Loopback
            "2001:db8::1",
            "fe80::1",
            "2001:0db8:0000:0000:0000:0000:0000:0001",
            "::",  # All zeros
        ]
        for ip in valid_ips:
            result = IPv6Address(ip)
            # IPv6 addresses may be normalized
            assert isinstance(result, str)

    def test_ipv6_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        result = IPv6Address("  ::1  ")
        assert str(result) == "::1"

    def test_reject_invalid_ipv6(self):
        """Should reject invalid IPv6 addresses."""
        invalid_ips = [
            "gggg::1",  # Invalid hex
            "::1::2",  # Multiple ::
            "not-an-ip",
        ]
        for ip in invalid_ips:
            with pytest.raises(ValueError, match="Invalid IPv6 address"):
                IPv6Address(ip)

    def test_reject_ipv4(self):
        """Should reject IPv4 addresses."""
        with pytest.raises(ValueError):
            IPv6Address("192.168.1.1")

    def test_ipv6_type_error(self):
        """Should reject non-string inputs."""
        with pytest.raises(TypeError):
            IPv6Address(123)  # type: ignore


# ==============================================================================
# IPvAnyAddress Tests
# ==============================================================================


class TestIPvAnyAddress:
    """Tests for IPvAnyAddress type."""

    def test_valid_ipv4_addresses(self):
        """Should accept valid IPv4 addresses."""
        valid_ips = ["192.168.1.1", "10.0.0.1", "127.0.0.1"]
        for ip in valid_ips:
            result = IPvAnyAddress(ip)
            assert str(result) == ip

    def test_valid_ipv6_addresses(self):
        """Should accept valid IPv6 addresses."""
        valid_ips = ["::1", "2001:db8::1", "fe80::1"]
        for ip in valid_ips:
            result = IPvAnyAddress(ip)
            assert isinstance(result, str)

    def test_ip_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        result = IPvAnyAddress("  192.168.1.1  ")
        assert str(result) == "192.168.1.1"

    def test_reject_invalid_ip(self):
        """Should reject invalid IP addresses."""
        invalid_ips = [
            "256.1.1.1",
            "not-an-ip",
            "192.168.1",
            "",
        ]
        for ip in invalid_ips:
            with pytest.raises(ValueError, match="Invalid IP address"):
                IPvAnyAddress(ip)

    def test_ip_type_error(self):
        """Should reject non-string inputs."""
        with pytest.raises(TypeError):
            IPvAnyAddress(123)  # type: ignore


# ==============================================================================
# Json Tests
# ==============================================================================


class TestJson:
    """Tests for Json type."""

    def test_valid_json_object(self):
        """Should accept valid JSON objects."""
        valid_json = [
            '{"key": "value"}',
            '{"number": 123}',
            '{"array": [1, 2, 3]}',
            '{"nested": {"key": "value"}}',
        ]
        for json_str in valid_json:
            result = Json(json_str)
            assert str(result) == json_str

    def test_valid_json_array(self):
        """Should accept valid JSON arrays."""
        valid_json = [
            "[1, 2, 3]",
            '["a", "b", "c"]',
            '[{"key": "value"}]',
        ]
        for json_str in valid_json:
            result = Json(json_str)
            assert str(result) == json_str

    def test_valid_json_primitives(self):
        """Should accept JSON primitives."""
        valid_json = [
            '"string"',
            "123",
            "true",
            "false",
            "null",
        ]
        for json_str in valid_json:
            result = Json(json_str)
            assert str(result) == json_str

    def test_json_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        result = Json('  {"key": "value"}  ')
        assert str(result) == '{"key": "value"}'

    def test_reject_invalid_json(self):
        """Should reject invalid JSON."""
        invalid_json = [
            "{key: value}",  # Unquoted keys
            "{'key': 'value'}",  # Single quotes
            "{",  # Incomplete
            "not json",
            "",
        ]
        for json_str in invalid_json:
            with pytest.raises(ValueError, match="Invalid JSON"):
                Json(json_str)

    def test_json_type_error(self):
        """Should reject non-string inputs."""
        with pytest.raises(TypeError):
            Json(123)  # type: ignore


# ==============================================================================
# MacAddress Tests
# ==============================================================================


class TestMacAddress:
    """Tests for MacAddress type."""

    def test_valid_mac_colon_format(self):
        """Should accept MAC addresses in colon format."""
        valid_macs = [
            "00:1B:44:11:3A:B7",
            "00-1B-44-11-3A-B7",  # Also with dashes
        ]
        for mac in valid_macs:
            result = MacAddress(mac)
            # Should be uppercase
            assert str(result).upper() == str(result)

    def test_valid_mac_dot_format(self):
        """Should accept MAC addresses in dot format."""
        result = MacAddress("001B.4411.3AB7")
        assert str(result).upper() == str(result)

    def test_mac_uppercase_conversion(self):
        """Should convert MAC to uppercase."""
        result = MacAddress("aa:bb:cc:dd:ee:ff")
        assert str(result) == "AA:BB:CC:DD:EE:FF"

    def test_reject_invalid_mac(self):
        """Should reject invalid MAC addresses."""
        invalid_macs = [
            "00:1B:44:11:3A",  # Too short
            "00:1B:44:11:3A:B7:C8",  # Too long
            "GG:1B:44:11:3A:B7",  # Invalid hex
            "not-a-mac",
        ]
        for mac in invalid_macs:
            with pytest.raises(ValueError, match="Invalid MAC address"):
                MacAddress(mac)

    def test_mac_type_error(self):
        """Should reject non-string inputs."""
        with pytest.raises(TypeError):
            MacAddress(123)  # type: ignore


# ==============================================================================
# ConStr Tests
# ==============================================================================


class TestConStr:
    """Tests for ConStr type."""

    def test_constr_no_constraints(self):
        """Should accept any string with no constraints."""
        result = ConStr("any string")
        assert str(result) == "any string"

    def test_constr_min_length(self):
        """Should enforce minimum length."""
        result = ConStr("hello", min_length=3)
        assert str(result) == "hello"

        with pytest.raises(ValueError, match="at least"):
            ConStr("hi", min_length=5)

    def test_constr_max_length(self):
        """Should enforce maximum length."""
        result = ConStr("hi", max_length=5)
        assert str(result) == "hi"

        with pytest.raises(ValueError, match="at most"):
            ConStr("too long", max_length=3)

    def test_constr_pattern(self):
        """Should enforce regex pattern."""
        result = ConStr("abc123", pattern=r"^[a-z0-9]+$")
        assert str(result) == "abc123"

        with pytest.raises(ValueError, match="must match pattern"):
            ConStr("ABC", pattern=r"^[a-z]+$")

    def test_constr_all_constraints(self):
        """Should enforce all constraints together."""
        result = ConStr("abc123", min_length=3, max_length=10, pattern=r"^[a-z0-9]+$")
        assert str(result) == "abc123"

        # Too short
        with pytest.raises(ValueError):
            ConStr("ab", min_length=3, max_length=10, pattern=r"^[a-z0-9]+$")

        # Too long
        with pytest.raises(ValueError):
            ConStr("abcdefghijk", min_length=3, max_length=10, pattern=r"^[a-z0-9]+$")

        # Pattern mismatch
        with pytest.raises(ValueError):
            ConStr("ABC", min_length=3, max_length=10, pattern=r"^[a-z0-9]+$")

    def test_constr_type_error(self):
        """Should reject non-string inputs."""
        with pytest.raises(TypeError):
            ConStr(123)  # type: ignore


# ==============================================================================
# ByteSize Tests
# ==============================================================================


class TestByteSize:
    """Tests for ByteSize type."""

    def test_bytesize_from_int(self):
        """Should accept integer bytes."""
        result = ByteSize(1024)
        assert int(result) == 1024

    def test_bytesize_from_string_bytes(self):
        """Should parse byte strings."""
        result = ByteSize("100B")
        assert int(result) == 100

    def test_bytesize_kb(self):
        """Should parse KB units."""
        result = ByteSize("1KB")
        assert int(result) == 1000

    def test_bytesize_mb(self):
        """Should parse MB units."""
        result = ByteSize("1MB")
        assert int(result) == 1000**2

    def test_bytesize_gb(self):
        """Should parse GB units."""
        result = ByteSize("1GB")
        assert int(result) == 1000**3

    def test_bytesize_kib(self):
        """Should parse KiB (binary) units."""
        result = ByteSize("1KiB")
        assert int(result) == 1024

    def test_bytesize_mib(self):
        """Should parse MiB (binary) units."""
        result = ByteSize("1MiB")
        assert int(result) == 1024**2

    def test_bytesize_gib(self):
        """Should parse GiB (binary) units."""
        result = ByteSize("1GiB")
        assert int(result) == 1024**3

    def test_bytesize_case_insensitive(self):
        """Should handle case-insensitive units."""
        assert int(ByteSize("1mb")) == 1000**2
        assert int(ByteSize("1MB")) == 1000**2
        assert int(ByteSize("1Mb")) == 1000**2

    def test_bytesize_with_spaces(self):
        """Should handle sizes with spaces."""
        result = ByteSize("100 MB")
        assert int(result) == 100 * 1000**2

    def test_reject_invalid_bytesize(self):
        """Should reject invalid byte sizes."""
        invalid_sizes = [
            "abc",
            "100XB",  # Invalid unit
            "",
        ]
        for size in invalid_sizes:
            with pytest.raises(ValueError):
                ByteSize(size)

    def test_bytesize_type_error(self):
        """Should reject invalid input types."""
        with pytest.raises(TypeError):
            ByteSize([])  # type: ignore


# ==============================================================================
# PastDate Tests
# ==============================================================================


class TestPastDate:
    """Tests for PastDate type."""

    def test_valid_past_date_from_date(self):
        """Should accept dates in the past."""
        yesterday = date.today() - timedelta(days=1)
        result = PastDate(yesterday)
        assert result == yesterday

    def test_valid_past_date_from_string(self):
        """Should accept ISO date strings in the past."""
        yesterday = date.today() - timedelta(days=1)
        result = PastDate(yesterday.isoformat())
        assert result == yesterday

    def test_reject_today(self):
        """Should reject today's date."""
        today = date.today()
        with pytest.raises(ValueError, match="must be in the past"):
            PastDate(today)

    def test_reject_future_date(self):
        """Should reject future dates."""
        tomorrow = date.today() + timedelta(days=1)
        with pytest.raises(ValueError, match="must be in the past"):
            PastDate(tomorrow)

    def test_past_date_invalid_string(self):
        """Should reject invalid date strings."""
        with pytest.raises(ValueError, match="Invalid date format"):
            PastDate("not-a-date")

    def test_past_date_type_error(self):
        """Should reject invalid input types."""
        with pytest.raises(TypeError):
            PastDate(123)  # type: ignore


# ==============================================================================
# FutureDate Tests
# ==============================================================================


class TestFutureDate:
    """Tests for FutureDate type."""

    def test_valid_future_date_from_date(self):
        """Should accept dates in the future."""
        tomorrow = date.today() + timedelta(days=1)
        result = FutureDate(tomorrow)
        assert result == tomorrow

    def test_valid_future_date_from_string(self):
        """Should accept ISO date strings in the future."""
        tomorrow = date.today() + timedelta(days=1)
        result = FutureDate(tomorrow.isoformat())
        assert result == tomorrow

    def test_reject_today(self):
        """Should reject today's date."""
        today = date.today()
        with pytest.raises(ValueError, match="must be in the future"):
            FutureDate(today)

    def test_reject_past_date(self):
        """Should reject past dates."""
        yesterday = date.today() - timedelta(days=1)
        with pytest.raises(ValueError, match="must be in the future"):
            FutureDate(yesterday)

    def test_future_date_invalid_string(self):
        """Should reject invalid date strings."""
        with pytest.raises(ValueError, match="Invalid date format"):
            FutureDate("not-a-date")

    def test_future_date_type_error(self):
        """Should reject invalid input types."""
        with pytest.raises(TypeError):
            FutureDate(123)  # type: ignore
