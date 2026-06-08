"""
MBs4Wind: Main Bearing Design, Analysis and Optimization for Large Floating Offshore Wind Turbines

A Python package for main bearing design, analysis, and multi-disciplinary optimization 
of drivetrains in large floating offshore wind turbines.
"""

__version__ = "0.1.0"
__author__ = "Vasudev Gupta"
__email__ = "vasudev.gupta@ntnu.no"

# Import main modules
from . import mainbearings
from . import utilities
from . import data
from . import core

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "mainbearings",
    "utilities",
    "data",
    "core",
]
