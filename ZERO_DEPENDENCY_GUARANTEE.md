# Zero-Dependency Guarantee

**Drive4Wind is a WISDEM/WEIS plugin that guarantees ZERO impact on your host environment.**

## What This Means

When you run:
```bash
pip install git+https://github.com/ibrahim-hanif/Drive4Wind.git
```

**Nothing** will be installed except the Drive4Wind package itself (~1 MB). No scientific packages will be touched, modified, downgraded, or upgraded.

## Why This Works

### 1. **pyproject.toml** - Empty Dependencies
```toml
dependencies = []  # ← EMPTY - No packages required at install time
```

### 2. **setup.py** - No install_requires
```python
setup(
    name="Drive4Wind",
    packages=find_packages(),
    # ← NO install_requires or requires
)
```

### 3. **environment.yml** - Not Used by pip
The `environment.yml` file is **only for conda development environments**, not for pip installations.

### 4. **No Hidden Dependency Files**
- ✓ No `requirements.txt`
- ✓ No `setup.cfg` with dependencies
- ✓ No constraint files

## How It Works

Drive4Wind assumes the WISDEM/WEIS environment is already installed. It imports these at runtime:

```python
import numpy
import scipy
import openmdao
import matplotlib
```

If any are missing, you get a clear import error (not a silent install). This is intentional - it forces you to address the issue rather than silently modifying your environment.

## Verification

To verify this guarantee:

```bash
python verify_no_dependencies.py
```

Output:
```
RESULT: ✓ SUCCESS - Zero-dependency configuration verified!
Installing this package will NOT touch the host environment.
```

## Version Requirements

If you need to know what versions are compatible, check:
1. **README.md** - Lists required versions
2. **Drive4Wind/utils.py** - Contains version specs and validation

To validate your environment:
```python
from Drive4Wind.utils import validate_environment
validate_environment(verbose=True)
```

## Installation Options

### Option 1: Simple (Recommended)
```bash
# In wisdem-env, after WISDEM is installed
pip install git+https://github.com/ibrahim-hanif/Drive4Wind.git
```

### Option 2: From Local Folder
```bash
git clone https://github.com/ibrahim-hanif/Drive4Wind.git
cd Drive4Wind
pip install -e .  # Editable mode for development
```

### Option 3: With Development Tools (Optional)
```bash
pip install -e ".[dev]"  # Adds pytest, black, flake8
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'numpy'"
This means WISDEM is not installed. Install it first:
```bash
pip install wisdem
```

### Version Incompatibility Warning
Check environment compatibility:
```bash
python -m Drive4Wind.utils
```

## Support

This is a research plugin. If you encounter issues:
1. Verify WISDEM is installed: `python -c "import openmdao"`
2. Check version compatibility: `python -m Drive4Wind.utils`
3. Report issues on GitHub: https://github.com/ibrahim-hanif/Drive4Wind/issues

---

**Guarantee:** Drive4Wind will **never** install or modify packages in your host environment. It's a pure plugin.
