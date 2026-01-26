# Changelog

All notable changes to TITrack will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Phase 2: Web UI with FastAPI backend
- Phase 3: Price engine with import/export
- Phase 4: Net worth and profit/hour calculations
- Phase 5: PyInstaller portable EXE packaging

## [0.1.1] - 2026-01-26

### Fixed
- Level transition pattern updated to match actual game log format
  - Changed from `LevelMgr@ EnterLevel` to `SceneLevelMgr@ OpenMainWorld END!`
- Hub zone detection patterns expanded to include:
  - `/01SD/` (Ember's Rest hideout path)
  - `YuJinZhiXiBiNanSuo` (Ember's Rest Chinese name)

### Added
- Zone name mapping system (`data/zones.py`)
  - Maps internal Chinese pinyin zone names to English display names
  - `get_zone_display_name()` function for lookups
  - Extensible dictionary for user-added mappings
- CLI now displays English zone names in `show-runs` and `tail` output

### Verified
- Real-world testing with live game data
- Successfully tracked multiple map runs with accurate FE and loot tallies
- Run duration timing working correctly

## [0.1.0] - 2026-01-26

### Added

#### Core Infrastructure
- Project structure with `src/titrack/` layout
- `pyproject.toml` with dev dependencies (pytest, black, ruff)
- Comprehensive `.gitignore` for Python projects

#### Domain Models (`core/models.py`)
- `SlotKey` - Unique identifier for inventory slots
- `SlotState` - Current state of an inventory slot
- `ItemDelta` - Computed change in item quantity
- `Run` - Map/zone run with timestamps
- `Item` - Item metadata from database
- `Price` - Item valuation in FE
- `ParsedBagEvent` - Parsed BagMgr modification
- `ParsedContextMarker` - Parsed ItemChange start/end
- `ParsedLevelEvent` - Parsed level transition
- `EventContext` enum - PICK_ITEMS vs OTHER

#### Log Parser (`parser/`)
- `patterns.py` - Compiled regex for BagMgr, ItemChange, LevelMgr
- `log_parser.py` - Parse single lines to typed events
- `log_tailer.py` - Incremental file reading with:
  - Position tracking for resume
  - Log rotation detection
  - Partial line buffering

#### Delta Calculator (`core/delta_calculator.py`)
- Pure function computing deltas from state + events
- Handles new slots, quantity updates, item swaps
- In-memory state with load/save capability

#### Run Segmenter (`core/run_segmenter.py`)
- State machine tracking active run
- Hub zone detection (hideout, town, hub, lobby, social)
- EnterLevel triggers run transitions

#### Database Layer (`db/`)
- `schema.py` - DDL for 7 tables:
  - settings, runs, item_deltas, slot_state
  - items, prices, log_position
- `connection.py` - SQLite with WAL mode, transaction support
- `repository.py` - Full CRUD for all entities

#### Collector (`collector/collector.py`)
- Main orchestration loop
- Context tracking (inside PickItems block or not)
- Callbacks for deltas, run start/end
- File processing and live tailing modes

#### Configuration (`config/settings.py`)
- Auto-detect log file in common Steam locations
- Default DB path: `%LOCALAPPDATA%\TITrack\tracker.db`
- Portable mode support

#### CLI (`cli/commands.py`)
- `init` - Initialize database, optionally seed items
- `parse-file` - Parse log file (non-blocking)
- `tail` - Live tail with delta output
- `show-runs` - List recent runs with FE totals
- `show-state` - Display current inventory

#### Item Database
- `tlidb_items_seed_en.json` with 1,811 items
- Includes name_en, name_cn, icon URLs, TLIDB links

#### Test Suite (80 tests)
- Unit tests for all modules
- Integration tests for full collector workflow
- Sample log fixture for testing

### Technical Details
- Python 3.11+ required
- Zero runtime dependencies (stdlib only)
- SQLite WAL mode for concurrent access
- Position persistence for resume after restart
