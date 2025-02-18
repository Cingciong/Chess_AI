import pygame
import sys
import copy
from board import Board  # Import the Board class

class ChessGame:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 800, 800
        self.ROWS, self.COLS = 8, 8
        self.SQUARE_SIZE = self.WIDTH // self.COLS

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.LIGHT_BROWN = (240, 217, 181)
        self.DARK_BROWN = (181, 136, 99)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)

        self.WIN = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Chess')

        self.colors = {
            'white': 0,
            'black': 1,
        }
        self.figures = {
            'Pawn': 1,
            'Rook': 2,
            'Knight': 3,
            'Bishop': 4,
            'Queen': 5,
            'King': 6,
        }
        self.reverse_figures = {v: k[0] for k, v in self.figures.items()}

        self.IMAGES = self.load_images()

    def load_images(self):
        pieces = {
            'wp': 'white pawn',
            'bp': 'black pawn',
            'wr': 'white rook',
            'br': 'black rook',
            'wn': 'white knight',
            'bn': 'black knight',
            'wb': 'white bishop',
            'bb': 'black bishop',
            'wq': 'white queen',
            'bq': 'black queen',
            'wk': 'white king',
            'bk': 'black king'
        }
        images = {}
        for piece, name in pieces.items():
            file_name = name.replace(' ', '_') + '.png'
            try:
                images[piece] = pygame.transform.scale(pygame.image.load(f'images/{file_name}'), (self.SQUARE_SIZE, self.SQUARE_SIZE))
            except FileNotFoundError:
                print(f"File not found: images/{file_name}")
        return images

    def draw_board(self):
        self.WIN.fill(self.WHITE)
        for row in range(self.ROWS):
            for col in range(self.COLS):
                color = self.LIGHT_BROWN if (row + col) % 2 == 0 else self.DARK_BROWN
                pygame.draw.rect(self.WIN, color, (col * self.SQUARE_SIZE, row * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))

    def draw_pieces(self, board):
        for row in range(self.ROWS):
            for col in range(self.COLS):
                piece = board[row][col]
                if piece:
                    piece_key = f"{'w' if piece.color == 0 else 'b'}{'n' if piece.__class__.__name__ == 'Knight' else piece.__class__.__name__[0].lower()}"
                    self.WIN.blit(self.IMAGES[piece_key], (col * self.SQUARE_SIZE, row * self.SQUARE_SIZE))

    def highlight_moves(self, piece_position, valid_moves):
        for move in valid_moves:
            if tuple(move[0]) == piece_position:
                row, col = move[1]
                pygame.draw.circle(self.WIN, self.BLUE, (col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2, row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2), self.SQUARE_SIZE // 4)

    def handle_mouse_button_up(self, board_instance, selected_piece, dragging, valid_moves):
        if dragging and selected_piece:
            pos = pygame.mouse.get_pos()
            col, row = pos[0] // self.SQUARE_SIZE, pos[1] // self.SQUARE_SIZE
            end_pos = [row, col]
            start_pos = list(selected_piece.position)
            if [start_pos, end_pos] in valid_moves:
                board_instance.move_piece(tuple(start_pos), tuple(end_pos))
                selected_piece.position = tuple(end_pos)
        return None, False

    def handle_mouse_button_down(self, board_instance, current_turn_color):
        pos = pygame.mouse.get_pos()
        col, row = pos[0] // self.SQUARE_SIZE, pos[1] // self.SQUARE_SIZE
        piece = board_instance.get_piece((row, col))
        if piece and piece.color == self.colors[current_turn_color]:
            selected_piece = piece
            dragging = True
            drag_offset_x = pos[0] - col * self.SQUARE_SIZE
            drag_offset_y = pos[1] - row * self.SQUARE_SIZE
            return selected_piece, dragging, drag_offset_x, drag_offset_y
        return None, False, 0, 0

    def handle_mouse_motion(self, dragging):
        col, row = -1, -1
        if dragging:
            pos = pygame.mouse.get_pos()
            col, row = pos[0] // self.SQUARE_SIZE, pos[1] // self.SQUARE_SIZE
        return col, row

    def main(self):
        turn_iteration = 1
        board_instance = Board()
        board_instance.populate_board()
        selected_piece = None
        valid_moves = []
        dragging = False
        drag_offset_x = 0
        drag_offset_y = 0
        turn = 1
        colors_turn = ['white', 'black']

        run = True
        while run:
            event = pygame.event.wait()

            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    selected_piece, dragging, drag_offset_x, drag_offset_y = self.handle_mouse_button_down(board_instance, colors_turn[turn])
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    selected_piece, dragging = self.handle_mouse_button_up(board_instance, selected_piece, dragging, valid_moves)
                    dragging = False
                    selected_piece = None

            elif event.type == pygame.MOUSEMOTION:
                col, row = self.handle_mouse_motion(dragging)

            if board_instance.is_changed():
                turn = 1 if turn == 0 else 0
                print("Turn:", turn_iteration, colors_turn[turn])
                turn_iteration += 1
                moves = board_instance.get_moves(colors_turn[turn])
                moves_free_check = []
                for move in moves:
                    future_board = copy.deepcopy(board_instance)
                    start_pos = tuple(move[0])
                    end_pos = tuple(move[1])
                    future_board.move_piece(start_pos, end_pos)
                    if not future_board.is_check(colors_turn[turn])[0]:
                        moves_free_check.append([list(move[0]), list(move[1])])  # Convert to lists
                valid_moves = moves_free_check

                print("Is check", board_instance.is_check(colors_turn[turn]))
                if board_instance.check_for_check_mate(colors_turn[turn], valid_moves):
                    print(f"Checkmate! {colors_turn[turn]} is in checkmate!")
                elif board_instance.check_for_pat(colors_turn[turn], valid_moves):
                    print(f"Pat! {colors_turn[turn]} is in pat!")

            self.draw_board()
            self.draw_pieces(board_instance.board)
            if selected_piece:
                self.highlight_moves(selected_piece.position, valid_moves)

            if dragging and selected_piece:
                pos = pygame.mouse.get_pos()
                self.WIN.blit(self.IMAGES[f"{'w' if selected_piece.color == 0 else 'b'}{'n' if selected_piece.__class__.__name__ == 'Knight' else selected_piece.__class__.__name__[0].lower()}"], (pos[0] - drag_offset_x, pos[1] - drag_offset_y))

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    game.main()