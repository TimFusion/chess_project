import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path
from PIL import Image, ImageTk
from board import Board, Color, PieceType
import config

# ------------------------------------------------------------------------ #
# Συντομες μεταβλητες (απο το config)
# ------------------------------------------------------------------------ #
GT = config.game_title # Τιτλος παιχνιδιου
SQ = config.square_size # Μεγεθος τετραγωνου σκακιερας
LC = config.light_color # Χρωμα ανοιχτου τετραγωνου
DC = config.dark_color # Χρωμα σκουρου τετραγωνου
MHBC = config.move_history_box_color # Χρωμα πλαισιου ιστορικου κινησεων
MHBW = config.move_history_box_width # Πλατος πλαισιου ιστορικου κινησεων
HC = config.highlight_color # Χρωμα επισημανσης
CC = config.check_color # Χρωμα για το σαχ
BT = config.blink_time_when_king_in_check # Διαρκεια χρονου (ms) blink οταν ο βασιλιας βρισκεται σε σαχ
PC = config.piece_codes # Κωδικοι εικονων πιονιων
DIR = Path(config.asset_directory) # Path φακελου με τις εικονες

# --------------------------------------------------------------------- #
# Συσχετιση τυπου πιονιου και χρωματος με το αντιστοιχο ονομα εικονας
# --------------------------------------------------------------------- #
codes = {
    (Color.WHITE, PieceType.PAWN):   "wP",
    (Color.WHITE, PieceType.ROOK):   "wR",
    (Color.WHITE, PieceType.KNIGHT): "wN",
    (Color.WHITE, PieceType.BISHOP): "wB",
    (Color.WHITE, PieceType.QUEEN):  "wQ",
    (Color.WHITE, PieceType.KING):   "wK",
    (Color.BLACK, PieceType.PAWN):   "bP",
    (Color.BLACK, PieceType.ROOK):   "bR",
    (Color.BLACK, PieceType.KNIGHT): "bN",
    (Color.BLACK, PieceType.BISHOP): "bB",
    (Color.BLACK, PieceType.QUEEN):  "bQ",
    (Color.BLACK, PieceType.KING):   "bK",
}

# ------------------------------------------------------------------ #
#  GUI κλαση (γραφικο περιβαλλον)
# ------------------------------------------------------------------ #
class ChessGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.board = Board()

        # Δημιουργια βασικου πλαισιου παραθυρου
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH)

        # Σκακιερα
        self.canvas = tk.Canvas(self.frame, width=SQ*8, height=SQ*8, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.Y)
        
        # Πλαίσιο για το ιστορικο κινησεων
        self.history_frame = tk.Frame(self.frame)
        self.history_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Κουτι κειμεου για εμφανιση των κινησεων
        self.history_box = tk.Text(self.history_frame, width=MHBW, state="disabled", bg=MHBC, font=("Consolas", 12), wrap="word")
        self.history_box.pack(fill=tk.BOTH, expand=True)

        # Scrollbar για το πλαισιο ιστορικου
        self.scrollbar = tk.Scrollbar(self.history_frame, command=self.history_box.yview)
        self.history_box.config(yscrollcommand=self.scrollbar.set)

        # Μεταβλητες για σαχ - επιλογη τετραγωνου - επισημανση πιονιου
        self.blink_id = None
        self.blink_state = False
        self.check_square = None
        self.selected_sq = None

        self.images = self.load_images() # Φορτωση πιονιων (εικονες)
        self.draw_board() # Σχεδιαση ταμπλο
        self.draw_all_pieces() # Τοποθετηση πιονιων
        self.canvas.bind("<Button-1>", self.on_click) # Αντιδραση σε αριστερο click χρηστη

        self.move_list = [] # Λιστα κινησεων

    # ------------------------------------------------------------------ #
    #  Image handling
    # ------------------------------------------------------------------ #
    # Φορτωση των εικονων PNG για καθε πιονι στο λεξικο imgs με την σωστη συσχετιση τυπου-χρωματος-εικονας
    def load_images(self):
        imgs = {}
        for code in PC:
            img = Image.open(DIR / f"{code}.png").resize((SQ, SQ), Image.LANCZOS)
            imgs[code] = ImageTk.PhotoImage(img)
        return imgs

    # ------------------------------------------------------------------ #
    #  Board drawing
    # ------------------------------------------------------------------ #
    # Σχεδιαση του ταμπλο σκακιερας
    def draw_board(self):
        for r in range(8):
            for c in range(8):
                x1, y1 = c*SQ, r*SQ
                x2, y2 = x1+SQ, y1+SQ
                color = LC if (r+c) % 2 == 0 else DC
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    # Σχεδιαση ολων των πιονιων πανω στην σκακιερα και εμφανιση σαχ (αν υπαρχει)
    def draw_all_pieces(self):
        self.canvas.delete("piece")
        self.canvas.delete("check")

        check_position = None
        if self.board.king_in_check(self.board.turn):
            for r in range(8):
                for c in range(8):
                    p = self.board.piece_at(r, c)
                    if p and p.color == self.board.turn and p.kind.name == "KING":
                        check_position = (r, c)
                        self.check_square = (r, c)
                        break
                if check_position:
                    break
            self.start_check_blink()
        else:
            self.stop_check_blink()
            self.check_square = None 

        for r in range(8):
            for c in range(8):
                piece = self.board.piece_at(r, c)
                if piece:
                    self.draw_piece(piece)

        if check_position:
            self.highlight_check(*check_position)

    # Σχεδιαση ενος πιονιου στη σωστη θεση
    def draw_piece(self, piece):
        x = piece.col * SQ + SQ // 2
        y = piece.row * SQ + SQ // 2
        code = codes[(piece.color, piece.kind)]
        self.canvas.create_image(x, y, image=self.images[code], tags=("piece",))

    # ------------------------------------------------------------------ #
    #  Event handling
    # ------------------------------------------------------------------ #
    # Καλειται οταν ο χρηστης κανει κλικ σε τετραγωνο της σκακιερας
    def on_click(self, evt):
        # Μετατροπη των συντεταγμενων του click σε θεση στη σκακιερα
        row, col = evt.y // SQ, evt.x // SQ
        # Αν υπαρχει ηδη επιλεγμενο πιονι, προσπαθουμε να το μετακινησουμε
        if self.selected_sq:
            source_row, source_col = self.selected_sq
            sel_piece = self.board.piece_at(source_row, source_col)
            moved = self.board.move(source_row, source_col, row, col)
            # Αφαιρουμε το highlight και μηδενιζουμε την τρεχουσα επιλογη
            self.canvas.delete("highlight")
            self.selected_sq = None
            if moved:
                # Αν η κινηση ηταν επιτυχης, ανανεωνουμε τα πιονια
                self.draw_all_pieces()
                # Καταγραφουμε την κινηση στο ιστορικο
                move_str = self.format_move(sel_piece, row, col)
                self.append_move_to_history(move_str)
                # Ελεγχος για ματ ή πατ
                if not self.board.has_legal_moves(self.board.turn):
                    if self.board.king_in_check(self.board.turn):
                        message = f"Checkmate - {self.board.turn.opposite.name} won"
                    else:
                        message = "Stalemate - draw"
                    tk.messagebox.showinfo("Game Over", message)
                    self.reset_game()
            else:
                # Αν η κινηση δεν ηταν εγκυρη, προσπαθουμε να επιλεξουμε νεο πιονι
                self.try_select(row, col)
        else:
            # Αν δεν εχει επιλεγει ακομη κομματι, προσπαθουμε να επιλεξουμε
            self.try_select(row, col)
    
    # Επιλογη κομματιου για μετακινηση
    def try_select(self, row, col):
        piece = self.board.piece_at(row, col)
        # Ελεγχει αν υπαρχει πιονι και αν ανηκει στον παιχτη που παιζει
        if piece and piece.color is self.board.turn:
            self.selected_sq = (row, col)
            self.highlight_square(row, col)

    # ------------------------------------------------------------------ #
    #  Extras
    # ------------------------------------------------------------------ #
    # Επισημανση επιλεγμενου τετραγωνου
    def highlight_square(self, row, col):
        x1, y1 = col * SQ, row * SQ
        x2, y2 = x1 + SQ, y1 + SQ
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=HC, width=2, tags="highlight")

    # Επισημανση σαχ στον βασιλια
    def highlight_check(self, row, col):
        x1, y1 = col * SQ, row * SQ
        x2, y2 = x1 + SQ, y1 + SQ
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=CC, width=2, tags="check")

    # Εναρξη blink οταν ο βασιλιας ειναι σε σαχ
    def start_check_blink(self):
        if self.blink_id:
            return
        if self.check_square:
            self.blink()

    # Τερματισμος blink
    def stop_check_blink(self):
        if self.blink_id:
            self.canvas.delete("check")
            self.root.after_cancel(self.blink_id)
            self.blink_id = None
            self.blink_state = False
            self.check_square = None
            
    # Blink του τετραγωνου του βασιλια οταν βρισκεται σε σαχ
    def blink(self):
        if not self.check_square:
            self.stop_check_blink()
            return

        self.canvas.delete("check")
        if self.blink_state:
            r, c = self.check_square
            self.highlight_check(r, c)
        self.blink_state = not self.blink_state
        self.blink_id = self.root.after(BT, self.blink)

    # Μορφοποιηση κινησης σε μορφη (π.χ. Qd5, e4)
    def format_move(self, piece, dst_r, dst_c):
        c = "abcdefgh"
        r = "87654321"

        name = {
            PieceType.KING: "K",
            PieceType.QUEEN: "Q",
            PieceType.ROOK: "R",
            PieceType.BISHOP: "B",
            PieceType.KNIGHT: "N",
            PieceType.PAWN: ""
        }[piece.kind]

        dst = c[dst_c] + r[dst_r]

        return name + dst
    
    # Ενημερωση του ιστορικου κινησεων
    def append_move_to_history(self, move_str):
        self.move_list.append(move_str)

        self.history_box.config(state="normal")
        self.history_box.delete("1.0", tk.END)

        lines = []
        for i in range(0, len(self.move_list), 2):
            turn = i // 2 + 1
            white = self.move_list[i]
            black = self.move_list[i + 1] if i + 1 < len(self.move_list) else ""
            lines.append(f"{turn:2d}. {white:5s} {black}")

        self.history_box.insert(tk.END, "\n".join(lines))
        self.history_box.see(tk.END)
        self.history_box.config(state="disabled")

    # Αποθηκευση κινησεων σε αρχειο κειμενου
    def download_move_history(self):
        if not self.move_list:
            return

        lines = []
        for i in range(0, len(self.move_list), 2):
            turn = i // 2 + 1
            white = self.move_list[i]
            black = self.move_list[i + 1] if i + 1 < len(self.move_list) else ""
            lines.append(f"{turn}. {white} {black}")

        content = "\n".join(lines)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Game History"
        )

        if file_path:
            with open(file_path, "w") as f:
                f.write(content)

    # Επαναφορα παιχνιδιου
    def reset_game(self):
        if self.move_list:
            answer = messagebox.askyesno("Save Game History", "Do you want to download the move history?")
            if answer:
                self.download_move_history()
        self.board = Board()
        self.selected_sq = None
        self.canvas.delete("highlight")
        self.canvas.delete("check")
        self.draw_board()
        self.draw_all_pieces()
        self.move_list.clear()
        self.history_box.config(state="normal")
        self.history_box.delete("1.0", tk.END)
        self.history_box.config(state="disabled")

# ------------------------------------------------------------------ #
#  Εκκινηση του παιχνιδιου (main)
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    root = tk.Tk()
    root.title(GT)
    ChessGUI(root)
    root.mainloop()