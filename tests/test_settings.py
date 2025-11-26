"""Tests for BaseSettings class."""

from msgspec_ext import BaseSettings


def test_settings_import():
    """Test that BaseSettings can be imported."""
    assert BaseSettings is not None
