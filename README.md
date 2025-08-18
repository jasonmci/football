# Football Formation Model

[![CI](https://github.com/YOUR_USERNAME/football/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/football/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/football/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/football)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python library for modeling football formations using a lane/depth grid system.

## Features

- **Type-safe** formation modeling with Python's type hints
- **Simple API** for building offensive and defensive formations
- **Comprehensive test coverage** (100%)
- **Continuous Integration** with GitHub Actions
- **Code quality** enforced with linting and formatting

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/football.git
cd football
pip install -r requirements-dev.txt
```

## Quick Start

```python
from src.formation_model import OffFormation, DefFormation, o, d

# Create formations
offense = OffFormation()
defense = DefFormation()

# Build an offensive formation
o(offense, "left", "line", 1)      # Left tackle
o(offense, "middle", "line", 3)    # Center and guards  
o(offense, "right", "line", 1)     # Right tackle
o(offense, "middle", "backfield", 1) # Running back
o(offense, "left", "wide", 1)      # Left receiver
o(offense, "right", "wide", 1)     # Right receiver

# Build a defensive formation
d(defense, "left", "line", 1)      # Left end
d(defense, "middle", "line", 2)    # Defensive tackles
d(defense, "right", "line", 1)     # Right end
d(defense, "left", "box", 1)       # Left linebacker
d(defense, "middle", "box", 2)     # Middle linebackers
d(defense, "right", "box", 1)      # Right linebacker
d(defense, "left", "deep", 1)      # Left safety/corner
d(defense, "middle", "deep", 1)    # Safety
d(defense, "right", "deep", 1)     # Right safety/corner

print(f"Offensive players: {sum(offense.counts.values())} + QB")
print(f"Defensive players: {sum(defense.counts.values())}")
```

## Formation System

The formation model uses a **lane/depth grid** system:

### Lanes
- `"left"` - Left side of the field
- `"middle"` - Center of the field  
- `"right"` - Right side of the field

### Offensive Depths
- `"line"` - Line of scrimmage (offensive line)
- `"backfield"` - Behind the line (RBs, FB)
- `"wide"` - Wide receivers/tight ends

### Defensive Depths
- `"line"` - Defensive line
- `"box"` - Linebacker level
- `"deep"` - Secondary (safeties, corners)

## Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m coverage run -m pytest tests/
python -m coverage report -m
```

### Code Quality

```bash
# Format code
python -m black src/ tests/

# Lint code
python -m flake8 src/ tests/

# Type checking
python -m mypy src/ --ignore-missing-imports
```

### Project Structure

```
football/
├── src/
│   ├── __init__.py
│   └── formation_model.py    # Core formation classes and functions
├── tests/
│   ├── __init__.py
│   └── test_formation_model.py  # Comprehensive test suite
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI/CD
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── pyproject.toml          # Tool configuration
├── .flake8                 # Flake8 configuration
└── README.md
```

## CI/CD Pipeline

The project uses GitHub Actions for:

- **Multi-version testing** (Python 3.9, 3.10, 3.11, 3.12)
- **Code formatting** with Black
- **Linting** with Flake8
- **Type checking** with MyPy
- **Test coverage** reporting with Codecov
- **Automated testing** on push and pull requests

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`python -m pytest && python -m black src/ tests/ && python -m flake8 src/ tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.