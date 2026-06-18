# Drive4Wind

**An open toolbox for fatigue-reliability-aware design and optimization of geared wind turbine drivetrains**

result of the EU project Made4Wind

A Python package for main bearing design, analysis, and multi-disciplinary optimization of drivetrains in large floating offshore wind turbines.

## Features

- Main bearing design and sizing
- Structural analysis for drivetrain bearings
- Multi-disciplinary optimization framework
- Integration with OpenMDAO for MDAO workflows
- Comprehensive bearing analysis tools

## Installation

### Prerequisites

**Drive4Wind is a WISDEM/WEIS plugin.** It assumes you already have WISDEM installed with its complete scientific stack.

```bash
# Ensure WISDEM/WEIS is installed first
pip install wisdem
# or install from source
```

### Install Drive4Wind

Since Drive4Wind has **no enforced dependencies** (it relies on WISDEM's stack), installation is lightweight:

```bash
# From public GitHub repo
pip install git+https://github.com/ibrahim-hanif/Drive4Wind.git

# Or locally (editable mode for development)
git clone https://github.com/ibrahim-hanif/Drive4Wind.git
cd Drive4Wind
pip install -e .
```

**That's it!** No venv corruption, no dependency conflicts.

### Development Setup

```bash
# Install with development tools
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Check environment compatibility (optional)
python -m Drive4Wind.utils
```

## Requirements

Drive4Wind is a plugin module that **assumes** the WISDEM/WEIS environment provides these packages. Version requirements are documented but not enforced at install time:

### Required (provided by WISDEM)
- Python >= 3.9
- numpy >= 1.20.0
- scipy >= 1.7.0
- openmdao >= 3.0.0
- matplotlib >= 3.0.0

### Optional (for advanced optimization)
- nlopt >= 2.7.0
- pyoptsparse >= 2.0.0

### Version Validation

To check environment compatibility at runtime:

```python
from Drive4Wind.utils import validate_environment

# Verbose check
validate_environment(verbose=True)
```

This validation is optional and useful for debugging, but Drive4Wind does not enforce it at import time.

## Usage

## Quick Start

```python
import Drive4Wind

# Your code here
```

## Documentation

For more detailed documentation, visit the [wiki](https://github.com/yourusername/Drive4Wind/wiki).

## Testing

Run the test suite with:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use Drive4Wind in your research, please cite it as:

```
Gupta, V. (2026). Drive4Wind: Drivetrain design, analysis and optimization for floating offshore wind turbines. 
Retrieved from https://github.com/yourusername/Drive4Wind
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Authors

- **Vasudev Gupta** - vasudev.gupta@ntnu.no

## Acknowledgments

- Developed at NTNU (Norwegian University of Science and Technology), IMT (Dept. of Marine Technology)
- Built for [WISDEM](https://github.com/WISDEM/WISDEM) framework
- Uses [OpenMDAO](https://openmdao.org/) for multidisciplinary optimization
