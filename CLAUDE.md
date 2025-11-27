# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Overview

**msgspec-ext** is a high-performance settings management library built on top of msgspec. It provides a pydantic-like API for loading settings from environment variables and .env files, with **3.8x better performance** than pydantic-settings.

## Project Structure

```
msgspec-ext/
├── src/msgspec_ext/       # Source code
│   ├── settings.py        # Core BaseSettings implementation
│   └── version.py         # Version string
├── tests/                 # Test suite
│   └── test_settings.py   # Comprehensive unit tests (22 tests)
├── examples/              # Practical examples
│   ├── 01_basic_usage.py
│   ├── 02_env_prefix.py
│   ├── 03_dotenv_file.py
│   ├── 04_advanced_types.py
│   ├── 05_serialization.py
│   └── README.md
├── scripts/               # Automation scripts
│   ├── release.sh         # Release automation (use this!)
│   └── setup-branch-protection.sh
└── benchmark.py           # Performance benchmarks

## Common Commands

### Development

```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --group dev

# Add new dependency
uv add <package>

# Run tests
uv run pytest tests/ -v

# Run specific test
uv run pytest tests/test_settings.py::test_name -v

# Run linter (only checks src/)
uv run ruff check src/

# Format code
uv run ruff format

# Run benchmark
uv run python benchmark.py
```

### Testing

All tests are in `tests/test_settings.py`:
- 22 comprehensive unit tests
- Tests cover: basic usage, env vars, type conversion, .env files, validation, serialization
- Run with: `uv run pytest tests/ -v`
- Should complete in < 0.1s

### Releases

**IMPORTANT**: Always use the release script:

```bash
# Create a new release
./scripts/release.sh <version>

# Example:
./scripts/release.sh 0.2.0
```

The script will:
1. Update `src/msgspec_ext/version.py`
2. Create git tag
3. Push to upstream
4. Trigger GitHub Actions for PyPI publishing

**Never manually edit version.py** - always use the release script!

## Architecture

### Core Implementation (`settings.py`)

**Key optimization**: Uses bulk JSON decoding instead of field-by-field validation.

```python
# Old approach (slow):
for field in fields:
    value = msgspec.convert(env_value, field_type)  # Python loop

# New approach (fast):
json_bytes = encoder.encode(all_values)  # Cached encoder
return decoder.decode(json_bytes)  # Cached decoder, all in C!
```

**Important classes**:
- `BaseSettings`: Wrapper factory that creates msgspec.Struct instances
- `SettingsConfigDict`: Configuration (env_file, env_prefix, etc.)

**Performance optimizations**:
- Cached encoders/decoders (ClassVar)
- Automatic field ordering (required before optional)
- Bulk JSON decoding in C
- Zero Python loops for validation

### Type Handling

Environment variables are always strings, but we need proper types:

```python
_preprocess_env_value(env_value: str, field_type: type) -> Any
```

Handles:
- `bool`: "true"/"false"/"1"/"0" → True/False
- `int`/`float`: String to number conversion
- `list`/`dict`: JSON parsing for complex types
- `Optional[T]`: Unwraps Union types correctly

### Field Ordering

`msgspec.defstruct` requires required fields before optional fields. We handle this automatically in `_create_struct_class()`:

```python
required_fields = [(name, type), ...]
optional_fields = [(name, type, default), ...]
fields = required_fields + optional_fields  # Correct order
```

## Linting & Code Style

**Ruff configuration** (`pyproject.toml`):
- Target: Python 3.10+
- Line length: 88
- Strict linting for `src/`
- Relaxed rules for `tests/` and `examples/`

**Running lint**:
```bash
# Check only src/ (recommended for quick checks)
uv run ruff check src/

# Check everything
uv run ruff check

# Auto-fix issues
uv run ruff check --fix

# Format code
uv run ruff format
```

**Important per-file ignores**:
- `tests/`: Ignores D (docstrings), S104 (binding), S105 (passwords), etc.
- `examples/`: Ignores D, S101, S104, S105, T201, F401
- `benchmark.py`: Ignores D, S101, S105, T201, etc.

## Examples

5 practical examples in `examples/`:
1. **Basic usage**: Defaults, env vars, explicit values
2. **Environment prefixes**: Organizing settings with `env_prefix`
3. **.env files**: Loading from dotenv files
4. **Advanced types**: Optional, lists, dicts, JSON parsing
5. **Serialization**: `model_dump()`, `model_dump_json()`, `schema()`

Run examples:
```bash
uv run python examples/01_basic_usage.py
```

## Benchmarking

```bash
uv run python benchmark.py
```

Expected results:
- msgspec-ext: ~0.7ms per load
- pydantic-settings: ~2.7ms per load (if installed)
- **Speedup**: 3.8x faster than pydantic-settings

## CI/CD

GitHub Actions workflows:
- **CI**: Runs on every push (Ruff, Tests, Build)
- **Publish**: Publishes to PyPI on new tags
- **Release Drafter**: Auto-generates release notes

**Creating a PR**:
1. Create feature branch from main
2. Make changes
3. Run tests: `uv run pytest tests/ -v`
4. Run lint: `uv run ruff check src/`
5. Format: `uv run ruff format`
6. Push and create PR
7. Ensure CI passes (Ruff, Tests, Build)

## Common Workflows

### Adding a new feature

1. Create branch: `git checkout -b feat/feature-name`
2. Implement feature in `src/msgspec_ext/settings.py`
3. Add tests in `tests/test_settings.py`
4. Add example in `examples/` (if user-facing)
5. Run tests: `uv run pytest tests/ -v`
6. Run lint: `uv run ruff check src/`
7. Create PR

### Fixing a bug

1. Add failing test in `tests/test_settings.py`
2. Fix bug in `src/msgspec_ext/settings.py`
3. Verify test passes
4. Run full test suite
5. Create PR

### Updating dependencies

```bash
# Update specific package
uv add package@latest

# Update all dependencies
uv sync --upgrade
```

## Performance Tips

- **Always use cached encoder/decoder**: Don't create new instances
- **Bulk operations**: Process all fields at once via JSON decode
- **Avoid Python loops**: Let msgspec handle validation in C
- **Field ordering**: Required before optional (automatic)
- **Type hints**: Proper annotations enable better performance

## Troubleshooting

**Tests failing**:
```bash
uv run pytest tests/ -v  # See detailed output
```

**Lint errors**:
```bash
uv run ruff check src/  # Check src only
uv run ruff check --fix  # Auto-fix
```

**Import errors**:
```bash
uv sync  # Reinstall dependencies
```

**Performance regression**:
```bash
uv run python benchmark.py  # Compare with baseline
```

## Key Files

- `src/msgspec_ext/settings.py` - Core implementation (most important)
- `src/msgspec_ext/version.py` - Version (updated by release script)
- `tests/test_settings.py` - Test suite (22 tests)
- `benchmark.py` - Performance benchmarks
- `scripts/release.sh` - Release automation (**use this for releases!**)
- `pyproject.toml` - Project config, dependencies, ruff settings

## Documentation

- `README.md` - User-facing docs with quickstart
- `examples/README.md` - Example gallery guide
- `CONTRIBUTING.md` - Contribution guidelines
- `CLAUDE.md` - This file (for Claude Code)

## Notes for Claude Code

- **Releases**: Always use `./scripts/release.sh <version>`, never edit version.py manually
- **Linting**: Focus on `src/` only (`uv run ruff check src/`)
- **Tests**: Must maintain 100% pass rate (22/22)
- **Performance**: Benchmark should show ~0.7ms per load, 3.8x vs pydantic
- **Examples**: Update if changing user-facing APIs
- **Breaking changes**: Require major version bump
