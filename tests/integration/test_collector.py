"""Integration tests for the collector."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from titrack.collector.collector import Collector
from titrack.core.models import ItemDelta, Run
from titrack.db.connection import Database
from titrack.db.repository import Repository
from titrack.parser.patterns import FE_CONFIG_BASE_ID


SAMPLE_LOG = """\
[2026.01.26-10.00.00:000][  0]LogLevel: LevelMgr@ EnterLevel MainHub_Social
[2026.01.26-10.00.05:000][  0]GameLog: Display: [Game] BagMgr@:Modfy BagItem PageId = 102 SlotId = 0 ConfigBaseId = 100300 Num = 500
[2026.01.26-10.01.00:000][  0]LogLevel: LevelMgr@ EnterLevel Map_Desert_T16_001
[2026.01.26-10.01.30:000][  0]GameLog: Display: [Game] ItemChange@ ProtoName=PickItems start
[2026.01.26-10.01.30:001][  0]GameLog: Display: [Game] BagMgr@:Modfy BagItem PageId = 102 SlotId = 0 ConfigBaseId = 100300 Num = 550
[2026.01.26-10.01.30:002][  0]GameLog: Display: [Game] ItemChange@ ProtoName=PickItems end
[2026.01.26-10.02.00:000][  0]GameLog: Display: [Game] ItemChange@ ProtoName=PickItems start
[2026.01.26-10.02.00:001][  0]GameLog: Display: [Game] BagMgr@:Modfy BagItem PageId = 102 SlotId = 0 ConfigBaseId = 100300 Num = 625
[2026.01.26-10.02.00:002][  0]GameLog: Display: [Game] BagMgr@:Modfy BagItem PageId = 102 SlotId = 1 ConfigBaseId = 200100 Num = 3
[2026.01.26-10.02.00:003][  0]GameLog: Display: [Game] ItemChange@ ProtoName=PickItems end
[2026.01.26-10.03.00:000][  0]GameLog: Display: [Game] ItemChange@ ProtoName=PickItems start
[2026.01.26-10.03.00:001][  0]GameLog: Display: [Game] BagMgr@:Modfy BagItem PageId = 102 SlotId = 0 ConfigBaseId = 100300 Num = 700
[2026.01.26-10.03.00:002][  0]GameLog: Display: [Game] ItemChange@ ProtoName=PickItems end
[2026.01.26-10.05.00:000][  0]LogLevel: LevelMgr@ EnterLevel MainHub_Social
"""


@pytest.fixture
def test_env():
    """Create a test environment with temp log file and database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create log file
        log_path = tmpdir / "test.log"
        log_path.write_text(SAMPLE_LOG)

        # Create database
        db_path = tmpdir / "test.db"
        db = Database(db_path)
        db.connect()

        yield {
            "tmpdir": tmpdir,
            "log_path": log_path,
            "db_path": db_path,
            "db": db,
        }

        db.close()


class TestCollectorIntegration:
    """Integration tests for full collector workflow."""

    def test_process_sample_log(self, test_env):
        """Test processing the sample log file."""
        db = test_env["db"]
        log_path = test_env["log_path"]

        deltas_received = []
        runs_started = []
        runs_ended = []

        collector = Collector(
            db=db,
            log_path=log_path,
            on_delta=lambda d: deltas_received.append(d),
            on_run_start=lambda r: runs_started.append(r),
            on_run_end=lambda r: runs_ended.append(r),
        )
        collector.initialize()
        line_count = collector.process_file(from_beginning=True)

        # Verify lines processed
        assert line_count > 0

        # Verify runs detected
        assert len(runs_started) >= 3  # Hub, Map, Hub

        # Verify deltas detected
        assert len(deltas_received) > 0

    def test_fe_tracking(self, test_env):
        """Test that FE gains are tracked correctly."""
        db = test_env["db"]
        log_path = test_env["log_path"]
        repo = Repository(db)

        collector = Collector(db=db, log_path=log_path)
        collector.initialize()
        collector.process_file(from_beginning=True)

        # Get inventory summary
        inventory = collector.get_inventory_summary()

        # We should have FE tracked
        # Initial 500, then gains of 50, 75, 75 = 700 final
        assert FE_CONFIG_BASE_ID in inventory
        assert inventory[FE_CONFIG_BASE_ID] == 700

    def test_run_segmentation(self, test_env):
        """Test that runs are properly segmented."""
        db = test_env["db"]
        log_path = test_env["log_path"]
        repo = Repository(db)

        collector = Collector(db=db, log_path=log_path)
        collector.initialize()
        collector.process_file(from_beginning=True)

        runs = repo.get_recent_runs(limit=10)

        # Should have runs for: Hub, Map, Hub
        assert len(runs) >= 3

        # Find the map run
        map_runs = [r for r in runs if not r.is_hub]
        assert len(map_runs) >= 1

        # The map run should have the FE deltas
        map_run = map_runs[0]
        summary = repo.get_run_summary(map_run.id)
        assert FE_CONFIG_BASE_ID in summary
        # Deltas during map run: 50 + 75 + 75 = 200
        assert summary[FE_CONFIG_BASE_ID] == 200

    def test_slot_state_persistence(self, test_env):
        """Test that slot state is persisted to database."""
        db = test_env["db"]
        log_path = test_env["log_path"]
        repo = Repository(db)

        collector = Collector(db=db, log_path=log_path)
        collector.initialize()
        collector.process_file(from_beginning=True)

        # Get slot state from DB
        states = repo.get_all_slot_states()
        assert len(states) >= 2  # FE slot and item slot

        # Verify FE slot state
        fe_state = repo.get_slot_state(102, 0)
        assert fe_state is not None
        assert fe_state.config_base_id == FE_CONFIG_BASE_ID
        assert fe_state.num == 700

    def test_resume_from_position(self, test_env):
        """Test resuming collection from saved position."""
        db = test_env["db"]
        log_path = test_env["log_path"]

        # First run
        collector1 = Collector(db=db, log_path=log_path)
        collector1.initialize()
        collector1.process_file(from_beginning=True)

        # Add more content to log
        with open(log_path, "a") as f:
            f.write(
                "[2026.01.26-10.10.00:000][  0]GameLog: Display: [Game] ItemChange@ ProtoName=PickItems start\n"
            )
            f.write(
                "[2026.01.26-10.10.00:001][  0]GameLog: Display: [Game] BagMgr@:Modfy BagItem PageId = 102 SlotId = 0 ConfigBaseId = 100300 Num = 800\n"
            )
            f.write(
                "[2026.01.26-10.10.00:002][  0]GameLog: Display: [Game] ItemChange@ ProtoName=PickItems end\n"
            )

        # Second run - should resume
        deltas = []
        collector2 = Collector(
            db=db,
            log_path=log_path,
            on_delta=lambda d: deltas.append(d),
        )
        collector2.initialize()
        collector2.process_file(from_beginning=False)

        # Should only process new deltas
        assert len(deltas) == 1
        assert deltas[0].delta == 100  # 800 - 700

    def test_context_tracking(self, test_env):
        """Test that PickItems context is tracked correctly."""
        db = test_env["db"]
        log_path = test_env["log_path"]
        repo = Repository(db)

        deltas = []
        collector = Collector(
            db=db,
            log_path=log_path,
            on_delta=lambda d: deltas.append(d),
        )
        collector.initialize()
        collector.process_file(from_beginning=True)

        # Find deltas with PickItems context
        pick_deltas = [d for d in deltas if d.proto_name == "PickItems"]
        other_deltas = [d for d in deltas if d.proto_name is None]

        # Most deltas should be from PickItems
        assert len(pick_deltas) > 0
