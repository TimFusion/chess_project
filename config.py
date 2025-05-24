import pathlib

# --------------- Board appearance --------------- #
game_title = "Chess Game"
square_size = 100

light_color = "#f0d9b5"
dark_color = "#b58863"
highlight_color = "red"
check_color = "yellow"

move_history_box_color = "white"
move_history_box_width = 18
temp = 50 

# --------------- Assets --------------- #
asset_directory = pathlib.Path(__file__).parent / "assets" / "pieces"

piece_codes = [
    "wP", "wR", "wN", "wB", "wQ", "wK",
    "bP", "bR", "bN", "bB", "bQ", "bK",
]
