import numpy as np
import copy
from piece import Pawn, Rook, Knight, Bishop, Queen, King, colors, reverse_figures

class Board:
    def __init__(self):
        self.board = self.create_board()
        self.populate_board()
        self.captured_pieces = []
        self.tmp_board = np.copy(self.board)

    def create_board(self):
        return np.array([[None for _ in range(8)] for _ in range(8)])

    def populate_board(self):
        self.place_pieces(Pawn, 1, colors['white'])
        self.place_pieces(Pawn, 6, colors['black'])
        self.place_pieces(Rook, 0, colors['white'], [0, 7])
        self.place_pieces(Rook, 7, colors['black'], [0, 7])
        self.place_pieces(Knight, 0, colors['white'], [1, 6])
        self.place_pieces(Knight, 7, colors['black'], [1, 6])
        self.place_pieces(Bishop, 0, colors['white'], [2, 5])
        self.place_pieces(Bishop, 7, colors['black'], [2, 5])
        self.place_pieces(Queen, 0, colors['white'], [3])
        self.place_pieces(Queen, 7, colors['black'], [3])
        self.place_pieces(King, 0, colors['white'], [4])
        self.place_pieces(King, 7, colors['black'], [4])

    def is_changed(self):
        if not np.array_equal(self.board, self.tmp_board):
            self.tmp_board = np.copy(self.board)
            return True
        return False

    def place_pieces(self, piece_class, row, color, cols=None):
        if cols is None:
            for col in range(8):
                self.board[row][col] = piece_class(color, (row, col))
        else:
            for col in cols:
                self.board[row][col] = piece_class(color, (row, col))

    def move_piece(self, start_pos, end_pos):
        piece = self.get_piece(start_pos)
        if not piece:
            return False
        if end_pos not in piece.valid_moves(self):
            return False
        target_piece = self.get_piece(end_pos)
        if target_piece:
            if isinstance(target_piece, King):
                return False
            if target_piece.color != piece.color:
                target_piece.eliminate()
                self.captured_pieces.append(target_piece)

        self.board[start_pos[0]][start_pos[1]] = None
        piece.position = end_pos
        self.board[end_pos[0]][end_pos[1]] = piece
        return True

    def show_board(self):
        print("  " + " ".join(str(x) for x in range(8)))
        for y, row in enumerate(self.board):
            print(f"{y} " + " ".join([reverse_figures[piece.figure] if piece else '.' for piece in row]))

    def get_piece(self, position):
        row, col = position
        return self.board[row][col]

    def check_for_enemy(self, position, color):
        piece = self.get_piece(position)
        return piece and piece.color != color

    def check_for_friendly(self, position, color):
        piece = self.get_piece(position)
        return piece and piece.color == color

    def check_for_empty(self, position):
        return not self.get_piece(position)

    def get_moves(self, color):
        color_value = colors[color]
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if piece and piece.color == color_value:
                    piece_moves = piece.valid_moves(self)
                    for move in piece_moves:
                        moves.append([(row, col), move])
        return moves

    def enemy_moves(self, color):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if piece and piece.color != color and not isinstance(piece, King):
                    piece_moves = piece.valid_moves(self)
                    if isinstance(piece, Pawn):
                        piece_moves = self.filter_pawn_moves(piece, piece_moves, row, col)
                    for move in piece_moves:
                        moves.append([(row, col), move])
        return moves

    def filter_pawn_moves(self, piece, piece_moves, row, col):
        if piece.color == colors['white']:
            return [move for move in piece_moves if not (move[0] == row + 1 and move[1] == col) and not (move[0] == row + 2 and move[1] == col)]
        elif piece.color == colors['black']:
            return [move for move in piece_moves if not (move[0] == row - 1 and move[1] == col) and not (move[0] == row - 2 and move[1] == col)]
        return piece_moves

    def future_enemy_moves(self, color):
        return self.enemy_moves(color)

    def get_enemy_king_position(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if piece and isinstance(piece, King) and piece.color != color:
                    return (row, col)
        return None

    def enemy_king_moves(self, color):
        enemy_king_position = self.get_enemy_king_position(color)
        if enemy_king_position:
            enemy_king = self.get_piece(enemy_king_position)
            if isinstance(enemy_king, King):
                return enemy_king.valid_moves(self)
        return []

    def get_king_position(self, color):
        color_value = colors[color]
        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if piece and isinstance(piece, King) and piece.color == color_value:
                    return (row, col)
        return None

    def is_check(self, color):
        king_position = self.get_king_position(color)
        checking_pieces = []
        enemy_moves = self.get_moves('white' if color == 'black' else 'black')
        for move in enemy_moves:
            if move[1] == king_position:
                checking_pieces.append(self.get_piece(move[0]))

        return bool(checking_pieces), checking_pieces

    def check_for_check_mate(self, color, valid_moves):
        in_check, checking_pieces = self.is_check(color)
        if in_check and len(valid_moves) == 0:
            return True
        return False

    def check_for_pat(self, color, valid_moves):
        in_check, _ = self.is_check(color)
        if not in_check and len(valid_moves) == 0:
            return True
        return False

    def translate_to_matrix(self):
        pawn_matrix = np.zeros((8, 8), dtype=int)
        rook_matrix = np.zeros((8, 8), dtype=int)
        knight_matrix = np.zeros((8, 8), dtype=int)
        bishop_matrix = np.zeros((8, 8), dtype=int)
        queen_matrix = np.zeros((8, 8), dtype=int)
        king_matrix = np.zeros((8, 8), dtype=int)

        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if piece:
                    value = 1 if piece.color == colors['white'] else -1
                    if isinstance(piece, Pawn):
                        pawn_matrix[row, col] = value
                    elif isinstance(piece, Rook):
                        rook_matrix[row, col] = value
                    elif isinstance(piece, Knight):
                        knight_matrix[row, col] = value
                    elif isinstance(piece, Bishop):
                        bishop_matrix[row, col] = value
                    elif isinstance(piece, Queen):
                        queen_matrix[row, col] = value
                    elif isinstance(piece, King):
                        king_matrix[row, col] = value

        board_matrix = np.array([pawn_matrix, rook_matrix, knight_matrix, bishop_matrix, queen_matrix, king_matrix])

        return board_matrix