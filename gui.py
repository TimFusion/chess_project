import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path
from PIL import Image, ImageTk
from board import Board, Color, PieceType
import config

GT = config.game_title
SQ = config.square_size
LC = config.light_color
DC = config.dark_color
MHBC = config.move_history_box_color
MHBW = config.move_history_box_width
HC = config.highlight_color
CC = config.check_color
PC = config.piece_codes
DIR = Path(config.asset_directory)

#load image pieces
CODE = {
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
#  GUI class
# ------------------------------------------------------------------ #
class ChessGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.board = Board()

        # main frame
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH)

        # board frame
        self.canvas = tk.Canvas(self.frame, width=SQ*8, height=SQ*8, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.Y)
        
        # history box frame
        self.history_frame = tk.Frame(self.frame)
        self.history_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # history box frame
        self.history_box = tk.Text(self.history_frame, width=MHBW, state="disabled", bg=MHBC, font=("Consolas", 12), wrap="word")
        self.history_box.pack(fill=tk.BOTH, expand=True)

        # history box scrollbar
        self.scrollbar = tk.Scrollbar(self.history_frame, command=self.history_box.yview)
        self.history_box.config(yscrollcommand=self.scrollbar.set)

        self.blink_id = None
        self.blink_state = False
        self.check_square = None
        self.selected_sq = None

        self.images = self.load_images()
        self.draw_board()
        self.draw_all_pieces()
        self.canvas.bind("<Button-1>", self.on_click)

        self.move_list = []

    # ------------------------------------------------------------------ #
    #  Image handling
    # ------------------------------------------------------------------ #
    def load_images(self):
        imgs = {}
        for code in PC:
            img = Image.open(DIR / f"{code}.png").resize((SQ, SQ), Image.LANCZOS)
            imgs[code] = ImageTk.PhotoImage(img)
        return imgs

    # ------------------------------------------------------------------ #
    #  Board drawing
    # ------------------------------------------------------------------ #
    def draw_board(self):
        for r in range(8):
            for c in range(8):
                x1, y1 = c*SQ, r*SQ
                x2, y2 = x1+SQ, y1+SQ
                color = LC if (r+c) % 2 == 0 else DC
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

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

    def draw_piece(self, piece):
        x = piece.col * SQ + SQ // 2
        y = piece.row * SQ + SQ // 2
        code = CODE[(piece.color, piece.kind)]
        self.canvas.create_image(x, y, image=self.images[code], tags=("piece",))

    # ------------------------------------------------------------------ #
    #  Event handling
    # ------------------------------------------------------------------ #
    def on_click(self, evt):
        row, col = evt.y // SQ, evt.x // SQ
        print(row, col)
        if self.selected_sq:
            src_r, src_c = self.selected_sq
            sel_piece = self.board.piece_at(src_r, src_c)
            moved = self.board.move(src_r, src_c, row, col)
            self.canvas.delete("highlight")
            self.selected_sq = None
            if moved:
                self.draw_all_pieces()
                move_str = self.format_move(sel_piece, src_r, src_c, row, col)
                self.append_move_to_history(move_str)
                if not self.board.has_legal_moves(self.board.turn):
                    if self.board.king_in_check(self.board.turn):
                        message = f"Checkmate - {self.board.turn.opposite.name} won"
                    else:
                        message = "Stalemate - draw"
                    tk.messagebox.showinfo("Game Over", message)
                    self.reset_game()
            else:
                self.try_select(row, col)
        else:
            self.try_select(row, col)

    def try_select(self, row, col):
        piece = self.board.piece_at(row, col)
        if piece and piece.color is self.board.turn:
            self.selected_sq = (row, col)
            self.highlight_square(row, col)

    # ------------------------------------------------------------------ #
    #  Extra
    # ------------------------------------------------------------------ #
    # ---------------- Highlight square ---------------- #
    def highlight_square(self, row, col):
        x1, y1 = col * SQ, row * SQ
        x2, y2 = x1 + SQ, y1 + SQ
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=HC, width=2, tags="highlight")

    # ---------------- Highlight check ---------------- #
    def highlight_check(self, row, col):
        x1, y1 = col * SQ, row * SQ
        x2, y2 = x1 + SQ, y1 + SQ
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=CC, width=2, tags="check")

    # ---------------- Start blink ---------------- #
    def start_check_blink(self):
        if self.blink_id:
            return
        if self.check_square:
            self.blink()

    # ---------------- Stop blink ---------------- #
    def stop_check_blink(self):
        if self.blink_id:
            self.canvas.delete("check")
            self.root.after_cancel(self.blink_id)
            self.blink_id = None
            self.blink_state = False
            self.check_square = None
            
    # ---------------- Check blink ---------------- #
    def blink(self):
        if not self.check_square:
            self.stop_check_blink()
            return

        self.canvas.delete("check")
        if self.blink_state:
            r, c = self.check_square
            self.highlight_check(r, c)
        self.blink_state = not self.blink_state
        self.blink_id = self.root.after(300, self.blink)

    # ---------------- Format move ---------------- #
    def format_move(self, piece, src_r, src_c, dst_r, dst_c):
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
    
    # ---------------- Add move to history box---------------- #
    def append_move_to_history(self, move_str):
        self.move_list.append(move_str)

        # Format into lines like: 1. e4 e5
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

    # ---------------- Download move history ---------------- #
    def save_move_history(self):
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

    # ---------------- Reset game ---------------- #
    def reset_game(self):
        if self.move_list:
            answer = messagebox.askyesno("Save Game History", "Do you want to download the move history?")
            if answer:
                self.save_move_history()
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

# ---------------- Main ---------------- #
if __name__ == "__main__":
    root = tk.Tk()
    root.title(GT)
    ChessGUI(root)
    root.mainloop()