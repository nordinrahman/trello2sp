# Trello to Super Productivity

A Python project for migrating tasks from Trello to Super Productivity.

## Overview

This tool transforms a Trello board export into a Super Productivity project and merges it into an existing SP export JSON file.

## Features

- **Complete Migration**: Transforms Trello boards, lists, cards, labels, checklists, and optionally members into Super Productivity format
- **Safe Merging**: Only adds new projects, tasks, and tags without modifying existing SP data
- **Deterministic**: Uses UUID4 for unique IDs, ensuring no collisions
- **Flexible Configuration**: CLI flags to control what gets migrated
- **Validation**: Built-in data validation to ensure SP compatibility

## Project Information

- **Author**: Nordin Rahman
- **Contact**: nordin.rahman@gmail.com
- **License**: MIT License

## Project Structure

```
trello-to-super-productivity/
├── src/
│   ├── __init__.py              # Package init
│   ├── main.py                  # Package entry point
│   ├── cli.py                   # CLI interface
│   └── migrator.py              # Migration logic
├── tests/
│   ├── unit/
│   │   └── test_main.py
│   ├── functional/
│   └── integration/
├── data/                        # Input files
├── output/                      # Generated files (git-ignored)
├── .venv/
├── pyproject.toml
├── LICENSE
└── README.md
```

## Migration Tool

### Mapping

| Trello Element | Super Productivity Element |
|---------------|---------------------------|
| Board | Project (title: "Imported from Trello: <Board Name>") |
| List | Tag (prefix: "list:<List Name>") |
| Label | Tag (uses label name) |
| Card | Task (with title, description, due date, tags) |
| Checklist Item | Subtask (under parent task) |
| Member | Optional tag (prefix: "@member:<Name>") |

### Usage

```bash
cd src && python cli.py \
  --trello ../data/trello_board.json \
  --sp-export ../data/sp_export.json \
  --out-delta ../output/sp_project_from_trello.json \
  --out-merged ../output/sp_import_merged.json \
  --project-title "Imported from Trello: My Board" \
  --include-archived false \
  --member-tags false \
  --list-tags true \
  --label-tags true \
  --dry-run false
```

### CLI Options

- `--trello`: Path to Trello board export JSON (required)
- `--sp-export`: Path to Super Productivity export JSON (required)
- `--out-delta`: Output path for delta JSON (just new project data)
- `--out-merged`: Output path for merged JSON (ready for SP import)
- `--project-title`: Custom title for the new project
- `--include-archived`: Include archived cards as completed tasks
- `--member-tags`: Create tags for Trello members
- `--list-tags`/`--no-list-tags`: Create tags for Trello lists (default: true)
- `--label-tags`/`--no-label-tags`: Create tags for Trello labels (default: true)
- `--reuse-project`: Merge into existing project with same title
- `--dry-run`: Run without writing files

### Output Files

1. **Delta File** (`output/sp_project_from_trello.json`): Contains only the new project data
2. **Merged File** (`output/sp_import_merged.json`): Complete SP export ready for import

### Import Process

1. **Export your current Super Productivity data**:
   - Open Super Productivity
   - Go to Settings → Data Management → Export
   - Save as `sp_export.json`

2. **Export your Trello board**:
   - Open Trello board
   - Go to Menu → More → Print and Export → Export JSON
   - Save as `trello_board.json`

3. **Run the migration tool**:
   ```bash
   cd src && python cli.py --trello ../trello_board.json --sp-export ../sp_export.json ...
   ```

4. **Import into Super Productivity**:
   - Open Super Productivity
   - Go to Settings → Data Management → Import
   - Select `sp_import_merged.json`
   - **IMPORTANT**: This will replace all in-app data

### Example Output

```
Migration summary:
  Projects added: 1
  Tasks added:    25
  Subtasks added: 47
  Tags created:   8 (reused: 3)
Output files: output/sp_project_from_trello.json, output/sp_import_merged.json
```

### Important Notes

#### ⚠️ Backup Required
Always export a backup from Super Productivity before importing, as SP replaces in-app data when importing.

#### Tag Deduplication
The tool automatically reuses existing tags with identical titles to prevent duplicates.

#### Project Naming
- Default: "Imported from Trello: <Board Name>"
- If a project with this title exists, " (Trello)" suffix is added
- Use `--reuse-project` to merge into existing project

#### Date Handling
- Trello ISO timestamps converted to YYYY-MM-DD format
- Invalid dates are ignored

#### Archived Cards
- Skipped by default
- Use `--include-archived` to include as completed tasks

## Setup

### Prerequisites

- Python 3.11 or higher
- Trello board export (JSON format)
- Super Productivity export (JSON format)

### Installation

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

## Development

### IDE Configuration

The project is pre-configured for multiple IDEs:

#### VS Code
- Python interpreter: `.venv/Scripts/python.exe`
- Source folders: `src`, `tests`
- Test runner: pytest
- Tasks: Run tests, coverage, mypy, black, isort
- Launch configurations: Current file, module, pytest, pytest with coverage

#### PyCharm
- Python interpreter: `.venv/Scripts/python.exe`
- Source root: `src`
- Test source root: `tests`
- PYTHONPATH: includes `src`
- Run configurations: pytest, pytest with coverage

#### Visual Studio
- Project file: `trello_to_super_productivity.pyproj`
- Python interpreter: `.venv\Scripts\python.exe`
- MSBuild targets: Test, TestWithCoverage, TypeCheck

### Code Quality

- **Code formatting**: `black src/ tests/`
- **Import sorting**: `isort src/ tests/`
- **Type checking**: `mypy src/`
- **Linting**: `flake8 src/ tests/`

### Testing

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

Run with coverage:
```bash
pytest --cov=src
```

## Troubleshooting

### Common Issues

1. **File not found**: Check file paths and ensure JSON files exist
2. **Invalid JSON**: Verify Trello/SP exports are valid JSON
3. **Missing data**: Ensure Trello export includes lists, cards, and labels
4. **Import fails**: Validate the merged JSON before importing

### Validation Errors

The tool includes built-in validation for:
- Required task fields
- Subtask references
- Project structure
- Tag consistency

## Technical Details

### ID Generation
- Uses UUID4 for all new entities
- Maintains reference integrity between tasks, subtasks, and projects
- No collisions with existing SP data

### Data Structure
Follows Super Productivity's AppBaseData format:
```json
{
  "project": { "ids": [...], "entities": {...} },
  "task": { "ids": [...], "entities": {...} },
  "tag": { "ids": [...], "entities": {...} },
  // ... other slices preserved unchanged
}
```

### Performance
- Processes data in memory for speed
- Minimal file I/O operations
- Efficient tag deduplication using hash maps

## License

MIT License - see LICENSE file for details.
