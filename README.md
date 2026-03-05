# Trello to Super Productivity

A Python project for migrating tasks from Trello to Super Productivity.

## Project Information

- **Author**: Nordin Rahman
- **Contact**: nordin.rahman@gmail.com
- **License**: MIT License

## Project Structure

```
trello-to-super-productivity/
├── src/
│   ├── main.py
├── tests/
│   ├── unit/
│   │   └── test_main.py
│   ├── functional/
│   └── integration/
├── .venv/
├── pyproject.toml
├── LICENSE
└── README.md
```

## Setup

1. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Unix/MacOS
   source .venv/bin/activate
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Usage

Run the main application:
```bash
python -m src.main
# or after installation
trello-to-super-productivity
```

## IDE Configuration

The project is pre-configured for multiple IDEs:

### VS Code
- Python interpreter: `.venv/Scripts/python.exe`
- Source folders: `src`, `tests`
- Test runner: pytest
- Tasks: Run tests, coverage, mypy, black, isort
- Launch configurations: Current file, module, pytest, pytest with coverage

### PyCharm
- Python interpreter: `.venv/Scripts/python.exe`
- Source root: `src`
- Test source root: `tests`
- PYTHONPATH: includes `src`
- Run configurations: pytest, pytest with coverage

### Visual Studio
- Project file: `trello_to_super_productivity.pyproj`
- Python interpreter: `.venv\Scripts\python.exe`
- MSBuild targets: Test, TestWithCoverage, TypeCheck

## Development

- **Code formatting**: `black src/ tests/`
- **Import sorting**: `isort src/ tests/`
- **Type checking**: `mypy src/`
- **Linting**: `flake8 src/ tests/`
- **Testing**: `pytest`
- **Coverage**: `pytest --cov=src`

## Testing

Run all tests:
```bash
pytest
```

Run specific test categories:
```bash
pytest tests/unit/
pytest tests/functional/
pytest tests/integration/
```
