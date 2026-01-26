"""Zone name mappings from internal paths to English names."""

# Map internal zone path patterns to English display names
# Add new mappings as you encounter zones
ZONE_NAMES = {
    # Hideouts / Hubs
    "XZ_YuJinZhiXiBiNanSuo": "Hideout - Ember's Rest",
    "DD_ShengTingZhuangYuan": "Hideout - Sacred Court Manor",

    # Maps - add as you encounter them
    "KD_YuanSuKuangDong": "Elemental Cave",  # Placeholder - update with real name
    "SQ_NvShenQunBai": "Goddess Worship",  # Placeholder - update with real name

    # Add more mappings here as you play
    # "InternalName": "English Name",
}


def get_zone_display_name(zone_path: str) -> str:
    """
    Get the English display name for a zone path.

    Args:
        zone_path: Internal zone path like /Game/Art/Maps/01SD/XZ_YuJinZhiXiBiNanSuo200/...

    Returns:
        English display name if known, otherwise a cleaned-up version of the path
    """
    # Check each known mapping
    for internal_name, english_name in ZONE_NAMES.items():
        if internal_name in zone_path:
            return english_name

    # Fallback: extract the zone code from the path
    # /Game/Art/Maps/01SD/XZ_YuJinZhiXiBiNanSuo200/... -> XZ_YuJinZhiXiBiNanSuo200
    parts = zone_path.split("/")
    for part in reversed(parts):
        if part and not part.startswith("Game") and not part.startswith("Art"):
            # Remove trailing numbers
            import re
            cleaned = re.sub(r'\d+$', '', part)
            return cleaned if cleaned else part

    return zone_path
