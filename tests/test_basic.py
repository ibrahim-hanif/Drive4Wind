"""Basic tests for MBs4Wind"""
import pytest
import MBs4Wind


def test_import():
    """Test that MBs4Wind can be imported"""
    assert MBs4Wind.__version__ == "0.1.0"


def test_version():
    """Test version string"""
    assert isinstance(MBs4Wind.__version__, str)


def test_author():
    """Test author information"""
    assert MBs4Wind.__author__ == "Vasudev Gupta"
    assert MBs4Wind.__email__ == "vasudev.gupta@ntnu.no"
