from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

# --------------------------------------------------------------------- #
#  Ορισμος Χρωματων
# --------------------------------------------------------------------- #
class Color(Enum):
    WHITE = "w"
    BLACK = "b"
 
    # Επιστρεφει το αντιθετο χρωμα (για εναλλαγη σειρας παικτων)
    @property
    def opposite(self):
        return Color.BLACK if self is Color.WHITE else Color.WHITE


# --------------------------------------------------------------------- #
#  Τυποι Πιονιων
# --------------------------------------------------------------------- #
class PieceType(Enum):
    PAWN   = "P" # Πιονι
    KNIGHT = "N" # Ιππος
    BISHOP = "B" # Αξιωματικος
    ROOK   = "R" # Πυργος
    QUEEN  = "Q" # Βασιλισσα
    KING   = "K" # Βασιλιας


# --------------------------------------------------------------------- #
#  Δομη για καθε Πιονι
# --------------------------------------------------------------------- #
@dataclass
class Piece:
    color: Color # Χρώμα του πιονιου
    kind: PieceType # Τυπος του πιονιου
    row: int # Γραμμη στην οποια βρισκεται
    col: int # Στηλη στην οποια βρισκεται
    moved: bool = False # Ελεγχει αν εχει μετακινηθει


# --------------------------------------------------------------------- #
#  Board κλαση (διαχειριζεται την λογικη)
# --------------------------------------------------------------------- #
class Board:
    def __init__(self):

        # Πινακας 8x8 που περιεχει είτε πιονια ειτε None (κενη θεση)
        self.sq: List[List[Optional[Piece]]] = [[None]*8 for _ in range(8)]

        # Κραταει την σειρα του παιχτη (ξεκιναει παντα ο λευκος)
        self.turn: Color = Color.WHITE

        # Τοποθετει τα πιονια στην αρχικη τους θεση
        self.setup_starting()

    # --------------------------------------------------------------------- #
    #  Τοποθετει τα πιονια στη σωστη αρχικη θεση στη σκακιερα
    # --------------------------------------------------------------------- #
    def setup_starting(self):

        # Σωστη σειρα των κυριων πιονιων
        correct_order = (PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN, PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK)
        
        # Τοποθετηση βασικων πιονιων (πρωτη και τελευταια σειρα)
        for col, kind in enumerate(correct_order):
            self._place(Piece(Color.WHITE, kind, 7, col))
            self._place(Piece(Color.BLACK, kind, 0, col))

        # Τοποθετηση πιονιων (δευτερη και προτελευταια σειρα)
        for col in range(8):
            self._place(Piece(Color.WHITE, PieceType.PAWN, 6, col))
            self._place(Piece(Color.BLACK, PieceType.PAWN, 1, col))

    # --------------------------------------------------------------------- #
    #  Τοποθετηση πιονιου σε συγκεκριμενη θεση
    # --------------------------------------------------------------------- #
    def _place(self, piece: Piece):
        self.sq[piece.row][piece.col] = piece

    # Επιστρεφει την συγκεκριμενη θεση του πιονιου (ή None αν ειναι αδεια)
    def piece_at(self, row: int, col: int) -> Optional[Piece]:
        return self.sq[row][col]

    # --------------------------------------------------------------------- #
    #  Εκτελεση κινησης
    # --------------------------------------------------------------------- #
    def move(self, source_row: int, source_col: int, destination_row: int, destination_col: int) -> bool:

        # Παιρνουμε το πιονι που προσπαθει να μετακινηθει με την συναρτηση piece_at
        piece = self.piece_at(source_row, source_col)

        # Ελεγχει αν δεν υπαρχει πιονι ή αν δεν είναι η σειρα του παικτη
        if piece is None or piece.color is not self.turn:
            return False
        
        # Ελεγχει αν το πιονι στο οποιο προσπαθει να μετακινηθει ειναι ιδιο χρωμα
        target = self.piece_at(destination_row, destination_col)
        if target and target.color is piece.color:
            return False
        
        # Ελεγχουμε αν η κηνηση ειναι νομιμη με την συναρτηση legal_moves η οποια διαθετει ολες τις νομιμες κινησεις
        legal = self.legal_moves(piece)
        if (destination_row, destination_col) not in legal:
            return False
        
        # Αποθηκευουμε τι υπαρχει στον προορισμο της κινησης (μπορει να ειναι πιονι του αντιπαλου ή κενο)
        captured = self.piece_at(destination_row, destination_col)

        # Αφαιρουμε προσωρινα το κομματι απο την αρχικη του θεση
        self.sq[source_row][source_col] = None

        # Τοποθετουμε το πιονι στη νεα του θεση
        self.sq[destination_row][destination_col] = piece

        # Αποθηκευουμε την παλια θεση του πιονιου (για πιθανο undo)
        old_row, old_col = piece.row, piece.col

        # Ενημερωνουμε τις συντεταγμενες του πιονιου ωστε να δειχνουν τη νεα του θεση
        piece.row, piece.col = destination_row, destination_col

        # Ελεγχει αν η κινηση αφηνει τον βασιλια σε σαχ, αν ναι η κινηση θεωρειται παρανομη και ακυρωνεται
        if self.king_in_check(piece.color):
            # Επαναφερουμε το πιονι στην αρχικη του θεση
            self.sq[source_row][source_col] = piece

            # Επαναφερουμε αυτο που υπηρχε στον προορισμο
            self.sq[destination_row][destination_col] = captured

            # Επαναφερουμε τις αρχικες συντεταγμενες του πιονιου
            piece.row, piece.col = old_row, old_col
            return False
    
        piece.moved = True # Το πιονι έχει πλεον μετακινηθει
        self.turn = self.turn.opposite # Εναλλαγη σειρας παιχτη
        return True
    
    # --------------------------------------------------------------------- #
    #  Επιτρεπτες κινησεις
    # --------------------------------------------------------------------- #
    def legal_moves(self, piece: Piece) -> list[tuple[int, int]]:
        
        moves = []
        r, c = piece.row, piece.col

        # ----------------------------- Πιονι ----------------------------- #
        if piece.kind == PieceType.PAWN:
            # Ορισμος κατευθυνσης βασει χρωματος: τα λευκα ανεβαινουν (-1), τα μαυρα κατεβαίνουν (+1)
            direction = -1 if piece.color == Color.WHITE else 1
            one_step = r + direction

            # Ελεγχει αν η κινηση μπροστα ειναι εντος σκακιερας και αδεια
            if 0 <= one_step <= 7 and self.sq[one_step][c] is None:
                moves.append((one_step, c))

            # Διαγωνιο φαγωμα αν υπαρχει πιονι σε εκεινη την θεση
            for delta_col in [-1, 1]:
                new_col = c + delta_col
                # Ελεγχει αν η νεα θεση ειναι εντος οριων (0 - 7 γραμμη/στηλη)
                if 0 <= new_col <= 7 and 0 <= one_step <= 7:
                    target = self.sq[one_step][new_col]
                    # Αν ειναι αδεια ή εχει αντιπαλο πιονι, τοτε η κινηση ειναι εγκυρη
                    if target and target.color != piece.color:
                        moves.append((one_step, new_col)) # Προσθηκη στη λιστα νομιμων κινησεων
        # ----------------------------- Ιππος  ----------------------------- #
        elif piece.kind == PieceType.KNIGHT:
            deltas = [
                (-2, -1), (-2, 1), # πανω-αριστερα και πανω-δεξια
                (-1, -2), (-1, 2), # αριστερα-πανω και δεξια-πανω
                (1, -2),  (1, 2), # αριστερα-κατω και δεξια-κατω
                (2, -1),  (2, 1) # κατω-αριστερα και κατω-δεξια
            ]
            
            for delta_row, delta_col in deltas:
                # Υπολογιζει την νεα θεση
                new_row, new_col = r + delta_row, c + delta_col

                # Ελεγχει αν η νεα θεση ειναι εντος οριων (0 - 7 γραμμη/στηλη)
                if 0 <= new_row <= 7 and 0 <= new_col <= 7:
                    target = self.sq[new_row][new_col]
                    # Αν ειναι αδεια ή εχει αντιπαλο πιονι, τοτε η κινηση ειναι εγκυρη
                    if not target or target.color != piece.color:
                        moves.append((new_row, new_col)) # Προσθηκη στη λιστα νομιμων κινησεων
        # ----------------------------- Αξιωματικος - Πυργος - Βασιλισσα ----------------------------- #
        elif piece.kind in {PieceType.BISHOP, PieceType.ROOK, PieceType.QUEEN}:
            if piece.kind == PieceType.BISHOP:
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] # Διαγωνια κινηση
            elif piece.kind == PieceType.ROOK:
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Καθετα - οριζοντια κινηση
            else:
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1),
                              (-1, 0), (1, 0), (0, -1), (0, 1)] # Βασιλισσα: διαγωνια - καθετα - οριζοντια κινηση 
                
            for delta_row, delta_col in directions:
                # Υπολογιζει την νεα θεση
                new_row, new_col = r + delta_row, c + delta_col

                # Προχωραει συνεχως προς την ιδια κατευθυνση μεχρι να φτασει σε εμποδιο ή στο οριο της σκακιερας
                while 0 <= new_row <= 7 and 0 <= new_col <= 7:
                    target = self.sq[new_row][new_col]

                    # Αν η θεση είναι αδεια, η κηνηση επιτρεπεται
                    if not target:
                        moves.append((new_row, new_col))

                    # Αν υπαρχει αντιπαλο πιονι, μπορουμε να το φαμε
                    elif target.color != piece.color:
                        moves.append((new_row, new_col))
                        break
                    # Αν υπαρχει δικο μας πιονι, δεν μπορουμε να συνεχισουμε προς αυτη την κατευθυνση
                    else:
                        break
                    new_row += delta_row
                    new_col += delta_col
        # ----------------------------- Βασιλιας ----------------------------- #
        elif piece.kind == PieceType.KING:
            deltas = [
                (-1, -1), (-1, 0), (-1, 1), # πανω-αριστερα, πανω, πανω-δεξια
                (0, -1),           (0, 1), # αριστερα,  δεξια
                (1, -1),  (1, 0),  (1, 1) # κατω-αριστερα, κατω, κατω-δεξια
                ]
            
            for delta_row, delta_col in deltas:
                # Υπολογιζει την νεα θεση
                new_row, new_col = r + delta_row, c + delta_col

                # Ελεγχει αν η νεα θεση ειναι εντος οριων (0 - 7 γραμμη/στηλη)
                if 0 <= new_row <= 7 and 0 <= new_col <= 7:
                    target = self.sq[new_row][new_col]
                    # Αν ειναι αδεια ή εχει αντιπαλο πιονι, τοτε η κινηση ειναι εγκυρη
                    if not target or target.color != piece.color:
                        moves.append((new_row, new_col)) # Προσθηκη στη λιστα νομιμων κινησεων

        return moves # Επιστρεφει ολες τις νομιμες κινησεις
    
    # --------------------------------------------------------------------- #
    #  Ελεγχος βασιλια
    # --------------------------------------------------------------------- #
    def king_in_check(self, color: Color) -> bool:
        king_position = None

         # Εντοπιζουμε τη θεση του βασιλια
        for r in range(8):
            for c in range(8):
                piece = self.sq[r][c]
                if piece and piece.color == color and piece.kind == PieceType.KING:
                    king_position = (r, c)
                    break
            if king_position:
                break
        
        # Σφαλμα στο στησιμο της σκακιερας (αν δεν βρεθει ο βασιλιας στην σκακερια)
        if not king_position:
            return False
        
        # Ελεγχει αν καποιο αντιπαλο κομματι μπορει να τον φαει
        for r in range(8):
            for c in range(8):
                attacker = self.sq[r][c]
                if attacker and attacker.color != color:
                    targets = self.legal_moves(attacker)
                    if king_position in targets:
                        return True

        return False
    
    # --------------------------------------------------------------------- #
    #  Ελεγχος διαθεσιμων νoμιμων κινησεων
    # --------------------------------------------------------------------- #
    def has_legal_moves(self, color: Color) -> bool:
        # Ελεγχει αν ο παικτης με το δοσμενο χρωμα έχει τουλαχιστον μια νομιμη κινηση
        for r in range(8):
            for c in range(8):
                piece = self.sq[r][c]
                if piece and piece.color == color:
                    # Ελεγχουμε καθε νομιμη κινηση για αυτο το κομματι
                    for (new_row, new_col) in self.legal_moves(piece):
                        # Αποθηκευουμε τι υπαρχει στην νεα θεση (μπορει να ειναι εχθρος ή κενο)
                        captured = self.sq[new_row][new_col]

                        # Προσωρινα κανουμε την κινηση (μεταφερουμε το κομματι)
                        self.sq[piece.row][piece.col] = None
                        self.sq[new_row][new_col] = piece

                        # Αποθηκευουμε την παλια θεση του κομματιου
                        old_row, old_col = piece.row, piece.col
                        piece.row, piece.col = new_row, new_col

                        # Ελεγχουμε αν μετα την κινηση ο βασιλιας είναι σε σαχ
                        in_check = self.king_in_check(color)

                        # Επαναφερουμε τα παντα στην προηγουμενη κατασταση (undo)
                        self.sq[old_row][old_col] = piece
                        self.sq[new_row][new_col] = captured
                        piece.row, piece.col = old_row, old_col

                        # Αν η κινηση δεν οδηγει σε σαχ, τοτε ειναι εγκυρη
                        if not in_check:
                            return True # Υπαρχει Τουλαχιστον μια νομιμη κινηση
                        
        # Αν δεν βρεθηκε καμια νομιμη κινηση, επιστρεφει False
        return False