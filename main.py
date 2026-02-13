# Chess pieces: By Cburnett - Own work, CC BY-SA 3.0, https://commons.wikimedia.org/w/index.php?curid=1499803
# TODO: King checks
# TODO: En Passent
# TODO: Stockfish Implementation with chess-api.com (model code in chess frame)

import pygame
import math


# Setup
piece_name = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
board = []
pieces = []
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
selected_piece = None
current_turn = "white"
last_move = None
pygame.init()


def does_have_piece(square_index): # Takes a 0-63 square index. Either returns the dict of the piece on that square or None
    for piece in pieces:
        if piece['square'] == square_index:
             return piece
    return None


def square_relation(piece, square): # Takes a pice dict and a 0-63 square index.
    occupant = does_have_piece(square)
    if occupant is None:
       return "empty"
    elif occupant['color'] == piece['color']:
       return "friendly"
    return "enemy"


def compute_valid_moves(piece): # Takes a piece dict. Eg: {"name": piece, "square" : i, 'valid_moves': [], 'id' : i, "special_moves" : special_moves, "color" : "black"}
    current_square = piece['square']
    row = current_square // 8
    col = current_square % 8
    valid_moves = []
    directions = []
    if piece['name'] == "rook":
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    elif piece['name'] == "bishop":
        directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
    elif piece['name'] == "queen":
        directions = [(1, 1), (-1, -1), (1, -1), (-1, 1),(1, 0), (-1, 0), (0, 1), (0, -1)]
    elif piece['name'] == 'knight':
        directions = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1)]
    elif piece['name'] == "king":
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    if piece['name'] == "pawn":
        direction = -1 if piece['color'] == "white" else 1
        new_row = row+direction
        if 0 <= new_row < 8:
             target_square = new_row*8 + col
             if square_relation(piece, target_square) == "empty":
                  valid_moves.append(target_square)
        starting_row = 6 if piece['color'] == "white" else 1
        if row == starting_row:
             two_forward_r = row + 2 * direction
             one_forward_s = (row + direction) * 8 + col
             two_forward_s = two_forward_r * 8 + col
             if square_relation(piece, one_forward_s) == "empty" and square_relation(piece, two_forward_s) == "empty":
                  valid_moves.append(two_forward_s)
        for x in (-1, 1):
             new_col = col + x
             if 0 <= new_col < 8:
                  diag_square = new_row * 8 + new_col
                  if square_relation(piece, diag_square) == "enemy":
                       valid_moves.append(diag_square)
        if last_move is not None:
            if last_move["piece"]["name"] == "pawn" and last_move['piece']['color'] != piece['color']:
                if abs(last_move["to"] - last_move["from"]) == 16:
                    last_col = last_move['to'] % 8
                    last_row = last_move['to'] // 8
                    if abs(last_col - col) == 1 and last_row == row:
                        valid_moves.append(last_move["piece"]["square"] + (direction * 8))
    elif piece['name'] == "rook" or piece['name'] == "bishop" or piece['name'] == "queen":
        for x, y, in directions:
             r = row + x
             c = col + y
             while 0 <= r < 8 and 0 <= c < 8:
                  idx = r * 8 + c
                  relation = square_relation(piece, idx)
                  if relation == "empty":
                       valid_moves.append(idx)
                  elif relation == "enemy":
                       valid_moves.append(idx)
                       break
                  else:
                       break
                  r += x
                  c += y
    elif piece['name'] == 'knight' or piece['name'] == "king":
        for x, y in directions:
             new_r = row + x
             new_c = col + y 
             if 0 <= new_r < 8 and 0 <= new_c < 8:
                  idx = new_r * 8 + new_c
                  relation = square_relation(piece, idx)
                  if relation == "empty" or relation == "enemy":
                       valid_moves.append(idx)
        if piece['name'] == "king":
            if piece['has_moved'] == False:
                king_home = 60 if piece['color'] == "white" else 4
                piece_on_home = does_have_piece(king_home)
                if piece_on_home['name'] == "king" and piece_on_home['color'] == piece['color']:
                    piece_on_rook_home = does_have_piece(7 if piece['color'] == "black" else 63) # King-side castling
                    if piece_on_rook_home is not None:
                        if piece_on_rook_home['name'] == "rook" and piece_on_rook_home['color'] == piece['color'] and piece_on_rook_home['has_moved'] == False:
                            if square_relation(piece, 5 if piece['color'] == "black" else 61) == "empty" and square_relation(piece, 6 if piece['color'] == "black" else 62) == "empty":
                                valid_moves.append(62 if piece['color'] == "white" else 6)
                    piece_on_rook_queen_side = does_have_piece(0 if piece['color'] == "black" else 56)
                    if piece_on_rook_queen_side is not None:
                        if piece_on_rook_queen_side['name'] == "rook" and piece_on_rook_queen_side['color'] == piece['color'] and piece_on_rook_queen_side['has_moved'] == False:
                            if square_relation(piece, 57 if piece['color'] == "white" else 1) == "empty" and square_relation(piece, 58 if piece['color'] == "white" else 2) == "empty" and square_relation(piece, 59 if piece['color'] == "white" else 3) == "empty":
                                valid_moves.append(58 if piece['color'] == "white" else 2)

    return valid_moves


# pieces - crappy code alert!
# white pieces
for i,piece in enumerate(piece_name):
    special_moves = "none"
    pieces.append({"name": piece, "square" : i, 'valid_moves': [], 'id' : i, "has_moved" : False, "color" : "black"})


for x in range(8):
  pieces.append({"name": "pawn", "square" : 8+x, 'valid_moves': [], 'id' : i, "has_moved" : False, "color" : "black"})
# black pieces
for i,piece in enumerate(piece_name):
    special_moves = "none"
    pieces.append({"name": piece, "square" : 56+i, 'valid_moves': [], 'id' : i, "has_moved" : False, "color" : "white"})


for x in range(8):
  pieces.append({"name": "pawn", "square" : 48+x, 'valid_moves': [], 'id' : i, "has_moved" : False, "color" : "white"})


# board
SQUARE_SIZE = 50
for index in range(64):
    row = index // 8
    col = index % 8


    x = col * SQUARE_SIZE
    y = row * SQUARE_SIZE


    rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)


    board.append({
        "rect": rect,
        "pos_coords": [x + 25, y + 25], 
        "row": row,
        "col": col,
        "color": 'black' if (row + col) % 2 else 'white',
        "can_click": True,
        "has_piece": False,
        "id": index
    })


# Set up the game window
screen = pygame.display.set_mode((400, 425))
pygame.display.set_caption("Chess")


#Load Images
PIECE_SIZE = 45
piece_images = {}
piece_types = ["pawn", "rook", "knight", "bishop", "queen", "king"]
colors = ["white", "black"]


for piece in piece_types:
  for color in colors:
      piece_name = f"piece-sprites/{piece}{color}.png"
      img = pygame.image.load(piece_name).convert_alpha()
      img = pygame.transform.smoothscale(img, (PIECE_SIZE, PIECE_SIZE))
      piece_images[f"{piece}_{color}"] = img


# Game loop
running = True
while running:
    screen.fill((128, 128, 128))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
             running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for i, square in enumerate(board):
                  if square['rect'].collidepoint(mouse_pos):
                       if selected_piece is None:
                            for piece in pieces:
                                if piece['square'] == i and piece['color'] == current_turn:
                                     selected_piece = piece
                                     selected_piece["valid_moves"] = compute_valid_moves(selected_piece)
                                     break
                       else:
                            if i in selected_piece['valid_moves']:
                                occupant = does_have_piece(i)
                                old_square = selected_piece['square']
                                if occupant is not None and occupant['color'] != selected_piece["color"]:
                                     pieces.remove(occupant)
                                if selected_piece['name'] == "pawn" and occupant is None and i % 8 != old_square % 8:
                                    direction = -1 if selected_piece['color'] == "white" else 1
                                    captured_square = i - (8 * direction)
                                    captured = does_have_piece(captured_square)
                                    pieces.remove(captured)
                                if selected_piece['name'] == "king" and abs(i - old_square) == 2:
                                    if i == 62:
                                        rook = does_have_piece(63)
                                        rook['square'] = 61
                                        rook['has_moved'] = True
                                    if i == 6:
                                        rook = does_have_piece(7)
                                        rook['square'] = 5
                                        rook['has_moved'] = True
                                    if i == 58:
                                        rook = does_have_piece(56)
                                        rook['square'] = 59
                                        rook['has_moved'] = True
                                    if i == 2:
                                        rook = does_have_piece(0)
                                        rook['square'] = 3
                                        rook['has_moved'] = True
                                selected_piece['square'] = i
                                current_turn = "black" if current_turn == "white" else "white"
                                selected_piece['has_moved'] = True
                                last_move = {"piece": selected_piece, "from": old_square, "to": i}
                            selected_piece = None
                 
    for square in board:
        color = (248, 209, 166) if square['color'] == 'white' else (200, 144, 82)
        pygame.draw.rect(screen, color, square['rect'])
        if selected_piece is not None and square["id"] == selected_piece["square"]:
             pygame.draw.rect(screen, (27, 179, 11), square['rect'], 4)
        if selected_piece and square["id"] in selected_piece["valid_moves"]:
             pygame.draw.rect(screen, (255, 0, 0), square['rect'], 3)
    # Create the pieces
    for piece in pieces:
        square = board[piece["square"]] 
        center = square['pos_coords']
        key = f"{piece['name']}_{piece['color']}"
        img = piece_images[key]
        rect = img.get_rect(center=center)
        screen.blit(img, rect)
    pygame.display.flip()
pygame.quit()