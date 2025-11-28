# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- .env file caching for massive performance gains (32x faster)
- Profiling script for identifying bottlenecks

### Changed
- Performance: Now 89x faster than pydantic-settings (up from 2.7x)
- Optimized .env file loading to parse only once per unique file

## [0.2.0] - 2025-11-27

### Added
- Comprehensive benchmark suite with statistical analysis
- Support for nested configuration via environment variables
- Improved documentation with accurate performance claims

### Changed
- Moved benchmark files to dedicated `/benchmark` directory
- Updated performance benchmarks: 2.7x faster than pydantic-settings
- Enhanced benchmark with 10 runs and statistical validation

### Fixed
- Merge-bot workflow now correctly handles PR branch checkouts
- Lint and formatting issues in benchmark code

## [0.1.0] - 2025-01-15

### Added
- Initial release
- BaseSettings class for environment-based configuration
- .env file support via python-dotenv
- Type validation using msgspec
- Support for common types: str, int, float, bool, list
- Field prefixes and delimiters
- Case-sensitive/insensitive matching
- JSON schema generation
- Performance optimizations with bulk JSON decoding
