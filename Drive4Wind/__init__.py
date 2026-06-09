"""
Drive4Wind: Main Bearing Design, Analysis and Optimization for Large Floating Offshore Wind Turbines

A Python package for main bearing design, analysis, and multi-disciplinary optimization 
of drivetrains in large floating offshore wind turbines.
"""

__version__ = "0.1.0"
__author__ = "Vasudev Gupta"
__email__ = "vasudev.gupta@ntnu.no"

# Lazy imports to avoid circular import issues
def __getattr__(name):
    if name == "mainbearings":
        from . import mainbearings
        return mainbearings
    elif name == "utilities":
        from . import utilities
        return utilities
    elif name == "data":
        from . import data
        return data
    elif name == "core":
        from . import core
        return core
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "mainbearings",
    "utilities",
    "data",
    "core",
]
