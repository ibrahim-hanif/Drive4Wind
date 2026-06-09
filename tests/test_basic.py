"""Basic tests for Drive4Wind"""
import pytest
import Drive4Wind


def test_import():
    """Test that Drive4Wind can be imported"""
    assert Drive4Wind.__version__ == "0.1.0"


def test_version():
    """Test version string"""
    assert isinstance(Drive4Wind.__version__, str)


def test_author():
    """Test author information"""
    assert Drive4Wind.__author__ == "Vasudev Gupta"
    assert Drive4Wind.__email__ == "vasudev.gupta@ntnu.no"
