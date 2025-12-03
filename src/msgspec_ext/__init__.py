import msgspec

from .settings import BaseSettings, SettingsConfigDict, _dec_hook, _enc_hook
from .types import (
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

# Re-export useful msgspec native types for convenience
Raw = msgspec.Raw
UNSET = msgspec.UNSET

# Re-export hooks with public names
dec_hook = _dec_hook
enc_hook = _enc_hook

__all__ = [
    "UNSET",
    "AnyUrl",
    "BaseSettings",
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
    "Raw",
    "RedisDsn",
    "SecretStr",
    "SettingsConfigDict",
    "dec_hook",
    "enc_hook",
]
