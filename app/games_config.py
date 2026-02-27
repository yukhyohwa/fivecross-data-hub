# Games Configuration Registry
# This file manages all game settings, IDs, and environments.

# Structure:
# {
#     "unique_key": {
#         "label": "Display Name in UI",
#         "folder": "Folder name in sql_templates",
#         "environment": "domestic" or "overseas",
#         "game_id": "Game ID (for use in SQL placeholders like [app_id] or logic)",
#         "engine": "odps" (default), "ta" (ThinkingData), or "holo" (Hologres),
#         "odps_project": "ODPS Project Name (optional, if needed for specific connection)"
#     }
# }

GAMES_CONFIG = {
    "slamdunk_overseas": {
        "label": "Slam Dunk (Overseas)",
        "folder": "slamdunk_overseas",
        "environment": "overseas",
        "game_id": "g33002013",
        "engine": "odps"
    },
    "jump_overseas": {
        "label": "JUMP (Overseas)",
        "folder": "jump_overseas",
        "environment": "overseas",
        "game_id": "g65002007",
        "engine": "odps"
    },
    "onepiece_domestic": {
        "label": "One Piece (China)",
        "folder": "onepiece_domestic",
        "environment": "domestic",
        "game_id": "hzw_cn",
        "engine": "odps"
    },
    # Example for ThinkingData Game
    # "new_ta_game": {
    #     "label": "New TA Game",
    #     "folder": "ta_game_folder",
    #     "environment": "global",
    #     "game_id": "ta_appid_123",
    #     "engine": "ta"
    # }
}

def get_game_config(key):
    return GAMES_CONFIG.get(key)
