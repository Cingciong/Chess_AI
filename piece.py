import copy

colors = {
    'white': 0,
    'black': 1,
}
figures = {
    'Pawn': 1,
    'Rook': 2,
    'Knight': 3,
    'Bishop': 4,
    'Queen': 5,
    'King': 6,
}
reverse_figures = {v: k[0] for k, v in figures.items()}

class Piece:
    def __init__(self, color, position):
        self.color = color
        self.position = position
        self.eliminated = False
        self.destructable = True

    def eliminate(self):
        self.eliminated = True

    def valid_moves(self, board_instance):
        return []

class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.first_move = True
        self.figure = figures['Pawn']

    def valid_moves(self, board_instance):
        moves = []
        row, col = self.position

        if self.color == colors['white']:
            if row == 1 and board_instance.check_for_empty((row + 2, col)) and board_instance.check_for_empty((row + 1, col)):
                moves.append((row + 2, col))
            if row + 1 < 8 and board_instance.check_for_empty((row + 1, col)):
                moves.append((row + 1, col))
            dc = [[1, 1], [1, -1]]
            for i in range(2):
                new_row, new_col = row + dc[i][0], col + dc[i][1]
                if 0 <= new_row < 8 and 0 <= new_col < 8 and board_instance.check_for_enemy((new_row, new_col), self.color):
                    moves.append((new_row, new_col))

        if self.color == colors['black']:
            if row == 6 and board_instance.check_for_empty((row - 2, col)) and board_instance.check_for_empty((row - 1, col)):
                moves.append((row - 2, col))
            if row - 1 >= 0 and board_instance.check_for_empty((row - 1, col)):
                moves.append((row - 1, col))
            dc = [[-1, 1], [-1, -1]]
            for i in range(2):
                new_row, new_col = row + dc[i][0], col + dc[i][1]
                if 0 <= new_row < 8 and 0 <= new_col < 8 and board_instance.check_for_enemy((new_row, new_col), self.color):
                    moves.append((new_row, new_col))

        return moves

class Rook(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.first_move = True
        self.figure = figures['Rook']

    def valid_moves(self, board_instance):
        moves = []
        row, col = self.position

        directions = [[1, 0], [-1, 0], [0, 1], [0, -1]]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board_instance.check_for_friendly((r, c), self.color):
                    break
                moves.append((r, c))
                if board_instance.check_for_enemy((r, c), self.color):
                    break
                r += dr
                c += dc

        return moves

class Knight(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.figure = figures['Knight']

    def valid_moves(self, board_instance):
        moves = []
        row, col = self.position

        dc = [[1, 2], [1, -2], [-1, 2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1]]

        for i in range(8):
            new_row, new_col = row + dc[i][0], col + dc[i][1]
            if 0 <= new_row < 8 and 0 <= new_col < 8 and not board_instance.check_for_friendly((new_row, new_col), self.color):
                moves.append((new_row, new_col))

        return moves

class Bishop(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.figure = figures['Bishop']

    def valid_moves(self, board_instance):
        moves = []
        row, col = self.position

        directions = [[1, 1], [1, -1], [-1, 1], [-1, -1]]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board_instance.check_for_friendly((r, c), self.color):
                    break
                moves.append((r, c))
                if board_instance.check_for_enemy((r, c), self.color):
                    break
                r += dr
                c += dc

        return moves

class Queen(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.figure = figures['Queen']

    def valid_moves(self, board_instance):
        moves = []
        row, col = self.position

        directions = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board_instance.check_for_friendly((r, c), self.color):
                    break
                moves.append((r, c))
                if board_instance.check_for_enemy((r, c), self.color):
                    break
                r += dr
                c += dc

        return moves

class King(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.figure = figures['King']
        self.destructable = False

    def valid_moves(self, board_instance):
        moves = []
        row, col = self.position

        dc = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

        for i in range(8):
            new_row, new_col = row + dc[i][0], col + dc[i][1]
            if 0 <= new_row < 8 and 0 <= new_col < 8 and not board_instance.check_for_friendly((new_row, new_col), self.color):
                moves.append((new_row, new_col))

        # restricted moves
        enemy_moves = board_instance.enemy_moves(self.color)
        king_position = board_instance.get_enemy_king_position(self.color)
        if king_position:
            restricted_positions = []
            king_dc = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
            king_row, king_col = king_position
            for dr, dc in king_dc:
                new_row, new_col = king_row + dr, king_col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    restricted_positions.append((new_row, new_col))

            moves = [move for move in moves if move not in restricted_positions]
        moves = [move for move in moves if move not in enemy_moves]

        valid_moves = []
        for move in moves:
            future_board = copy.deepcopy(board_instance)
            future_board.board[move[0]][move[1]] = self
            future_board.board[row][col] = None
            future_enemy_moves = future_board.future_enemy_moves(self.color)
            if move not in future_enemy_moves:
                valid_moves.append(move)

        return valid_moves