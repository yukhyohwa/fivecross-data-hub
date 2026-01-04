# Games Configuration Registry
# This file manages all game settings, IDs, and environments.

# Structure:
# {
#     "unique_key": {
#         "label": "Display Name in UI",
#         "folder": "Folder name in sql_templates",
#         "environment": "domestic" or "overseas",
#         "game_id": "Game ID (for use in SQL placeholders like [app_id] or logic)",
#         "odps_project": "ODPS Project Name (optional, if needed for specific connection)"
#     }
# }

GAMES_CONFIG = {
    "slamdunk_overseas": {
        "label": "Slam Dunk (Overseas)",
        "folder": "slamdunk_overseas",
        "environment": "overseas",
        "game_id": "g33002013"
    },
    "jump_overseas": {
        "label": "JUMP (Overseas)",
        "folder": "jump_overseas",
        "environment": "overseas",
        "game_id": "g65002007"
    },
    "onepiece_domestic": {
        "label": "One Piece (China)",
        "folder": "onepiece_domestic",
        "environment": "domestic",
        "game_id": "hzw_cn"
    }
}

def get_game_config(key):
    return GAMES_CONFIG.get(key)
