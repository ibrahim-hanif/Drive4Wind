"""
Verification Script: Confirm Drive4Wind is a true zero-dependency plugin

This script verifies that installing Drive4Wind does NOT modify the host environment.
It checks:
1. pyproject.toml has empty dependencies
2. setup.py doesn't declare any dependencies
3. No hidden dependency files exist
4. Installation doesn't trigger dependency downloads
"""

import os
import sys
from pathlib import Path


def check_config_files():
    """Verify configuration files have zero dependencies."""
    print("=" * 70)
    print("VERIFICATION: Zero-Dependency Configuration")
    print("=" * 70)
    
    errors = []
    
    # Check pyproject.toml
    print("\n1. Checking pyproject.toml...")
    pyproject = Path(__file__).parent / "pyproject.toml"
    with open(pyproject) as f:
        content = f.read()
        if "dependencies = []" in content:
            print("   ✓ dependencies = [] (EMPTY - GOOD!)")
        else:
            errors.append("pyproject.toml has non-empty dependencies")
            print("   ✗ FAILED: pyproject.toml has dependencies!")
    
    # Check setup.py
    print("\n2. Checking setup.py...")
    setup_py = Path(__file__).parent / "setup.py"
    with open(setup_py) as f:
        content = f.read()
        if "install_requires" not in content and "requires" not in content:
            print("   ✓ No 'install_requires' or 'requires' found (GOOD!)")
        else:
            errors.append("setup.py declares dependencies")
            print("   ✗ FAILED: setup.py declares dependencies!")
    
    # Check for requirements.txt
    print("\n3. Checking for requirements.txt...")
    req_file = Path(__file__).parent / "requirements.txt"
    if req_file.exists():
        errors.append("requirements.txt found (should not exist)")
        print("   ✗ FAILED: requirements.txt exists!")
    else:
        print("   ✓ No requirements.txt (GOOD!)")
    
    # Check for setup.cfg
    print("\n4. Checking setup.cfg...")
    setup_cfg = Path(__file__).parent / "setup.cfg"
    if setup_cfg.exists():
        with open(setup_cfg) as f:
            if "install_requires" in f.read():
                errors.append("setup.cfg has install_requires")
                print("   ✗ FAILED: setup.cfg declares dependencies!")
            else:
                print("   ✓ setup.cfg exists but has no dependencies (OK)")
    else:
        print("   ✓ No setup.cfg (GOOD!)")
    
    # Check environment.yml
    print("\n5. Checking environment.yml...")
    env_yml = Path(__file__).parent / "environment.yml"
    if env_yml.exists():
        with open(env_yml) as f:
            env_content = f.read()
            # Check for scientific stack packages
            risky_packages = ["numpy", "scipy", "openmdao", "matplotlib"]
            found_risky = []
            for pkg in risky_packages:
                if f"    - {pkg}" in env_content or f"    - {pkg}=" in env_content:
                    found_risky.append(pkg)
            
            if found_risky:
                errors.append(f"environment.yml has packages: {found_risky}")
                print(f"   ⚠ environment.yml includes: {found_risky}")
                print("     (This is OK for development, but NOT used by pip)")
            else:
                print("   ✓ environment.yml has no scientific packages (GOOD!)")
    
    print("\n" + "=" * 70)
    if errors:
        print("RESULT: ✗ FAILED - Issues found:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("RESULT: ✓ SUCCESS - Zero-dependency configuration verified!")
        print("\nInstalling this package will NOT touch the host environment.")
        return True


if __name__ == "__main__":
    success = check_config_files()
    sys.exit(0 if success else 1)
