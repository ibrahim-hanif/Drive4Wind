"""Version validation utilities for Drive4Wind

This module provides optional runtime version checking for required dependencies.
Drive4Wind assumes WISDEM/WEIS host environment provides the scientific stack.
This is useful for detecting compatibility issues at import time.
"""

from packaging import version as pkg_version


# Required package versions (documented requirements, not enforced)
REQUIRED_VERSIONS = {
    "numpy": ">=1.20.0",
    "scipy": ">=1.7.0",
    "openmdao": ">=3.0.0",
    "matplotlib": ">=3.0.0",
}

OPTIONAL_VERSIONS = {
    "nlopt": ">=2.7.0",
    "pyoptsparse": ">=2.0.0",
}


def check_version(package_name, required_spec):
    """
    Check if an installed package meets the version specification.
    
    Parameters
    ----------
    package_name : str
        Name of the package to check
    required_spec : str
        Version specification (e.g., ">=1.20.0")
    
    Returns
    -------
    bool
        True if package meets spec, False otherwise
    
    Raises
    ------
    ImportError
        If package is not installed
    """
    try:
        mod = __import__(package_name)
        installed = pkg_version.parse(mod.__version__)
        spec = pkg_version.Specifier(required_spec)
        return installed in spec
    except ImportError:
        raise ImportError(f"Package '{package_name}' not found. "
                         f"Please install WISDEM/WEIS with required dependencies.")


def validate_environment(verbose=False):
    """
    Validate that the host environment has compatible versions.
    
    Parameters
    ----------
    verbose : bool, optional
        If True, print version information for all packages
    
    Returns
    -------
    dict
        Dictionary with validation results for each package
    
    Notes
    -----
    This is optional and can be called at runtime if desired.
    Drive4Wind does not enforce this at import time.
    """
    results = {}
    
    # Check required packages
    for pkg, spec in REQUIRED_VERSIONS.items():
        try:
            mod = __import__(pkg)
            meets_spec = check_version(pkg, spec)
            results[pkg] = {
                "installed": True,
                "version": mod.__version__,
                "required": spec,
                "compatible": meets_spec,
            }
            if verbose:
                status = "✓" if meets_spec else "✗"
                print(f"{status} {pkg}: {mod.__version__} (required: {spec})")
        except ImportError:
            results[pkg] = {
                "installed": False,
                "version": None,
                "required": spec,
                "compatible": False,
            }
            if verbose:
                print(f"✗ {pkg}: NOT INSTALLED (required: {spec})")
    
    # Check optional packages
    for pkg, spec in OPTIONAL_VERSIONS.items():
        try:
            mod = __import__(pkg)
            meets_spec = check_version(pkg, spec)
            results[pkg] = {
                "installed": True,
                "version": mod.__version__,
                "required": spec,
                "compatible": meets_spec,
                "optional": True,
            }
            if verbose:
                status = "✓" if meets_spec else "⚠"
                print(f"{status} {pkg}: {mod.__version__} (optional, required: {spec})")
        except ImportError:
            results[pkg] = {
                "installed": False,
                "version": None,
                "required": spec,
                "compatible": False,
                "optional": True,
            }
            if verbose:
                print(f"⚠ {pkg}: NOT INSTALLED (optional, required: {spec})")
    
    return results


if __name__ == "__main__":
    # Test: python -m Drive4Wind.utils.version
    print("Drive4Wind Environment Validation")
    print("=" * 50)
    validate_environment(verbose=True)
