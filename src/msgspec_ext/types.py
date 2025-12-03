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

import ipaddress
import json
import os
import re
from datetime import date, datetime
from typing import Annotated, ClassVar

import msgspec

__all__ = [
    "AnyUrl",
    "ByteSize",
    "ConStr",
    "DirectoryPath",
    "EmailStr",
    "FilePath",
    "FutureDate",
    "HttpUrl",
    "IPv4Address",
    "IPv6Address",
    "IPvAnyAddress",
    "Json",
    "MacAddress",
    "NegativeFloat",
    "NegativeInt",
    "NonNegativeFloat",
    "NonNegativeInt",
    "NonPositiveFloat",
    "NonPositiveInt",
    "PastDate",
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


# ==============================================================================
# IP Address Validation Types
# ==============================================================================


class _IPv4Address(str):
    """IPv4 address validation.

    Validates IPv4 addresses (e.g., 192.168.1.1).
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "_IPv4Address":
        """Create and validate IPv4 address.

        Args:
            value: IPv4 address string

        Returns:
            Validated IPv4 address

        Raises:
            ValueError: If address format is invalid
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")

        value = value.strip()

        try:
            # Validate using ipaddress module
            addr = ipaddress.IPv4Address(value)
            return str.__new__(cls, str(addr))
        except (ValueError, ipaddress.AddressValueError) as e:
            raise ValueError(f"Invalid IPv4 address: {value!r}") from e

    def __repr__(self) -> str:
        return f"IPv4Address({str.__repr__(self)})"


class _IPv6Address(str):
    """IPv6 address validation.

    Validates IPv6 addresses (e.g., 2001:0db8:85a3::8a2e:0370:7334).
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "_IPv6Address":
        """Create and validate IPv6 address.

        Args:
            value: IPv6 address string

        Returns:
            Validated IPv6 address

        Raises:
            ValueError: If address format is invalid
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")

        value = value.strip()

        try:
            # Validate using ipaddress module
            addr = ipaddress.IPv6Address(value)
            return str.__new__(cls, str(addr))
        except (ValueError, ipaddress.AddressValueError) as e:
            raise ValueError(f"Invalid IPv6 address: {value!r}") from e

    def __repr__(self) -> str:
        return f"IPv6Address({str.__repr__(self)})"


class _IPvAnyAddress(str):
    """IP address validation (IPv4 or IPv6).

    Validates both IPv4 and IPv6 addresses.
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "_IPvAnyAddress":
        """Create and validate IP address.

        Args:
            value: IP address string (IPv4 or IPv6)

        Returns:
            Validated IP address

        Raises:
            ValueError: If address format is invalid
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")

        value = value.strip()

        try:
            # Validate using ipaddress module (accepts both IPv4 and IPv6)
            addr = ipaddress.ip_address(value)
            return str.__new__(cls, str(addr))
        except (ValueError, ipaddress.AddressValueError) as e:
            raise ValueError(f"Invalid IP address: {value!r}") from e

    def __repr__(self) -> str:
        return f"IPvAnyAddress({str.__repr__(self)})"


# ==============================================================================
# JSON and Special String Types
# ==============================================================================


class _Json(str):
    """JSON string validation.

    Validates that a string contains valid JSON.
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "_Json":
        """Create and validate JSON string.

        Args:
            value: JSON string

        Returns:
            Validated JSON string

        Raises:
            ValueError: If JSON is invalid
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")

        value = value.strip()

        try:
            # Validate by parsing
            json.loads(value)
            return str.__new__(cls, value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}") from e

    def __repr__(self) -> str:
        return f"Json({str.__repr__(self)})"


class _MacAddress(str):
    """MAC address validation.

    Validates MAC addresses in common formats:
    - 00:1B:44:11:3A:B7
    - 00-1B-44-11-3A-B7
    - 001B.4411.3AB7
    """

    __slots__ = ()

    # MAC address patterns
    _MAC_PATTERNS: ClassVar[list] = [
        re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"),  # 00:1B:44:11:3A:B7
        re.compile(r"^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$"),  # 001B.4411.3AB7
    ]

    def __new__(cls, value: str) -> "_MacAddress":
        """Create and validate MAC address.

        Args:
            value: MAC address string

        Returns:
            Validated MAC address

        Raises:
            ValueError: If MAC address format is invalid
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")

        value = value.strip()

        # Check against patterns
        if not any(pattern.match(value) for pattern in cls._MAC_PATTERNS):
            raise ValueError(f"Invalid MAC address format: {value!r}")

        return str.__new__(cls, value.upper())

    def __repr__(self) -> str:
        return f"MacAddress({str.__repr__(self)})"


class _ConStr(str):
    """Constrained string with validation.

    String with optional min_length, max_length, and pattern constraints.
    """

    __slots__ = ("_max_length", "_min_length", "_pattern")

    def __new__(
        cls,
        value: str,
        min_length: int | None = None,
        max_length: int | None = None,
        pattern: str | None = None,
    ) -> "_ConStr":
        """Create and validate constrained string.

        Args:
            value: String value
            min_length: Minimum length (optional)
            max_length: Maximum length (optional)
            pattern: Regex pattern (optional)

        Returns:
            Validated constrained string

        Raises:
            ValueError: If constraints are violated
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")

        # Check min_length
        if min_length is not None and len(value) < min_length:
            raise ValueError(f"String must be at least {min_length} characters")

        # Check max_length
        if max_length is not None and len(value) > max_length:
            raise ValueError(f"String must be at most {max_length} characters")

        # Check pattern
        if pattern is not None and not re.match(pattern, value):
            raise ValueError(f"String must match pattern: {pattern!r}")

        instance = str.__new__(cls, value)
        # Store constraints (though they're not used after validation)
        object.__setattr__(instance, "_min_length", min_length)
        object.__setattr__(instance, "_max_length", max_length)
        object.__setattr__(instance, "_pattern", pattern)
        return instance

    def __repr__(self) -> str:
        return f"ConStr({str.__repr__(self)})"


# ==============================================================================
# Byte Size Type
# ==============================================================================


class _ByteSize(int):
    """Byte size with unit parsing.

    Accepts sizes with units: B, KB, MB, GB, TB, KiB, MiB, GiB, TiB.
    """

    __slots__ = ()

    # Size multipliers
    _UNITS: ClassVar[dict[str, int]] = {
        "B": 1,
        "KB": 1000,
        "MB": 1000**2,
        "GB": 1000**3,
        "TB": 1000**4,
        "KIB": 1024,
        "MIB": 1024**2,
        "GIB": 1024**3,
        "TIB": 1024**4,
    }

    def __new__(cls, value: str | int) -> "_ByteSize":
        """Create and validate byte size.

        Args:
            value: Size as int (bytes) or str with unit (e.g., "1MB", "500KB")

        Returns:
            Validated byte size (as int)

        Raises:
            ValueError: If format is invalid
        """
        if isinstance(value, int):
            if value < 0:
                raise ValueError("Byte size must be non-negative")
            return int.__new__(cls, value)

        if not isinstance(value, str):
            raise TypeError(f"Expected str or int, got {type(value).__name__}")

        value = value.strip().upper()

        # Try to parse number + unit
        match = re.match(r"^(\d+(?:\.\d+)?)\s*([A-Z]+)?$", value)
        if not match:
            raise ValueError(f"Invalid byte size format: {value!r}")

        number_str, unit = match.groups()
        number = float(number_str)

        if unit is None or unit == "B":
            bytes_value = int(number)
        elif unit in cls._UNITS:
            bytes_value = int(number * cls._UNITS[unit])
        else:
            raise ValueError(f"Unknown unit: {unit!r}")

        if bytes_value < 0:
            raise ValueError("Byte size must be non-negative")

        return int.__new__(cls, bytes_value)

    def __repr__(self) -> str:
        return f"ByteSize({int.__repr__(self)})"


# ==============================================================================
# Date Validation Types
# ==============================================================================


class _PastDate(date):
    """Date that must be in the past.

    Validates that the date is before today.
    """

    __slots__ = ()

    def __new__(cls, value: date | str) -> "_PastDate":
        """Create and validate past date.

        Args:
            value: Date object or ISO format string (YYYY-MM-DD)

        Returns:
            Validated past date

        Raises:
            ValueError: If date is not in the past
        """
        if isinstance(value, str):
            try:
                parsed_date = datetime.fromisoformat(value).date()
            except ValueError as e:
                raise ValueError(f"Invalid date format: {value!r}") from e
        elif isinstance(value, date):
            parsed_date = value
        else:
            raise TypeError(f"Expected date or str, got {type(value).__name__}")

        today = date.today()  # noqa: DTZ011
        if parsed_date >= today:
            raise ValueError(f"Date must be in the past: {parsed_date}")

        return date.__new__(cls, parsed_date.year, parsed_date.month, parsed_date.day)

    def __repr__(self) -> str:
        return f"PastDate({date.__repr__(self)})"


class _FutureDate(date):
    """Date that must be in the future.

    Validates that the date is after today.
    """

    __slots__ = ()

    def __new__(cls, value: date | str) -> "_FutureDate":
        """Create and validate future date.

        Args:
            value: Date object or ISO format string (YYYY-MM-DD)

        Returns:
            Validated future date

        Raises:
            ValueError: If date is not in the future
        """
        if isinstance(value, str):
            try:
                parsed_date = datetime.fromisoformat(value).date()
            except ValueError as e:
                raise ValueError(f"Invalid date format: {value!r}") from e
        elif isinstance(value, date):
            parsed_date = value
        else:
            raise TypeError(f"Expected date or str, got {type(value).__name__}")

        today = date.today()  # noqa: DTZ011
        if parsed_date <= today:
            raise ValueError(f"Date must be in the future: {parsed_date}")

        return date.__new__(cls, parsed_date.year, parsed_date.month, parsed_date.day)

    def __repr__(self) -> str:
        return f"FutureDate({date.__repr__(self)})"


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
IPv4Address = _IPv4Address
IPv6Address = _IPv6Address
IPvAnyAddress = _IPvAnyAddress
Json = _Json
MacAddress = _MacAddress
ConStr = _ConStr
ByteSize = _ByteSize
PastDate = _PastDate
FutureDate = _FutureDate
