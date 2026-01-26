# TITrack - Torchlight Infinite Local Loot Tracker

A privacy-focused, fully local Windows desktop application that tracks loot from Torchlight Infinite by parsing game log files. Calculate profit per map run, track net worth, and analyze your farming efficiency.

Inspired by [WealthyExile](https://github.com/WealthyExile) for Path of Exile.

## Current Status: Phase 1 Complete ✓

**Phase 1 (Foundation)** implements the core log parsing and database infrastructure:

| Component | Status | Description |
|-----------|--------|-------------|
| Log Parser | ✓ Complete | Regex-based parsing of BagMgr, ItemChange, SceneLevelMgr events |
| Delta Calculator | ✓ Complete | Computes inventory changes from absolute stack counts |
| Run Segmenter | ✓ Complete | Detects map vs hub zones, tracks run boundaries |
| Database Layer | ✓ Complete | SQLite with WAL mode, full CRUD repository |
| Log Tailer | ✓ Complete | Incremental file reading with position persistence |
| Collector | ✓ Complete | Orchestrates parsing, computation, and storage |
| CLI | ✓ Complete | Commands for init, parse, tail, show-runs, show-state |
| Item Database | ✓ Complete | 1,811 items seeded from TLIDB |
| Test Suite | ✓ Complete | 80 unit + integration tests passing |

### What Works Now

- Parse game log files and extract item pickup events
- Track Flame Elementium (FE) gains per map run
- Detect run boundaries (entering/leaving maps vs hubs)
- Persist all data to local SQLite database
- Resume tracking from last position after restart
- Display inventory state and run history via CLI
- Zone name mapping (internal Chinese names → English display names)

**Tested with live game data** - successfully tracked multiple map runs with accurate FE and loot tallies.

### What's Planned (Future Phases)

- **Phase 2**: Web UI with FastAPI backend
- **Phase 3**: Price engine with manual editing and import/export
- **Phase 4**: Net worth calculation and profit/hour metrics
- **Phase 5**: PyInstaller packaging for portable EXE distribution

## Installation

### Prerequisites

- Python 3.11 or higher
- Windows 10/11
- Torchlight Infinite installed via Steam

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd TITrack

# Install in development mode
pip install -e ".[dev]"

# Initialize database and seed items
python -m titrack init --seed tlidb_items_seed_en.json
```

## Usage

### CLI Commands

```bash
# Initialize database (first time setup)
python -m titrack init --seed tlidb_items_seed_en.json

# Parse an existing log file
python -m titrack parse-file "path/to/UE_game.log"

# Live tail the log file (Ctrl+C to stop)
python -m titrack tail "path/to/UE_game.log"

# Show recent runs with FE gains
python -m titrack show-runs

# Show current inventory state
python -m titrack show-state
```

### Options

```bash
--db PATH       # Custom database path (default: %LOCALAPPDATA%\TITrack\tracker.db)
--portable      # Use portable mode (data stored beside executable)
```

### Log File Location

The game log is typically located at:
```
C:\Program Files (x86)\Steam\steamapps\common\Torchlight Infinite\UE_Game\Torchlight\Saved\Logs\UE_game.log
```

The CLI will auto-detect common Steam library locations.

## Example Output

```
$ python -m titrack parse-file UE_game.log

=== Entered: MainHub_Social (hub) ===
  +500 Flame Elementium

=== Entered: Map_Desert_T16_001 ===
  +50 Flame Elementium [PICK_ITEMS]
  +75 Flame Elementium [PICK_ITEMS]
  +3 Ember Crystal [PICK_ITEMS]

--- Run ended: 4m 32s ---
  FE gained: 200
  +3 Ember Crystal

$ python -m titrack show-runs

Recent Runs (last 5):
------------------------------------------------------------
  #  5 [hub] MainHub_Social                     active FE: +0
  #  4 Map_Forest_T14_002                  3m 15s FE: +150
  #  3 [hub] MainHub_Social                      0m 45s FE: +0
  #  2 Map_Desert_T16_001                  4m 32s FE: +200
  #  1 [hub] MainHub_Social                      1m 20s FE: +0
------------------------------------------------------------

$ python -m titrack show-state

Current Inventory:
----------------------------------------
      1250 Flame Elementium (FE)
        12 Ember Crystal
         5 Divine Orb
----------------------------------------
Total item types: 3
```

## Project Structure

```
TITrack/
├── src/titrack/
│   ├── __init__.py              # Package version
│   ├── __main__.py              # Entry point
│   ├── core/                    # Pure domain logic (no I/O)
│   │   ├── models.py            # Dataclasses: ItemDelta, SlotState, Run
│   │   ├── delta_calculator.py  # Compute deltas from slot state
│   │   └── run_segmenter.py     # Track run boundaries
│   ├── parser/
│   │   ├── patterns.py          # Compiled regex patterns
│   │   ├── log_parser.py        # Parse lines to typed events
│   │   └── log_tailer.py        # Incremental file reading
│   ├── db/
│   │   ├── schema.py            # SQLite DDL statements
│   │   ├── connection.py        # Database connection (WAL mode)
│   │   └── repository.py        # CRUD operations
│   ├── collector/
│   │   └── collector.py         # Main orchestration loop
│   ├── config/
│   │   └── settings.py          # Configuration and auto-detection
│   └── cli/
│       └── commands.py          # CLI command implementations
├── tests/
│   ├── fixtures/                # Sample log files
│   ├── unit/                    # Unit tests (74 tests)
│   └── integration/             # Integration tests (6 tests)
├── pyproject.toml               # Project configuration
├── tlidb_items_seed_en.json     # Item database (1,811 items)
├── CLAUDE.md                    # AI assistant instructions
└── TI_Local_Loot_Tracker_PRD.md # Product requirements document
```

## Architecture

### Data Flow

```
Game Log File
      │
      ▼
┌─────────────┐
│ Log Tailer  │  ← Incremental reading, position tracking
└─────────────┘
      │
      ▼
┌─────────────┐
│ Log Parser  │  ← Regex matching, typed event creation
└─────────────┘
      │
      ▼
┌─────────────┐
│ Collector   │  ← Context tracking, orchestration
└─────────────┘
      │
      ├──────────────────┐
      ▼                  ▼
┌─────────────┐   ┌──────────────┐
│   Delta     │   │     Run      │
│ Calculator  │   │  Segmenter   │
└─────────────┘   └──────────────┘
      │                  │
      └────────┬─────────┘
               ▼
        ┌─────────────┐
        │  Repository │  ← SQLite persistence
        └─────────────┘
```

### Key Concepts

- **Flame Elementium (FE)**: Primary currency, ConfigBaseId = `100300`
- **ConfigBaseId**: Integer item type identifier from game logs
- **Delta**: Change in quantity (current - previous) for a slot
- **SlotState**: Current `(ConfigBaseId, Num)` for each `(PageId, SlotId)`
- **Run**: Time period in a single zone, bounded by OpenMainWorld events
- **Context**: Whether an item change occurred during PickItems (loot) or other actions

### Database Schema

| Table | Purpose |
|-------|---------|
| `settings` | Key/value configuration |
| `runs` | Map run records with timestamps |
| `item_deltas` | Per-item quantity changes |
| `slot_state` | Current inventory state |
| `items` | Item metadata (name, icon, etc.) |
| `prices` | Item valuations in FE |
| `log_position` | File position for resume |

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=titrack --cov-report=html

# Run specific test file
pytest tests/unit/test_delta_calculator.py -v
```

### Code Quality

```bash
# Format code
black .

# Lint
ruff check .
```

### Test Coverage

All 80 tests passing:
- `test_patterns.py` - Regex pattern matching
- `test_log_parser.py` - Line parsing to typed events
- `test_delta_calculator.py` - Inventory change computation
- `test_run_segmenter.py` - Run boundary detection
- `test_log_tailer.py` - File reading and position tracking
- `test_repository.py` - Database CRUD operations
- `test_collector.py` - Full integration tests

## Design Principles

1. **Privacy First**: All data stored locally, no network calls
2. **No Cheating**: Only reads log files, no memory hooks or game modification
3. **Pure Core**: Domain logic has no I/O, easy to test
4. **Incremental Processing**: Resume from last position, handle log rotation
5. **Zero Runtime Dependencies**: Phase 1 uses only Python stdlib

## Log Format Reference

The parser recognizes these log patterns:

```
# Item pickup block
GameLog: Display: [Game] ItemChange@ ProtoName=PickItems start
GameLog: Display: [Game] BagMgr@:Modfy BagItem PageId = 102 SlotId = 0 ConfigBaseId = 100300 Num = 671
GameLog: Display: [Game] ItemChange@ ProtoName=PickItems end

# Level transitions (actual game format)
SceneLevelMgr@ OpenMainWorld END! InMainLevelPath = /Game/Art/Maps/01SD/XZ_YuJinZhiXiBiNanSuo200/...
```

## Zone Name Mapping

Internal map paths use Chinese pinyin names. Edit `src/titrack/data/zones.py` to add English mappings:

```python
ZONE_NAMES = {
    "XZ_YuJinZhiXiBiNanSuo": "Hideout - Ember's Rest",
    "KD_YuanSuKuangDong": "Elemental Cave",
    # Add more as you discover them
}
```

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please:
1. Run tests before submitting PRs
2. Follow existing code style (black, ruff)
3. Add tests for new functionality
