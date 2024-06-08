import pygame
import sys
from GameState import *

pygame.init()

DEPTH = 5

width, height = 1100, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Checkers')

button_color = (0, 128, 0)
button_hover_color = (0, 255, 0)
button_text_color = (255, 255, 255)
button_rect = pygame.Rect(875, 300, 150, 50)
button_font = pygame.font.SysFont("Arial", 25)

rows, cols = 8, 8
tile_size = 800 // cols
light_color = (204, 225, 198)
dark_color = (84, 78, 62)

red_pawns = [(0, 1), (0, 3), (0, 5), (0, 7),
            (1, 0), (1, 2), (1, 4), (1, 6),
            (2, 1), (2, 3), (2, 5), (2, 7)]
red_kings = []
black_pawns = [(5, 0), (5, 2), (5, 4), (5, 6),
            (6, 1), (6, 3), (6, 5), (6, 7),
            (7, 0), (7, 2), (7, 4), (7, 6)]
black_kings = []

pawn_radius = tile_size // 2 - 10
red_pawn_color = (161, 0, 21)
black_pawn_color = (26, 26, 26)
king_color = (255, 215, 0)
highlight_color = (255, 255, 255)
move_highlight_color = (255, 255, 255)

selected_pawn = None
selected_color = None
valid_moves = []

current_turn = "black"

text_font = pygame.font.SysFont("Arial", 30)

def draw_button(screen, rect, color, text, text_color):
    pygame.draw.rect(screen, color, rect)
    text_surface = button_font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def reset_game():
    global red_pawns, black_pawns, red_kings, black_kings, current_turn, selected_pawn, selected_color, valid_moves
    red_pawns = [(0, 1), (0, 3), (0, 5), (0, 7),
                 (1, 0), (1, 2), (1, 4), (1, 6),
                 (2, 1), (2, 3), (2, 5), (2, 7)]
    red_kings = []
    black_pawns = [(5, 0), (5, 2), (5, 4), (5, 6),
                   (6, 1), (6, 3), (6, 5), (6, 7),
                   (7, 0), (7, 2), (7, 4), (7, 6)]
    black_kings = []
    current_turn = "black"
    selected_pawn = None
    selected_color = None
    valid_moves = []

    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(800, 200, 300, 30))
    draw_text("Evaluation: 0", text_font, (255, 255, 255), 800, 200)

def draw_text(text, font, text_color, x, y):
    img = font.render(text, text_color, True)
    screen.blit(img, (x, y))

def draw_checkerboard(screen):
    for row in range(rows):
        for col in range(cols):
            color = light_color if (row + col) % 2 == 0 else dark_color
            pygame.draw.rect(screen, color, (col * tile_size, row * tile_size, tile_size, tile_size))

    for (row, col) in valid_moves:
        pygame.draw.rect(screen, move_highlight_color, (col * tile_size, row * tile_size, tile_size, tile_size))

    for (row, col) in red_pawns:
        center = (col * tile_size + tile_size // 2, row * tile_size + tile_size // 2)
        pygame.draw.circle(screen, red_pawn_color, center, pawn_radius)

    for (row, col) in black_pawns:
        center = (col * tile_size + tile_size // 2, row * tile_size + tile_size // 2)
        pygame.draw.circle(screen, black_pawn_color, center, pawn_radius)

    for (row, col) in red_kings:
        center = (col * tile_size + tile_size // 2, row * tile_size + tile_size // 2)
        pygame.draw.circle(screen, red_pawn_color, center, pawn_radius)
        pygame.draw.circle(screen, king_color, center, pawn_radius // 2)

    for (row, col) in black_kings:
        center = (col * tile_size + tile_size // 2, row * tile_size + tile_size // 2)
        pygame.draw.circle(screen, black_pawn_color, center, pawn_radius)
        pygame.draw.circle(screen, king_color, center, pawn_radius // 2)

    if selected_pawn:
        row, col = selected_pawn
        center = (col * tile_size + tile_size // 2, row * tile_size + tile_size // 2)
        pygame.draw.circle(screen, highlight_color, center, pawn_radius + 5, 5)
    
def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // tile_size
    col = x // tile_size
    return row, col

def is_valid_move(start_pos, end_pos, color, is_king):
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    if not (0 <= end_row < rows and 0 <= end_col < cols):
        return False

    if (end_row, end_col) in red_pawns or (end_row, end_col) in black_pawns or (end_row, end_col) in red_kings or (end_row, end_col) in black_kings:
        return False

    direction = 1 if color == "red" else -1

    if is_king:
        directions = [1, -1]
    else:
        directions = [direction]

    for direction in directions:
        if end_row == start_row + direction and abs(end_col - start_col) == 1:
            return True
        if end_row == start_row + 2 * direction and abs(end_col - start_col) == 2:
            mid_row = (start_row + end_row) // 2
            mid_col = (start_col + end_col) // 2
            if color == "red" and ((mid_row, mid_col) in black_pawns or (mid_row, mid_col) in black_kings):
                return True
            elif color == "black" and ((mid_row, mid_col) in red_pawns or (mid_row, mid_col) in red_kings):
                return True
        
    return False

def calculate_valid_moves(pawn_pos, color, is_king):
    moves = []
    directions = [1, -1] if is_king else [1] if color == "red" else [-1]
    for direction in directions:
        for dc in [-1, 1]:
            new_row = pawn_pos[0] + direction
            new_col = pawn_pos[1] + dc
            if is_valid_move(pawn_pos, (new_row, new_col), color, is_king):
                moves.append((new_row, new_col))

            new_row = pawn_pos[0] + 2 * direction
            new_col = pawn_pos[1] + 2 * dc
            if is_valid_move(pawn_pos, (new_row, new_col), color, is_king):
                moves.append((new_row, new_col))
            
            new_row = pawn_pos[0] + 4 * direction
            new_col = pawn_pos[1] + 4 * dc
            if is_valid_move(pawn_pos, (new_row, new_col), color, is_king):
                moves.append((new_row, new_col))

    return moves

def switch_turn():
    global current_turn
    current_turn = "black" if current_turn == "red" else "red"

def check_win():
    if len(black_kings) == 0 and len(black_pawns) == 0:
        draw_text("Red wins!", text_font, (255,255,255), 900, 500)
        print("Red wins!")
        pygame.quit()
        sys.exit
    elif len(red_kings) == 0 and len(red_pawns) == 0:
        draw_text("Black wins!", text_font, (255,255,255), 900, 500)
        print("Black wins!")
        pygame.quit()
        sys.exit

running = True
cache = GameState.load_cache_from_json("eval_cache.json")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            row, col = get_row_col_from_mouse(pos)

            if button_rect.collidepoint(pos):
                reset_game()

            if selected_pawn:
                if (row, col) in valid_moves:
                    start_row, start_col = selected_pawn
                    if selected_color == "red":
                        print("red")
                    elif selected_color == "black":
                        if selected_pawn in black_kings:
                            black_kings.remove(selected_pawn)
                            black_kings.append((row, col))
                        else:
                            black_pawns.remove(selected_pawn)
                            if row == 0:
                                black_kings.append((row, col))
                            else:
                                black_pawns.append((row, col))

                    if abs(row - start_row) == 2:
                        mid_row = (start_row + row) // 2
                        mid_col = (start_col + col) // 2
                        if selected_color == "red":
                            print("red")
                        elif selected_color == "black":
                            if (mid_row, mid_col) in red_pawns:
                                red_pawns.remove((mid_row, mid_col))
                            elif (mid_row, mid_col) in red_kings:
                                red_kings.remove((mid_row, mid_col))
                    
                    selected_pawn = None
                    selected_color = None
                    valid_moves = []

                    switch_turn()
                    state =  GameState(red_pawns, black_pawns, red_kings, black_kings, current_turn)
                    evaluation = state.evaluate(state)
                    pygame.draw.rect(screen, (255,255,255), pygame.Rect(800, 200, 300, 30))
                    draw_text("Evaluation: " + str(evaluation), text_font, (255,255,255), 800, 200)
                    if state.is_terminal(state):
                        print("------------------------------")
                        check_win()
                        pygame.quit()
                        sys.exit()
                    else:
                        best_move = state.minimax(state, DEPTH, float('-inf'), float('inf'), False, cache)
                        state.write_the_best_move_in_cache(state, DEPTH, float('-inf'), float('inf'), False, cache)
                        state = state.apply_move(best_move[1], state)
                        red_pawns, black_pawns, red_kings, black_kings = state.red_pawns, state.black_pawns, state.red_kings, state.black_kings
                        switch_turn()

                    check_win()
                else:
                    if selected_color == "red":
                        print("red")
                    elif selected_color == "black":
                        if (row, col) in black_pawns:
                            selected_pawn = (row, col)
                            valid_moves = calculate_valid_moves(selected_pawn, selected_color, False)
                        elif (row, col) in black_kings:
                            selected_pawn = (row, col)
                            valid_moves = calculate_valid_moves(selected_pawn, selected_color, True)
                        else:
                            selected_pawn = None
                            selected_color = None
                            valid_moves = []
            else:
                if current_turn == "red":
                    print("red")
                elif current_turn == "black":
                    if (row, col) in black_pawns:
                        selected_pawn = (row, col)
                        selected_color = "black"
                        valid_moves = calculate_valid_moves(selected_pawn, selected_color, False)
                    elif (row, col) in black_kings:
                        selected_pawn = (row, col)
                        selected_color = "black"
                        valid_moves = calculate_valid_moves(selected_pawn, selected_color, True)

    draw_checkerboard(screen)
    draw_button(screen, button_rect, button_color, "Restart", button_text_color)
    pygame.display.flip()

pygame.quit()
sys.exit()