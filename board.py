from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

# --------------------------------------------------------------------- #
#  Color
# --------------------------------------------------------------------- #
class Color(Enum):
    WHITE = "w"
    BLACK = "b"

    @property
    def opposite(self):
        return Color.BLACK if self is Color.WHITE else Color.WHITE


# --------------------------------------------------------------------- #
#  Piece type
# --------------------------------------------------------------------- #
class PieceType(Enum):
    PAWN   = "P"
    KNIGHT = "N"
    BISHOP = "B"
    ROOK   = "R"
    QUEEN  = "Q"
    KING   = "K"


# --------------------------------------------------------------------- #
#  Dataclass
# --------------------------------------------------------------------- #
@dataclass
class Piece:
    color: Color
    kind: PieceType
    row: int
    col: int
    moved: bool = False


# --------------------------------------------------------------------- #
#  Board class
# --------------------------------------------------------------------- #
class Board:
    def __init__(self):
        self.sq: List[List[Optional[Piece]]] = [[None]*8 for _ in range(8)]
        self.turn: Color = Color.WHITE
        self.setup_starting()
        print(self.sq)

    # --------------------------------------------------------------------- #
    #  Initial position
    # --------------------------------------------------------------------- #
    def setup_starting(self):
        correct_order = (
            PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
            PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK
        )
        #draw main pieces
        for col, kind in enumerate(correct_order):
            self._place(Piece(Color.WHITE, kind, 7, col))
            self._place(Piece(Color.BLACK, kind, 0, col))
        #draw pawns
        for col in range(8):
            self._place(Piece(Color.WHITE, PieceType.PAWN, 6, col))
            self._place(Piece(Color.BLACK, PieceType.PAWN, 1, col))

    # --------------------------------------------------------------------- #
    #  Core helpers
    # --------------------------------------------------------------------- #
    def _place(self, piece: Piece):
        self.sq[piece.row][piece.col] = piece

    def piece_at(self, row: int, col: int) -> Optional[Piece]:
        return self.sq[row][col]

    # --------------------------------------------------------------------- #
    #  Move execution
    # --------------------------------------------------------------------- #
    def move(self, source_row: int, source_col: int, destination_row: int, destination_col: int) -> bool:

        piece = self.piece_at(source_row, source_col)
        if piece is None or piece.color is not self.turn:
            print("error detected: piece move error #1")
            return False
        
        legal = self.legal_moves(piece)
        if (destination_row, destination_col) not in legal:
            return False
        
        target = self.piece_at(destination_row, destination_col)
        if target and target.color is piece.color:
            return False

        # update array
        captured = self.piece_at(destination_row, destination_col)
        self.sq[source_row][source_col] = None
        self.sq[destination_row][destination_col] = piece
        old_row, old_col = piece.row, piece.col
        piece.row, piece.col = destination_row, destination_col

        if self.king_in_check(piece.color):
            # Undo move
            self.sq[source_row][source_col] = piece
            self.sq[destination_row][destination_col] = captured
            piece.row, piece.col = old_row, old_col
            return False  # illegal
    
        piece.moved = True
        self.turn = self.turn.opposite
        return True
    
    # ----------------------------- Legal moves ----------------------------- #
    def legal_moves(self, piece: Piece) -> list[tuple[int, int]]:
        moves = []
        r, c = piece.row, piece.col

        # ----------------------------- Pawn ----------------------------- #
        if piece.kind == PieceType.PAWN:
            direction = -1 if piece.color == Color.WHITE else 1
            one_step = r + direction

            # forward
            if 0 <= one_step <= 7 and self.sq[one_step][c] is None:
                moves.append((one_step, c))

            # diagonal
            for dc in [-1, 1]:
                new_col = c + dc
                if 0 <= new_col <= 7 and 0 <= one_step <= 7:
                    target = self.sq[one_step][new_col]
                    if target and target.color != piece.color:
                        moves.append((one_step, new_col))
        # ----------------------------- Knight ----------------------------- #
        elif piece.kind == PieceType.KNIGHT:
            deltas = [
                (-2, -1), (-2, 1),
                (-1, -2), (-1, 2),
                (1, -2),  (1, 2),
                (2, -1),  (2, 1)
            ]
            for dr, dc in deltas:
                nr, nc = r + dr, c + dc
                if 0 <= nr <= 7 and 0 <= nc <= 7:
                    target = self.sq[nr][nc]
                    if not target or target.color != piece.color:
                        moves.append((nr, nc))
        # ----------------------------- Bishop - Rook - Queen ----------------------------- #
        elif piece.kind in {PieceType.BISHOP, PieceType.ROOK, PieceType.QUEEN}:
            if piece.kind == PieceType.BISHOP:
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]       # diagonal
            elif piece.kind == PieceType.ROOK:
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]     # straight
            else:  # queen
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1),
                              (-1, 0), (1, 0), (0, -1), (0, 1)]

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                while 0 <= nr <= 7 and 0 <= nc <= 7:
                    target = self.sq[nr][nc]
                    if not target:
                        moves.append((nr, nc))  # empty square => valid
                    elif target.color != piece.color:
                        moves.append((nr, nc))  # enemy => capture, then stop
                        break
                    else:
                        break  # own piece blocks
                    nr += dr
                    nc += dc
        # ----------------------------- King ----------------------------- #
        elif piece.kind == PieceType.KING:
            deltas = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1),           (0, 1),
                (1, -1),  (1, 0),  (1, 1)
                ]
            for dr, dc in deltas:
                nr, nc = r + dr, c + dc
                if 0 <= nr <= 7 and 0 <= nc <= 7:
                    target = self.sq[nr][nc]
                    if not target or target.color != piece.color:
                        moves.append((nr, nc))

        return moves
    
    # ----------------------------- Check King ----------------------------- #
    def king_in_check(self, color: Color) -> bool:
        king_position = None
        for r in range(8):
            for c in range(8):
                piece = self.sq[r][c]
                if piece and piece.color == color and piece.kind == PieceType.KING:
                    king_position = (r, c)
                    break
            if king_position:
                break

        if not king_position:
            print("error detected: king error #1")
            return False

        for r in range(8):
            for c in range(8):
                attacker = self.sq[r][c]
                if attacker and attacker.color != color:
                    targets = self.legal_moves(attacker)
                    if king_position in targets:
                        return True

        return False
    
    # ----------------------------- Check remaining legal moves ----------------------------- #
    def has_legal_moves(self, color: Color) -> bool:
        for r in range(8):
            for c in range(8):
                piece = self.sq[r][c]
                if piece and piece.color == color:
                    for (nr, nc) in self.legal_moves(piece):
                        captured = self.sq[nr][nc]
                        self.sq[piece.row][piece.col] = None
                        self.sq[nr][nc] = piece
                        old_row, old_col = piece.row, piece.col
                        piece.row, piece.col = nr, nc

                        in_check = self.king_in_check(color)

                        self.sq[old_row][old_col] = piece
                        self.sq[nr][nc] = captured
                        piece.row, piece.col = old_row, old_col

                        if not in_check:
                            return True
        return False