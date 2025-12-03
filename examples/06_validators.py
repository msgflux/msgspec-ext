"""Example demonstrating custom validators and constrained types.

This example shows how to use msgspec-ext's built-in validators:
- EmailStr for email validation
- HttpUrl for HTTP/HTTPS URL validation
- PositiveInt, NegativeInt, NonNegativeInt for numeric constraints
- PositiveFloat, NegativeFloat for float constraints
"""

import os
import tempfile

from msgspec_ext import (
    AnyUrl,
    BaseSettings,
    DirectoryPath,
    EmailStr,
    FilePath,
    HttpUrl,
    NegativeInt,
    NonNegativeInt,
    PaymentCardNumber,
    PositiveFloat,
    PositiveInt,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    SettingsConfigDict,
)


# Example 1: Email validation
class EmailSettings(BaseSettings):
    """Settings with email validation."""

    model_config = SettingsConfigDict(env_prefix="EMAIL_")

    admin_email: EmailStr
    support_email: EmailStr
    notifications_email: EmailStr = EmailStr("noreply@example.com")


# Example 2: URL validation
class APISettings(BaseSettings):
    """Settings with URL validation."""

    model_config = SettingsConfigDict(env_prefix="API_")

    base_url: HttpUrl  # HTTP/HTTPS only
    webhook_url: HttpUrl
    docs_url: AnyUrl  # Any valid URL scheme


# Example 3: Numeric constraints
class DatabaseSettings(BaseSettings):
    """Settings with numeric constraints."""

    model_config = SettingsConfigDict(env_prefix="DB_")

    port: PositiveInt  # > 0
    max_connections: PositiveInt
    min_connections: NonNegativeInt  # >= 0
    timeout: PositiveFloat  # > 0.0


# Example 4: Secret string (passwords, API keys, tokens)
class SecretSettings(BaseSettings):
    """Settings with secret strings (masked in logs/output)."""

    model_config = SettingsConfigDict(env_prefix="SECRET_")

    api_key: SecretStr
    database_password: SecretStr
    jwt_secret: SecretStr


# Example 5: Database and cache DSN validation
class ConnectionSettings(BaseSettings):
    """Settings with DSN validation."""

    model_config = SettingsConfigDict(env_prefix="CONN_")

    postgres_url: PostgresDsn
    redis_url: RedisDsn


# Example 6: Payment card validation
class PaymentSettings(BaseSettings):
    """Settings with payment card validation."""

    model_config = SettingsConfigDict(env_prefix="PAYMENT_")

    card_number: PaymentCardNumber


# Example 7: File and directory path validation
class PathSettings(BaseSettings):
    """Settings with path validation."""

    model_config = SettingsConfigDict(env_prefix="PATH_")

    config_file: FilePath
    data_directory: DirectoryPath


# Example 8: Combined validators
class AppSettings(BaseSettings):
    """Real-world app settings with multiple validators."""

    # Email validation
    admin_email: EmailStr

    # URL validation
    api_url: HttpUrl
    frontend_url: HttpUrl

    # Secret strings (masked)
    api_key: SecretStr
    db_password: SecretStr

    # Positive integers
    port: PositiveInt
    max_workers: PositiveInt

    # Non-negative integers (can be 0)
    retry_count: NonNegativeInt

    # Positive floats
    timeout: PositiveFloat
    rate_limit: PositiveFloat

    # Defaults
    debug: bool = False


def main():  # noqa: PLR0915
    print("=" * 60)
    print("msgspec-ext Validators Demo")
    print("=" * 60)

    # Example 1: Email validation
    print("\n1. Email Validation")
    print("-" * 60)

    os.environ.update(
        {
            "EMAIL_ADMIN_EMAIL": "admin@example.com",
            "EMAIL_SUPPORT_EMAIL": "support@company.org",
        }
    )

    email_settings = EmailSettings()
    print(f"Admin Email: {email_settings.admin_email}")
    print(f"Support Email: {email_settings.support_email}")
    print(f"Notifications: {email_settings.notifications_email}")

    # Try invalid email (will raise ValueError)
    try:
        EmailStr("not-an-email")
    except ValueError as e:
        print(f"✓ Email validation works: {e}")

    # Example 2: URL validation
    print("\n2. URL Validation")
    print("-" * 60)

    os.environ.update(
        {
            "API_BASE_URL": "https://api.example.com",
            "API_WEBHOOK_URL": "https://webhook.example.com/events",
            "API_DOCS_URL": "https://docs.example.com",
        }
    )

    api_settings = APISettings()
    print(f"Base URL: {api_settings.base_url}")
    print(f"Webhook URL: {api_settings.webhook_url}")
    print(f"Docs URL: {api_settings.docs_url}")

    # Try invalid URL (will raise ValueError)
    try:
        HttpUrl("not a url")
    except ValueError as e:
        print(f"✓ URL validation works: {e}")

    # Try non-HTTP scheme (will raise ValueError)
    try:
        HttpUrl("ftp://example.com")
    except ValueError as e:
        print(f"✓ HTTP scheme validation works: {e}")

    # Example 3: Numeric constraints
    print("\n3. Numeric Constraints")
    print("-" * 60)

    os.environ.update(
        {
            "DB_PORT": "5432",
            "DB_MAX_CONNECTIONS": "100",
            "DB_MIN_CONNECTIONS": "0",
            "DB_TIMEOUT": "30.5",
        }
    )

    db_settings = DatabaseSettings()
    print(f"Port: {db_settings.port} (PositiveInt)")
    print(f"Max Connections: {db_settings.max_connections} (PositiveInt)")
    print(f"Min Connections: {db_settings.min_connections} (NonNegativeInt)")
    print(f"Timeout: {db_settings.timeout}s (PositiveFloat)")

    # Example 4: Secret strings
    print("\n4. Secret Strings (Masked in Output)")
    print("-" * 60)

    # codeql[py/clear-text-logging-sensitive-data] - example code with fake credentials
    os.environ.update(
        {
            "SECRET_API_KEY": "sk_live_1234567890abcdef",  # example fake key
            "SECRET_DATABASE_PASSWORD": "super-secret-password-123",  # example fake password
            "SECRET_JWT_SECRET": "jwt-signing-key-xyz",  # example fake secret
        }
    )

    secret_settings = SecretSettings()
    print(f"API Key: {secret_settings.api_key}")  # Masked
    print(f"DB Password: {secret_settings.database_password}")  # Masked
    print(f"JWT Secret: {secret_settings.jwt_secret}")  # Masked
    print(f"Actual API Key: {secret_settings.api_key.get_secret_value()}")  # Unmasked

    # Example 5: Database and Cache DSN validation
    print("\n5. Database & Cache DSN Validation")
    print("-" * 60)

    os.environ.update(
        {
            "CONN_POSTGRES_URL": "postgresql://user:pass@localhost:5432/mydb",
            "CONN_REDIS_URL": "redis://localhost:6379/0",
        }
    )

    conn_settings = ConnectionSettings()
    print(f"PostgreSQL: {conn_settings.postgres_url}")
    print(f"Redis: {conn_settings.redis_url}")

    # Try invalid DSN
    try:
        PostgresDsn("mysql://localhost/db")
    except ValueError as e:
        print(f"✓ PostgreSQL DSN validation works: {e}")

    # Example 6: Payment card validation
    print("\n6. Payment Card Validation (Luhn Algorithm)")
    print("-" * 60)

    os.environ.update(
        {
            "PAYMENT_CARD_NUMBER": "4532-0151-1283-0366",  # Valid Visa test card
        }
    )

    payment_settings = PaymentSettings()
    print(f"Card Number: {payment_settings.card_number}")  # Shows digits
    print(f"Card Repr: {payment_settings.card_number!r}")  # Masked!

    # Try invalid card
    try:
        PaymentCardNumber("1234567890123456")
    except ValueError as e:
        print(f"✓ Card validation works: {e}")

    # Example 7: File and directory path validation
    print("\n7. File & Directory Path Validation")
    print("-" * 60)

    # Create temporary file and use current directory
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".conf") as f:
        f.write("config=value")
        temp_config_file = f.name

    os.environ.update(
        {
            "PATH_CONFIG_FILE": temp_config_file,
            "PATH_DATA_DIRECTORY": ".",  # Current directory
        }
    )

    path_settings = PathSettings()
    print(f"Config File: {path_settings.config_file}")
    print(f"Data Directory: {path_settings.data_directory}")

    # Cleanup
    os.unlink(temp_config_file)

    # Try nonexistent file
    try:
        FilePath("/nonexistent/file.txt")
    except ValueError as e:
        print(f"✓ Path validation works: {e}")

    # Example 8: Real-World Combined validators
    print("\n8. Real-World App Settings")
    print("-" * 60)

    # Set environment variables
    # codeql[py/clear-text-logging-sensitive-data] - example code with fake credentials
    os.environ.update(
        {
            "ADMIN_EMAIL": "admin@myapp.com",
            "API_URL": "https://api.myapp.com",
            "FRONTEND_URL": "https://myapp.com",
            "API_KEY": "sk_prod_secret_key_123",  # example fake key
            "DB_PASSWORD": "postgres_password_456",  # example fake password
            "PORT": "8000",
            "MAX_WORKERS": "4",
            "RETRY_COUNT": "3",
            "TIMEOUT": "30.0",
            "RATE_LIMIT": "100.0",
        }
    )

    app_settings = AppSettings()
    print(f"Admin: {app_settings.admin_email}")
    print(f"API: {app_settings.api_url}")
    print(f"Frontend: {app_settings.frontend_url}")
    print(f"API Key: {app_settings.api_key}")  # Masked!
    print(f"DB Password: {app_settings.db_password}")  # Masked!
    print(f"Port: {app_settings.port}")
    print(f"Workers: {app_settings.max_workers}")
    print(f"Retries: {app_settings.retry_count}")
    print(f"Timeout: {app_settings.timeout}s")
    print(f"Rate Limit: {app_settings.rate_limit}/s")
    print(f"Debug: {app_settings.debug}")

    # Example 9: Validation errors
    print("\n9. Validation Error Examples")
    print("-" * 60)

    # Negative port (invalid)
    os.environ["PORT"] = "-1"
    try:
        AppSettings()
    except ValueError as e:
        print(f"✓ Negative port rejected: {e}")

    # Zero for PositiveInt (invalid)
    os.environ["PORT"] = "0"
    try:
        AppSettings()
    except ValueError as e:
        print(f"✓ Zero rejected for PositiveInt: {e}")

    # Zero for NonNegativeInt (valid!)
    os.environ["PORT"] = "8000"  # Valid again
    os.environ["RETRY_COUNT"] = "0"
    try:
        settings = AppSettings()
        print(f"✓ Zero allowed for NonNegativeInt: {settings.retry_count}")
    except ValueError as e:
        print(f"Unexpected error: {e}")

    print("\n" + "=" * 60)
    print("All validator examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
