"""Tests for Settings class."""

import pytest
from msgspec_ext import Settings


def test_settings_import():
    """Test that Settings can be imported."""
    assert Settings is not None
