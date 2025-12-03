"""Custom types and validators for msgspec-ext.

Provides Pydantic-like type aliases and validation types built on msgspec.Meta.

Example:
    from msgspec_ext import BaseSettings
    from msgspec_ext.types import EmailStr, HttpUrl, PositiveInt

    class AppSettings(BaseSettings):
        email: EmailStr
        api_url: HttpUrl
        max_connections: PositiveInt
"""

import os
import re
from typing import Annotated

import msgspec

__all__ = [
    "AnyUrl",
    "DirectoryPath",
    "EmailStr",
    "FilePath",
    "HttpUrl",
    "NegativeFloat",
    "NegativeInt",
    "NonNegativeFloat",
    "NonNegativeInt",
    "NonPositiveFloat",
    "NonPositiveInt",
    "PaymentCardNumber",
    "PositiveFloat",
    "PositiveInt",
    "PostgresDsn",
    "RedisDsn",
    "SecretStr",
]

# ==============================================================================
# Numeric Constraint Types
# ==============================================================================

# Integer types
PositiveInt = Annotated[int, msgspec.Meta(gt=0, description="Integer greater than 0")]
NegativeInt = Annotated[int, msgspec.Meta(lt=0, description="Integer less than 0")]
NonNegativeInt = Annotated[int, msgspec.Meta(ge=0, description="Integer >= 0")]
NonPositiveInt = Annotated[int, msgspec.Meta(le=0, description="Integer <= 0")]

# Float types
PositiveFloat = Annotated[
    float, msgspec.Meta(gt=0.0, description="Float greater than 0.0")
]
NegativeFloat = Annotated[
    float, msgspec.Meta(lt=0.0, description="Float less than 0.0")
]
NonNegativeFloat = Annotated[float, msgspec.Meta(ge=0.0, description="Float >= 0.0")]
NonPositiveFloat = Annotated[float, msgspec.Meta(le=0.0, description="Float <= 0.0")]


# ==============================================================================
# String Validation Types with Custom Logic
# ==============================================================================

# Email validation constants
_EMAIL_MIN_LENGTH = 3
_EMAIL_MAX_LENGTH = 320  # RFC 5321

# URL validation constants
_URL_MAX_LENGTH = 2083  # IE limit, de facto standard

# Payment card validation constants
_CARD_MIN_LENGTH = 13
_CARD_MAX_LENGTH = 19
_CARD_MASK_LAST_DIGITS = 4
_LUHN_DOUBLE_THRESHOLD = 9

# Email regex pattern (simplified but covers most common cases)
# More strict than basic patterns, requires @ and domain with TLD
_EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# URL regex patterns
_HTTP_URL_PATTERN = r"^https?://[^\s/$.?#].[^\s]*$"
_ANY_URL_PATTERN = r"^[a-zA-Z][a-zA-Z0-9+.-]*:.+$"


class _EmailStr(str):
    """Email string type with validation.

    Validates email format using regex pattern.
    Compatible with msgspec encoding/decoding.
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "_EmailStr":
        """Create and validate email string.

        Args:
            value: Email address string

        Returns:
            Validated email string

        Raises:
            ValueError: If email format is invalid
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")

        # Strip whitespace
        value = value.strip()

        # Validate length
        if not value or len(value) < _EMAIL_MIN_LENGTH:
            raise ValueError(f"Email must be at least {_EMAIL_MIN_LENGTH} characters")
        if len(value) > _EMAIL_MAX_LENGTH:
            raise ValueError(f"Email must be at most {_EMAIL_MAX_LENGTH} characters")

        # Validate format
        if not re.match(_EMAIL_PATTERN, value):
            raise ValueError(f"Invalid email format: {value!r}")

        return str.__new__(cls, value)

    def __repr__(self) -> str:
        return f"EmailStr({str.__repr__(self)})"


class _HttpUrl(str):
    """HTTP/HTTPS URL string type with validation.

    Validates URL format and scheme (http or https only).
    Compatible with msgspec encoding/decoding.
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "_HttpUrl":
        """Create and validate HTTP URL string.

        Args:
            value: HTTP/HTTPS URL string

        Returns:
            Validated URL string

        Raises:
            ValueError: If URL format is invalid or scheme is not http/https
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")

        # Strip whitespace
        value = value.strip()

        # Validate length
        if not value:
            raise ValueError("URL cannot be empty")
        if len(value) > _URL_MAX_LENGTH:
            raise ValueError(f"URL must be at most {_URL_MAX_LENGTH} characters")

        # Validate format
        if not re.match(_HTTP_URL_PATTERN, value, re.IGNORECASE):
            raise ValueError(f"Invalid HTTP URL format: {value!r}")

        # Ensure http/https scheme
        lower_value = value.lower()
        if not (
            lower_value.startswith("http://") or lower_value.startswith("https://")
        ):
            raise ValueError(f"URL must use http or https scheme: {value!r}")

        return str.__new__(cls, value)

    def __repr__(self) -> str:
        return f"HttpUrl({str.__repr__(self)})"


class _AnyUrl(str):
    """URL string type with validation for any scheme.

    Validates URL format for any valid scheme (http, https, ftp, ws, etc).
    Compatible with msgspec encoding/decoding.
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "_AnyUrl":
        """Create and validate URL string.

        Args:
            value: URL string with any scheme

        Returns:
            Validated URL string

        Raises:
            ValueError: If URL format is invalid
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")

        # Strip whitespace
        value = value.strip()

        # Validate length
        if not value:
            raise ValueError("URL cannot be empty")

        # Validate format
        if not re.match(_ANY_URL_PATTERN, value, re.IGNORECASE):
            raise ValueError(f"Invalid URL format: {value!r}")

        return str.__new__(cls, value)

    def __repr__(self) -> str:
        return f"AnyUrl({str.__repr__(self)})"


class _SecretStr(str):
    """Secret string type that masks the value in string representation.

    Useful for passwords, API keys, tokens, and other sensitive data.
    The actual value is accessible but hidden in logs and reprs.
    Compatible with msgspec encoding/decoding.
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "_SecretStr":
        """Create secret string.

        Args:
            value: The secret string value

        Returns:
            Secret string instance

        Raises:
            TypeError: If value is not a string
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")

        return str.__new__(cls, value)

    def __repr__(self) -> str:
        """Return masked representation."""
        return "SecretStr('**********')"

    def __str__(self) -> str:
        """Return masked string representation."""
        return "**********"

    def get_secret_value(self) -> str:
        """Get the actual secret value.

        Returns:
            The unmasked secret string
        """
        return str.__str__(self)


class _PostgresDsn(str):
    """PostgreSQL DSN (Data Source Name) validation.

    Validates PostgreSQL connection strings.
    Format: postgresql://user:password@host:port/database
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "_PostgresDsn":
        """Create and validate PostgreSQL DSN.

        Args:
            value: PostgreSQL connection string

        Returns:
            Validated DSN string

        Raises:
            ValueError: If DSN format is invalid
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")

        value = value.strip()

        # Check scheme
        if not value.lower().startswith(("postgresql://", "postgres://")):
            raise ValueError(
                "PostgreSQL DSN must start with 'postgresql://' or 'postgres://'"
            )

        # Basic validation: must have a host/database part after scheme
        # Format can be: postgresql://host/db or postgresql://user:pass@host/db
        scheme_end = value.find("://") + 3
        remainder = value[scheme_end:]
        if not remainder or "/" not in remainder:
            raise ValueError("Invalid PostgreSQL DSN format")

        return str.__new__(cls, value)

    def __repr__(self) -> str:
        return f"PostgresDsn({str.__repr__(self)})"


class _RedisDsn(str):
    """Redis DSN (Data Source Name) validation.

    Validates Redis connection strings.
    Format: redis://[user:password@]host:port[/database]
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "_RedisDsn":
        """Create and validate Redis DSN.

        Args:
            value: Redis connection string

        Returns:
            Validated DSN string

        Raises:
            ValueError: If DSN format is invalid
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")

        value = value.strip()

        # Check scheme
        if not value.lower().startswith(("redis://", "rediss://")):
            raise ValueError("Redis DSN must start with 'redis://' or 'rediss://'")

        return str.__new__(cls, value)

    def __repr__(self) -> str:
        return f"RedisDsn({str.__repr__(self)})"


class _PaymentCardNumber(str):
    """Payment card number validation using Luhn algorithm.

    Validates credit/debit card numbers.
    Supports major card types: Visa, Mastercard, Amex, Discover, etc.
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "_PaymentCardNumber":
        """Create and validate payment card number.

        Args:
            value: Card number (with or without spaces/dashes)

        Returns:
            Validated card number

        Raises:
            ValueError: If card number is invalid
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")

        # Remove spaces and dashes
        digits = value.replace(" ", "").replace("-", "")

        # Check all digits
        if not digits.isdigit():
            raise ValueError("Card number must contain only digits")

        # Check length (13-19 digits for most cards)
        if not _CARD_MIN_LENGTH <= len(digits) <= _CARD_MAX_LENGTH:
            raise ValueError(
                f"Card number must be {_CARD_MIN_LENGTH}-{_CARD_MAX_LENGTH} digits"
            )

        # Luhn algorithm validation
        if not cls._luhn_check(digits):
            raise ValueError("Invalid card number (failed Luhn check)")

        return str.__new__(cls, digits)

    @staticmethod
    def _luhn_check(card_number: str) -> bool:
        """Validate card number using Luhn algorithm.

        Args:
            card_number: Card number string (digits only)

        Returns:
            True if valid, False otherwise
        """
        total = 0
        reverse_digits = card_number[::-1]

        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:  # Every second digit from the right
                n *= 2
                if n > _LUHN_DOUBLE_THRESHOLD:
                    n -= _LUHN_DOUBLE_THRESHOLD
            total += n

        return total % 10 == 0

    def __repr__(self) -> str:
        # Mask all but last 4 digits
        if len(self) >= _CARD_MASK_LAST_DIGITS:
            masked = (
                "*" * (len(self) - _CARD_MASK_LAST_DIGITS)
                + str.__str__(self)[-_CARD_MASK_LAST_DIGITS:]
            )
        else:
            masked = "*" * len(self)
        return f"PaymentCardNumber('{masked}')"


class _FilePath(str):
    """File path validation - must exist and be a file.

    Validates that the path exists and points to a file (not directory).
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "_FilePath":
        """Create and validate file path.

        Args:
            value: Path to file

        Returns:
            Validated file path

        Raises:
            ValueError: If path doesn't exist or is not a file
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")

        value = value.strip()

        if not os.path.exists(value):
            raise ValueError(f"Path does not exist: {value}")

        if not os.path.isfile(value):
            raise ValueError(f"Path is not a file: {value}")

        return str.__new__(cls, value)

    def __repr__(self) -> str:
        return f"FilePath({str.__repr__(self)})"


class _DirectoryPath(str):
    """Directory path validation - must exist and be a directory.

    Validates that the path exists and points to a directory (not file).
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "_DirectoryPath":
        """Create and validate directory path.

        Args:
            value: Path to directory

        Returns:
            Validated directory path

        Raises:
            ValueError: If path doesn't exist or is not a directory
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")

        value = value.strip()

        if not os.path.exists(value):
            raise ValueError(f"Path does not exist: {value}")

        if not os.path.isdir(value):
            raise ValueError(f"Path is not a directory: {value}")

        return str.__new__(cls, value)

    def __repr__(self) -> str:
        return f"DirectoryPath({str.__repr__(self)})"


# Export as type aliases for better DX
EmailStr = _EmailStr
HttpUrl = _HttpUrl
AnyUrl = _AnyUrl
SecretStr = _SecretStr
PostgresDsn = _PostgresDsn
RedisDsn = _RedisDsn
PaymentCardNumber = _PaymentCardNumber
FilePath = _FilePath
DirectoryPath = _DirectoryPath
