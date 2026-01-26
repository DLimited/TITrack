"""Tests for regex patterns."""

import pytest

from titrack.parser.patterns import (
    BAG_MODIFY_PATTERN,
    ITEM_CHANGE_PATTERN,
    LEVEL_EVENT_PATTERN,
    HUB_ZONE_PATTERNS,
)


class TestBagModifyPattern:
    """Tests for BagMgr modification pattern."""

    def test_matches_standard_line(self):
        line = "GameLog: Display: [Game] BagMgr@:Modfy BagItem PageId = 102 SlotId = 0 ConfigBaseId = 100300 Num = 671"
        match = BAG_MODIFY_PATTERN.search(line)
        assert match is not None
        assert match.group("page_id") == "102"
        assert match.group("slot_id") == "0"
        assert match.group("config_base_id") == "100300"
        assert match.group("num") == "671"

    def test_matches_different_values(self):
        line = "GameLog: Display: [Game] BagMgr@:Modfy BagItem PageId = 1 SlotId = 99 ConfigBaseId = 999999 Num = 12345"
        match = BAG_MODIFY_PATTERN.search(line)
        assert match is not None
        assert match.group("page_id") == "1"
        assert match.group("slot_id") == "99"
        assert match.group("config_base_id") == "999999"
        assert match.group("num") == "12345"

    def test_no_match_on_unrelated_line(self):
        line = "GameLog: Display: [Game] SomeOtherEvent"
        match = BAG_MODIFY_PATTERN.search(line)
        assert match is None

    def test_matches_with_prefix(self):
        line = "[2026.01.26-10.00.00:000][  0]GameLog: Display: [Game] BagMgr@:Modfy BagItem PageId = 102 SlotId = 0 ConfigBaseId = 100300 Num = 500"
        match = BAG_MODIFY_PATTERN.search(line)
        assert match is not None
        assert match.group("num") == "500"


class TestItemChangePattern:
    """Tests for ItemChange context marker pattern."""

    def test_matches_start_marker(self):
        line = "GameLog: Display: [Game] ItemChange@ ProtoName=PickItems start"
        match = ITEM_CHANGE_PATTERN.search(line)
        assert match is not None
        assert match.group("proto_name") == "PickItems"
        assert match.group("marker") == "start"

    def test_matches_end_marker(self):
        line = "GameLog: Display: [Game] ItemChange@ ProtoName=PickItems end"
        match = ITEM_CHANGE_PATTERN.search(line)
        assert match is not None
        assert match.group("proto_name") == "PickItems"
        assert match.group("marker") == "end"

    def test_matches_other_proto_name(self):
        line = "GameLog: Display: [Game] ItemChange@ ProtoName=SellItems start"
        match = ITEM_CHANGE_PATTERN.search(line)
        assert match is not None
        assert match.group("proto_name") == "SellItems"

    def test_no_match_without_marker(self):
        line = "GameLog: Display: [Game] ItemChange@ ProtoName=PickItems"
        match = ITEM_CHANGE_PATTERN.search(line)
        assert match is None


class TestLevelEventPattern:
    """Tests for level transition event pattern."""

    def test_matches_enter_level(self):
        line = "LevelMgr@ EnterLevel Map_Desert_T16_001"
        match = LEVEL_EVENT_PATTERN.search(line)
        assert match is not None
        assert match.group("event_type") == "EnterLevel"
        assert match.group("level_info") == "Map_Desert_T16_001"

    def test_matches_open_level(self):
        line = "LevelMgr@ OpenLevel Map_Forest_T14_002"
        match = LEVEL_EVENT_PATTERN.search(line)
        assert match is not None
        assert match.group("event_type") == "OpenLevel"
        assert match.group("level_info") == "Map_Forest_T14_002"

    def test_matches_with_spaces_in_level_info(self):
        line = "LevelMgr@ EnterLevel Some Level With Spaces"
        match = LEVEL_EVENT_PATTERN.search(line)
        assert match is not None
        assert match.group("level_info") == "Some Level With Spaces"


class TestHubZonePatterns:
    """Tests for hub/town zone detection patterns."""

    def test_detects_hub(self):
        assert any(p.search("MainHub_Social") for p in HUB_ZONE_PATTERNS)

    def test_detects_town(self):
        assert any(p.search("Town_Start") for p in HUB_ZONE_PATTERNS)

    def test_detects_hideout(self):
        assert any(p.search("Player_Hideout_01") for p in HUB_ZONE_PATTERNS)

    def test_does_not_match_map(self):
        assert not any(p.search("Map_Desert_T16_001") for p in HUB_ZONE_PATTERNS)
