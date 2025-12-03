"""Tests for custom types and validators in msgspec_ext.types."""

import pytest

from msgspec_ext.types import (
    AnyUrl,
    DirectoryPath,
    EmailStr,
    FilePath,
    HttpUrl,
    NegativeFloat,
    NegativeInt,
    NonNegativeFloat,
    NonNegativeInt,
    NonPositiveFloat,
    NonPositiveInt,
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
