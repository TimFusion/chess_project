import pathlib

# --------------- Εμφανιση σκακιερας --------------- #
game_title = "Chess Game"
square_size = 100

light_color = "#f0d9b5"
dark_color = "#b58863"
highlight_color = "red"
check_color = "yellow"

blink_time_when_king_in_check = 300 # (100ms = 0.1 second)

move_history_box_color = "white"
move_history_box_width = 18

# --------------- Αρχεια εικονας --------------- #

#Το path του φακελου που περιεχει τις εικονες των πιονιων
asset_directory = pathlib.Path(__file__).parent / "assets" / "pieces"

# Κωδικοι εικονων για τα πιονια (χρησιμοποιουνται για την φορτωση εικονων)
piece_codes = [
    "wP", "wR", "wN", "wB", "wQ", "wK",
    "bP", "bR", "bN", "bB", "bQ", "bK",
]
