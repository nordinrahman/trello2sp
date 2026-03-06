# 🚀 **Trello to Super Productivity Migration Tool**

> **⚠️ WARNING**: Super Productivity import replaces ALL data. Always create multiple backups before proceeding!

## 📋 **Quick Start (5 Minutes)**

```bash
# 1. Export data (see detailed guide below)
#    - Trello: Menu → Share → Print and Export → Export JSON
#    - Super Productivity: Settings → Data Management → Export

# 2. Run migration
.venv\Scripts\Activate.ps1
cd src
python cli.py \
  --trello ../data/your-board.json \
  --sp-export ../data/sp-backup.json \
  --out-merged ../output/final-import.json

# 3. 🚨 BACKUP your Super Productivity data!
#    Make 2-3 copies before importing

# 4. Import into Super Productivity
#    Settings → Data Management → Import → final-import.json
```

## 🎯 **What It Does**

Transforms Trello board exports into Super Productivity format and merges with existing data:

| Trello → Super Productivity | Mapping |
|---------------------------|---------|
| Board → Project | Creates new project |
| List → Tag | "list:List Name" |
| Card → Task | With title, description, due date, tags |
| Checklist → Subtasks | Under parent task |
| Labels → Tags | Using label names |

---

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

## 🚨 **CRITICAL SAFETY WARNINGS**

### ⚠️ **SUPER PRODUCTIVITY IMPORT IS DESTRUCTIVE**
- **Importing replaces ALL existing data** in Super Productivity
- **No partial imports** - it's all or nothing
- **Always create multiple backups** before importing
- **Test imports on a copy** of your data first

### 🛡️ **BACKUP STRATEGY**
1. **Primary Backup**: Export current SP data → `sp_backup_before_import.json`
2. **Secondary Backup**: Copy to cloud storage (Google Drive, Dropbox, etc.)
3. **Tertiary Backup**: Keep original SP export untouched
4. **Test Environment**: Consider testing with a fresh SP installation

---

## 📋 **COMPLETE STEP-BY-STEP GUIDE**

### **Step 1: Prepare Your Data Exports**

#### **A. Export Super Productivity Data**
```
1. Open Super Productivity
2. Go to Settings → Data Management → Export
3. Choose "Complete Backup" 
4. Save as: data/super-productivity-backup.json
5. IMMEDIATELY make 2-3 copies of this file
```

#### **B. Export Trello Board**
```
1. Open your Trello board
2. Click "Share" button (top right)
3. Select "Print and Export"
4. Choose "Export as JSON"
5. Save as: data/your-board-name.json
6. Verify the file contains your cards, lists, labels
```

### **Step 2: Run Migration Tool**

#### **Basic Usage**
```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run migration
cd src
python cli.py \
  --trello ../data/your-board-name.json \
  --sp-export ../data/super-productivity-backup.json \
  --out-delta ../output/trello_project.json \
  --out-merged ../output/final_import.json \
  --project-title "Imported from Trello: Your Board Name"
```

#### **Dry Run Test (Recommended)**
```bash
python cli.py \
  --trello ../data/your-board-name.json \
  --sp-export ../data/super-productivity-backup.json \
  --dry-run
# Check the output summary before proceeding
```

### **Step 3: Verify Output Files**

#### **Check Migration Summary**
```
✅ Expected output:
Migration summary:
  Projects added: 1
  Tasks added:    [number]
  Subtasks added: [number] 
  Tags created:   [number] (reused: [number])
```

#### **Verify Files Created**
```bash
# Check output folder
ls ../output/
# Should see:
# - trello_project.json (delta file)
# - final_import.json (merged file)
```

#### **Validate JSON Structure**
```bash
# Quick validation (optional)
python -c "import json; print('Valid JSON' if json.load(open('../output/final_import.json')) else 'Invalid')"
```

### **Step 4: Import Process (High Risk)**

#### **🚨 PRE-IMPORT CHECKLIST**
- [ ] **Multiple backups created** (at least 2 copies)
- [ ] **Migration summary looks correct**
- [ ] **Output files validated**
- [ ] **Super Productivity is closed**
- [ ] **You have time to complete the process** (don't rush)

#### **Import Steps**
```
1. 🔄 Close Super Productivity completely
2. 📁 Open Super Productivity
3. ⚙️  Go to Settings → Data Management → Import
4. 📂 Select: output/final_import.json
5. ⚠️  CONFIRM: "This will replace all existing data"
6. 🚀 Click Import
7. ⏳ Wait for import to complete
8. ✅ Verify your tasks appeared correctly
```

#### **🆘 IF IMPORT FAILS**
```
1. 🚨 Don't panic - you have backups!
2. 📂 Import your original backup: data/super-productivity-backup.json
3. 🔍 Check error logs in Super Productivity
4. 🐛 Debug the migration tool output
5. 🔄 Try again with fixed migration
```

---

## 🎯 **TROUBLESHOOTING GUIDE**

### **Common Issues**

#### **Import Errors**
- **Problem**: "Cannot read properties of undefined (reading 'filter')"
- **Cause**: Invalid JSON structure
- **Solution**: Re-run migration with latest code

#### **Missing Tasks**
- **Problem**: Some tasks don't appear after import
- **Cause**: Archived cards excluded by default
- **Solution**: Use `--include-archived true`

#### **Duplicate Tags**
- **Problem**: Same tag appears multiple times
- **Cause**: Different capitalization or spacing
- **Solution**: Manually merge tags in Super Productivity

### **Validation Commands**

#### **Check Trello Export**
```bash
python -c "
import json
data = json.load(open('data/your-board-name.json'))
print(f'Cards: {len(data.get(\"cards\", []))}')
print(f'Lists: {len(data.get(\"lists\", []))}')
print(f'Labels: {len(data.get(\"labels\", []))}')
"
```

#### **Check SP Export**
```bash
python -c "
import json
data = json.load(open('data/super-productivity-backup.json'))
print(f'Tasks: {len(data[\"data\"][\"task\"][\"ids\"])}')
print(f'Projects: {len(data[\"data\"][\"project\"][\"ids\"])}')
print(f'Tags: {len(data[\"data\"][\"tag\"][\"ids\"])}')
"
```

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
