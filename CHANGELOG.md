# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2025-12-03

## [0.4.0] - 2025-12-03

### Added
- Custom `.env` parser implementation (117.5x faster than pydantic-settings)
- Zero-dependency .env file parsing (removed python-dotenv)
- Smart caching for .env files (169x faster on repeated loads)

### Changed
- **BREAKING**: Replaced python-dotenv with custom fast parser
- Updated benchmark results: 7x faster than pydantic-settings (Google Colab)
- Improved cold start performance: 0.353ms vs 2.47ms (pydantic)
- Enhanced warm load performance: 0.011ms vs 1.86ms (pydantic)

### Performance
- Cold start: **7.0x faster** than pydantic-settings
- Warm loads: **169x faster** than pydantic-settings
- .env parsing: **117.5x faster** than pydantic-settings

## [0.3.4] - 2025-12-02

### Fixed
- Minor bug fixes and stability improvements

## [0.3.3] - 2025-12-02

### Fixed
- Resolved publish workflow failures in CI/CD pipeline
- Fixed version extraction in release automation

## [0.3.2] - 2025-12-02

### Added
- CodeQL security scanning workflow
- Automatic PR labeling workflow
- Monthly pre-commit hook auto-update workflow

### Changed
- Aligned all GitHub Actions workflows with msgtrace-sdk standards
- Updated publish workflow to automatically create release tags
- Disabled labeler workflow for fork PRs (prevents failures)

### Fixed
- Fixed publish workflow version extraction (now uses grep instead of Python import)

## [0.3.1] - 2025-12-02

### Added
- `uv.lock` file for reproducible builds across environments

### Changed
- Improved dependency management with lock file

## [0.3.0] - 2025-12-02

### Added
- Comprehensive benchmark suite with statistical analysis
- Support for nested configuration via environment variables
- Detailed performance comparison documentation
- Example files demonstrating nested settings

### Changed
- Moved benchmark files to dedicated `/benchmark` directory
- Updated performance benchmarks: **3.8x faster** than pydantic-settings
- Enhanced benchmark with 10 runs and statistical validation
- Improved README with accurate, reproducible performance claims

### Fixed
- Merge-bot workflow now correctly handles PR branch checkouts
- Lint and formatting issues in benchmark code
- Field ordering in struct creation (required before optional)

## [0.2.0] - 2025-01-20

### Added
- Support for `Optional` fields with proper None handling
- JSON parsing for list and dict types from environment variables
- `model_dump()` method for serialization to dict
- `model_dump_json()` method for JSON serialization
- `schema()` method for JSON Schema generation

### Changed
- Improved type conversion for complex types
- Enhanced error messages for validation failures

### Fixed
- Boolean conversion edge cases (true/false/1/0/yes/no)
- Type handling for nested structures

## [0.1.0] - 2025-01-15

### Added
- Initial release of msgspec-ext
- `BaseSettings` class for environment-based configuration
- `.env` file support via python-dotenv
- Type validation using msgspec
- Support for common types: str, int, float, bool, list, dict
- Field prefixes (`env_prefix`) and delimiters (`env_nested_delimiter`)
- Case-sensitive and case-insensitive matching
- JSON schema generation
- Performance optimizations with bulk JSON decoding
- Comprehensive test suite (22 tests)
- Examples demonstrating basic usage, prefixes, .env files, and advanced types

### Performance
- **3.8x faster** than pydantic-settings in initial benchmarks
- Bulk validation in C via msgspec (zero Python loops)
- Cached encoders/decoders for repeated use

[Unreleased]: https://github.com/msgflux/msgspec-ext/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/msgflux/msgspec-ext/compare/v0.3.4...v0.4.0
[0.3.4]: https://github.com/msgflux/msgspec-ext/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/msgflux/msgspec-ext/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/msgflux/msgspec-ext/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/msgflux/msgspec-ext/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/msgflux/msgspec-ext/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/msgflux/msgspec-ext/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/msgflux/msgspec-ext/releases/tag/v0.1.0
