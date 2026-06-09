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

### From source

```bash
git clone https://github.com/yourusername/MBs4Wind.git
cd MBs4Wind
pip install -e .
```

### With optional dependencies

```bash
# Include WISDEM integration
pip install -e ".[wisdem]"

# Include pyoptsparse optimizer
pip install -e ".[pyoptsparse]"

# Development environment
pip install -e ".[dev]"

# All extras
pip install -e ".[wisdem,pyoptsparse,dev]"
```

## Requirements

- Python >= 3.9
- numpy >= 1.20.0
- scipy >= 1.7.0
- openmdao >= 3.0.0
- matplotlib >= 3.0.0
- nlopt >= 2.7.0

## Quick Start

```python
import MBs4Wind

# Your code here
```

## Documentation

For more detailed documentation, visit the [wiki](https://github.com/yourusername/MBs4Wind/wiki).

## Testing

Run the test suite with:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use MBs4Wind in your research, please cite it as:

```
Gupta, V. (2026). MBs4Wind: Main bearing design, analysis and optimization for floating offshore wind turbines. 
Retrieved from https://github.com/yourusername/MBs4Wind
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Authors

- **Vasudev Gupta** - vasudev.gupta@ntnu.no

## Acknowledgments

- Developed at NTNU (Norwegian University of Science and Technology)
- Built for [WISDEM](https://github.com/WISDEM/WISDEM) framework
- Uses [OpenMDAO](https://openmdao.org/) for multidisciplinary optimization
