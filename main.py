from enum import Enum
from typing import List, Tuple, Optional
from dataclasses import dataclass

class PieceType(Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

class Color(Enum):
    WHITE = 0
    BLACK = 1

@dataclass
class Piece:
    piece_type: PieceType
    color: Color
    has_moved: bool = False

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self._initialize_board()
        self.current_turn = Color.WHITE
        
    def _initialize_board(self):
        # Initialize pawns
        for col in range(8):
            self.board[1][col] = Piece(PieceType.PAWN, Color.WHITE)
            self.board[6][col] = Piece(PieceType.PAWN, Color.BLACK)
        
        # Initialize other pieces
        piece_order = [
            PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
            PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK
        ]
        
        for col in range(8):
            self.board[0][col] = Piece(piece_order[col], Color.WHITE)
            self.board[7][col] = Piece(piece_order[col], Color.BLACK)

    def calculate_slope(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> float:
        """Calculate the slope between two positions."""
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        # Handle vertical movement (undefined slope)
        if end_col - start_col == 0:
            return float('inf')
            
        return (end_row - start_row) / (end_col - start_col)

    def calculate_distance(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> float:
        """Calculate the manhattan distance between two positions."""
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        return max(abs(end_row - start_row), abs(end_col - start_col))

    def is_valid_move(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> bool:
        """Validate a move based on piece type and slope."""
        if not self._is_within_bounds(end_pos):
            return False
            
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        piece = self.board[start_row][start_col]
        
        if piece is None:
            return False
            
        # Can't capture your own piece
        if self.board[end_row][end_col] and self.board[end_row][end_col].color == piece.color:
            return False
            
        slope = self.calculate_slope(start_pos, end_pos)
        distance = self.calculate_distance(start_pos, end_pos)
        
        if piece.piece_type == PieceType.BISHOP:
            return self._is_valid_bishop_move(slope)
        elif piece.piece_type == PieceType.ROOK:
            return self._is_valid_rook_move(slope)
        elif piece.piece_type == PieceType.QUEEN:
            return self._is_valid_queen_move(slope)
        elif piece.piece_type == PieceType.KNIGHT:
            return self._is_valid_knight_move(start_pos, end_pos)
        elif piece.piece_type == PieceType.KING:
            return self._is_valid_king_move(slope, distance)
        elif piece.piece_type == PieceType.PAWN:
            return self._is_valid_pawn_move(start_pos, end_pos, piece.color)
            
        return False

    def _is_valid_bishop_move(self, slope: float) -> bool:
        """Bishop moves must have slope of exactly 1 or -1."""
        return abs(slope) == 1

    def _is_valid_rook_move(self, slope: float) -> bool:
        """Rook moves must have slope of 0 (horizontal) or infinity (vertical)."""
        return slope == 0 or slope == float('inf')

    def _is_valid_queen_move(self, slope: float) -> bool:
        """Queen combines bishop and rook movements."""
        return slope == 0 or slope == float('inf') or abs(slope) == 1

    def _is_valid_king_move(self, slope: float, distance: float) -> bool:
        """King moves like queen but only one square at a time."""
        return (slope == 0 or slope == float('inf') or abs(slope) == 1) and distance == 1

    def _is_valid_knight_move(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> bool:
        """Knight moves in L-shape: 2 squares one way, 1 square perpendicular."""
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        return sorted([row_diff, col_diff]) == [1, 2]

    def _is_valid_pawn_move(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], color: Color) -> bool:
        """Pawn moves forward 1 square (or 2 from start) and captures diagonally."""
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        # Direction based on color
        direction = 1 if color == Color.BLACK else -1
        
        # Regular forward move
        if start_col == end_col:
            if end_row - start_row == direction:
                return self.board[end_row][end_col] is None
            # First move can be 2 squares
            if not piece.has_moved and end_row - start_row == 2 * direction:
                middle_row = start_row + direction
                return (self.board[middle_row][start_col] is None and 
                       self.board[end_row][end_col] is None)
            return False
            
        # Capture move (diagonal)
        if abs(end_col - start_col) == 1 and end_row - start_row == direction:
            return self.board[end_row][end_col] is not None

        return False

    def _is_within_bounds(self, pos: Tuple[int, int]) -> bool:
        """Check if position is within board boundaries."""
        row, col = pos
        return 0 <= row < 8 and 0 <= col < 8

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Get piece at given position."""
        if self._is_within_bounds((row, col)):
            return self.board[row][col]
        return None

    def make_move(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> bool:
        """Attempt to make a move. Return True if successful."""
        if not self.is_valid_move(start_pos, end_pos):
            return False
            
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        # Move piece
        piece = self.board[start_row][start_col]
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None
        piece.has_moved = True
        
        # Switch turns
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        return True

    def is_path_clear(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> bool:
        """Check if path between two positions is clear of pieces."""
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        row_step = 0 if start_row == end_row else (end_row - start_row) // abs(end_row - start_row)
        col_step = 0 if start_col == end_col else (end_col - start_col) // abs(end_col - start_col)
        
        current_row = start_row + row_step
        current_col = start_col + col_step
        
        while (current_row, current_col) != end_pos:
            if self.board[current_row][current_col] is not None:
                return False
            current_row += row_step
            current_col += col_step
            
        return True
