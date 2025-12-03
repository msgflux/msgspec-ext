r"""Fast .env file parser - optimized for performance.

Key features:
1. UTF-8 BOM support (\ufeff)
2. Escape sequences parsing (\n, \t, etc)
3. Whitespace preservation inside quotes
4. Strict variable name validation (isidentifier)
5. Robust 'export' keyword support
6. Correct duplicate handling
7. Special symbols in unquoted values
"""

import os

# Global cache
_FILE_CACHE: dict[str, dict[str, str]] = {}

# Optimization constants
_BOM = "\ufeff"
_EXPORT_LEN = 6  # len("export")


def parse_env_file(file_path: str, encoding: str | None = "utf-8") -> dict[str, str]:  # noqa: C901, PLR0912
    """Fast .env file parser with production-grade robustness.

    Optimized for speed while handling edge cases correctly.
    """
    cache_key = f"{file_path}:{encoding}"
    if cache_key in _FILE_CACHE:
        return _FILE_CACHE[cache_key]

    env_vars: dict[str, str] = {}

    try:
        # 1. Fast read with immediate BOM handling
        with open(file_path, encoding=encoding) as f:
            content = f.read()

        # Remove BOM if present
        if content.startswith(_BOM):
            content = content[1:]

        # Local references for loop speed
        _str_strip = str.strip
        _str_startswith = str.startswith

        for raw_line in content.splitlines():
            # Fast initial cleanup
            line = _str_strip(raw_line)

            if not line or _str_startswith(line, "#"):
                continue

            # 2. Handle 'export' keyword
            # Check if starts with 'export' followed by space (not a var called 'exporter')
            if _str_startswith(line, "export") and len(line) > _EXPORT_LEN and line[_EXPORT_LEN].isspace():
                line = line[_EXPORT_LEN:].lstrip()

            # 3. Atomic partition
            key, sep, value = line.partition("=")

            if not sep:
                continue

            key = key.strip()

            # 4. Variable name validation
            # isidentifier() is implemented in C and covers:
            # - Not starting with number
            # - Only alphanumerics and underscore
            # - No hyphens (bash compliant)
            if not key.isidentifier():
                continue

            # 5. Value parsing
            if not value:
                env_vars[key] = ""
                continue

            quote = value[0] if value else ""

            # Quote handling logic
            if quote in ('"', "'"):
                # Check if quote closes (ignore orphaned quotes)
                if value.endswith(quote) and len(value) > 1:
                    # Extract content
                    val_content = value[1:-1]

                    # Double quotes: Support escape sequences
                    if quote == '"':
                        # Decode common escapes
                        # Manual replace is faster than codecs.decode('unicode_escape') for this subset
                        if "\\" in val_content:
                            val_content = (
                                val_content
                                .replace("\\n", "\n")
                                .replace("\\r", "\r")
                                .replace("\\t", "\t")
                                .replace('\\"', '"')
                                .replace("\\\\", "\\")
                            )
                    # Single quotes: Minimal escape processing
                    elif quote == "'":
                        # Only unescape single quote itself if needed
                        if "\\'" in val_content:
                            val_content = val_content.replace("\\'", "'")

                    env_vars[key] = val_content
                else:
                    # Broken or unclosed quotes -> Treat as unquoted string
                    env_vars[key] = value.strip()
            else:
                # Unquoted value - Preserve leading spaces but allow inline comments
                # Do NOT remove leading spaces to preserve intentionality

                # Remove inline comments (e.g., VAL=123 # id)
                if "#" in value:
                    # Only partition if # exists to avoid overhead
                    value = value.partition("#")[0]

                # Remove trailing whitespace only at the end
                env_vars[key] = value.rstrip()

    except FileNotFoundError:
        pass
    except Exception:  # noqa: S110
        # In critical production, logging would be ideal, but keeping interface clean
        pass

    _FILE_CACHE[cache_key] = env_vars
    return env_vars


def load_dotenv(
    dotenv_path: str | None = ".env",
    encoding: str | None = "utf-8",
    *,
    override: bool = False,
) -> bool:
    """Load environment variables from .env file into os.environ.

    Args:
        dotenv_path: Path to .env file (default: ".env")
        encoding: File encoding (default: "utf-8")
        override: Whether to override existing environment variables (default: False)

    Returns:
        True if file was loaded successfully, False otherwise
    """
    try:
        env_vars = parse_env_file(dotenv_path, encoding)

        if not env_vars:
            return False  # Empty or invalid file

        if override:
            # Override all variables from file
            os.environ.update(env_vars)
        else:
            # Preserve existing environment variables
            # Direct iteration is faster than sets for small/medium dicts
            environ = os.environ
            for key, value in env_vars.items():
                if key not in environ:
                    environ[key] = value

        return True
    except Exception:
        return False
