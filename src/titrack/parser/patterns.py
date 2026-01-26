"""Compiled regex patterns for log parsing."""

import re

# BagMgr modification line
# Example: GameLog: Display: [Game] BagMgr@:Modfy BagItem PageId = 102 SlotId = 0 ConfigBaseId = 100300 Num = 671
BAG_MODIFY_PATTERN = re.compile(
    r"GameLog:\s*Display:\s*\[Game\]\s*BagMgr@:Modfy\s+BagItem\s+"
    r"PageId\s*=\s*(?P<page_id>\d+)\s+"
    r"SlotId\s*=\s*(?P<slot_id>\d+)\s+"
    r"ConfigBaseId\s*=\s*(?P<config_base_id>\d+)\s+"
    r"Num\s*=\s*(?P<num>\d+)"
)

# ItemChange context markers
# Example: GameLog: Display: [Game] ItemChange@ ProtoName=PickItems start
# Example: GameLog: Display: [Game] ItemChange@ ProtoName=PickItems end
ITEM_CHANGE_PATTERN = re.compile(
    r"GameLog:\s*Display:\s*\[Game\]\s*ItemChange@\s*"
    r"ProtoName=(?P<proto_name>\w+)\s+"
    r"(?P<marker>start|end)"
)

# Level transition events
# Actual format from game logs:
# SceneLevelMgr@ OpenMainWorld END! InMainLevelPath = /Game/Art/Maps/04DD/DD_ShengTingZhuangYuan000/...
LEVEL_EVENT_PATTERN = re.compile(
    r"SceneLevelMgr@\s+(?P<event_type>OpenMainWorld)\s+END!\s+"
    r"InMainLevelPath\s*=\s*(?P<level_info>.+)"
)

# Known hub/town zone patterns (for run segmentation)
# These patterns identify non-mapping zones
# Map paths look like: /Game/Art/Maps/01SD/XZ_YuJinZhiXiBiNanSuo200/...
# Hub/hideout codes: 01SD (Ember's Rest hideout), 04DD, etc.
HUB_ZONE_PATTERNS = [
    re.compile(r"hideout", re.IGNORECASE),
    re.compile(r"town", re.IGNORECASE),
    re.compile(r"hub", re.IGNORECASE),
    re.compile(r"lobby", re.IGNORECASE),
    re.compile(r"social", re.IGNORECASE),
    re.compile(r"/01SD/", re.IGNORECASE),  # Ember's Rest hideout
    re.compile(r"/04DD/", re.IGNORECASE),  # Another hideout variant
    re.compile(r"YuJinZhiXiBiNanSuo", re.IGNORECASE),  # Ember's Rest (Chinese name)
    re.compile(r"ShengTingZhuangYuan", re.IGNORECASE),  # Sacred Court Manor (hideout)
    re.compile(r"ZhuCheng", re.IGNORECASE),  # Main city
]

# Flame Elementium ConfigBaseId (primary currency)
FE_CONFIG_BASE_ID = 100300
