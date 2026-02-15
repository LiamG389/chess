# Chess pieces: By Cburnett - Own work, CC BY-SA 3.0, https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces

import pygame
import requests
from tkinter import *

# Setup
piece_name = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
board = []
pieces = []
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
selected_piece = None
current_turn = "white"
last_move = None
full_move = 1
ai_enabled = False
ai_difficulty = 0
status_message = "WHITE To Move."
# Config Screen

def go():
    global ai_enabled, ai_difficulty
    ai_enabled = True if opt.get() == "Player Vs. Computer" else False
    if opt2.get() == "Easy":
        ai_difficulty = 6
    elif opt2.get() == "Medium":
        ai_difficulty = 10
    else:
        ai_difficulty = 14
    master.destroy()

master = Tk()
master.geometry("300x150")
master.title("Chess")
directions = Label(master, text="Choose a Game Mode:")
directions.pack()
options = ["Player Vs. Player", "Player Vs. Computer"]
opt = StringVar(value="Player Vs. Player")
menu = OptionMenu(master, opt, *options)
menu.pack()
Label(master, text="Select a difficulty \n (Only Applies if Playing COMPUTER):").pack()
options2 = ["Easy", "Medium", "Hard"]
opt2 = StringVar(value="Easy")
OptionMenu(master, opt2, *options2).pack()
go = Button(master, text="Start", command=go)
go.pack()
master.mainloop()


#Game starts here!!!

pygame.init()


#crappy code alert:
def do_some_king_stuff(king):
    if piece['has_moved'] == False:
        king_home = 60 if piece['color'] == "white" else 4
        piece_on_home = does_have_piece(king_home)
        if piece_on_home['name'] == "king" and piece_on_home['color'] == piece['color']:
            piece_on_rook_home = does_have_piece(7 if piece['color'] == "black" else 63) # King-side castling
            if piece_on_rook_home is not None:
                if piece_on_rook_home['name'] == "rook" and piece_on_rook_home['color'] == piece['color'] and piece_on_rook_home['has_moved'] == False:
                    if square_relation(piece, 5 if piece['color'] == "black" else 61) == "empty" and square_relation(piece, 6 if piece['color'] == "black" else 62) == "empty":
                        valid_moves.append("K" if piece['color'] == "white" else "k")
            piece_on_rook_queen_side = does_have_piece(0 if piece['color'] == "black" else 56)
            if piece_on_rook_queen_side is not None:
                if piece_on_rook_queen_side['name'] == "rook" and piece_on_rook_queen_side['color'] == piece['color'] and piece_on_rook_queen_side['has_moved'] == False:
                    if square_relation(piece, 57 if piece['color'] == "white" else 1) == "empty" and square_relation(piece, 58 if piece['color'] == "white" else 2) == "empty" and square_relation(piece, 59 if piece['color'] == "white" else 3) == "empty":
                        valid_moves.append("Q" if piece['color'] == "white" else "q")
    return sorted(valid_moves)

def index_to_algebraic(n):
    file = chr(ord('a') + (n % 8))
    rank = 8 - (n // 8)
    return file + str(rank)

def does_have_piece(square_index): # Takes a 0-63 square index. Either returns the dict of the piece on that square or None
    for piece in pieces:
        if piece['square'] == square_index:
             return piece
    return None

def algebraic_to_index(alge):
    file = ord(alge[0]) - ord('a')
    rank = int(alge[1])
    row = 8-rank
    col = file
    return row*8+col

def square_relation(piece, square): # Takes a pice dict and a 0-63 square index.
    occupant = does_have_piece(square)
    if occupant is None:
       return "empty"
    elif occupant['color'] == piece['color']:
       return "friendly"
    return "enemy"

def isattacked(piecepar):
    for piece in pieces:
        valid_moves = compute_valid_moves(piece)
        if piecepar['square'] in valid_moves:
            return True
    return False

def find_king(color):
    for piece in pieces:
        if piece['name'] == "king" and piece['color'] == color:
            return piece

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

def get_castling_letters():
    # Returns a list of castling rights letters (KQkq) based on board state
    rights = []
    # White
    white_king = find_king("white")
    if white_king and not white_king.get("has_moved", False):
        # King-side rook (h1, index 63)
        rook_k = does_have_piece(63)
        if rook_k and rook_k.get("name") == "rook" and rook_k.get("color") == "white" and not rook_k.get("has_moved", False):
            rights.append("K")
        # Queen-side rook (a1, index 56)
        rook_q = does_have_piece(56)
        if rook_q and rook_q.get("name") == "rook" and rook_q.get("color") == "white" and not rook_q.get("has_moved", False):
            rights.append("Q")
    # Black
    black_king = find_king("black")
    if black_king and not black_king.get("has_moved", False):
        # King-side rook (h8, index 7)
        rook_k = does_have_piece(7)
        if rook_k and rook_k.get("name") == "rook" and rook_k.get("color") == "black" and not rook_k.get("has_moved", False):
            rights.append("k")
        # Queen-side rook (a8, index 0)
        rook_q = does_have_piece(0)
        if rook_q and rook_q.get("name") == "rook" and rook_q.get("color") == "black" and not rook_q.get("has_moved", False):
            rights.append("q")
    return rights

def exportFEN():
    fen = ""
    pieces_fen = ""
    count = 0
    for i, square in enumerate(board):
        if does_have_piece(i) is not None:
            if count != 0:
                pieces_fen += str(count)
                count = 0
            piece_obj = does_have_piece(i)
            if piece_obj["color"] == "white":
                if piece_obj["name"] == "knight":
                    pieces_fen += "N"
                else:
                    pieces_fen += piece_obj["name"][0].upper()
            else:
                if piece_obj["name"] == "knight":
                    pieces_fen += "n"
                else:
                    pieces_fen += piece_obj["name"][0]
        else:
            count += 1
        if i % 8 == 7:
            if count != 0:
                pieces_fen += str(count)
                count = 0
            if i != 63:
                pieces_fen += "/"
    togo = "w" if current_turn == "white" else "b"
    fen = " ".join([pieces_fen, togo])
    # Castling rights using new helper
    castling_letters = get_castling_letters()
    castling_rights_str = "".join(castling_letters) if castling_letters else "-"
    fen += " " + castling_rights_str
    # En passant
    en_passant = "-"
    if last_move is not None:
        # Only set en passant square if the opposing side has a pawn that could capture it
        if last_move['piece']['name'] == "pawn" and abs(last_move["to"] - last_move['from']) == 16:
            passed_over = (last_move["from"] + last_move["to"]) // 2
            # Determine which side could capture en passant
            ep_file = passed_over % 8
            ep_rank = passed_over // 8
            # The capturing color is the side to move
            capturing_color = "white" if current_turn == "white" else "black"
            pawn_row = ep_rank + (1 if capturing_color == "white" else -1)
            found_capturer = False
            # Check left and right of ep square for a pawn of the capturing color
            for dfile in (-1, 1):
                pawn_file = ep_file + dfile
                if 0 <= pawn_file < 8 and 0 <= pawn_row < 8:
                    idx = pawn_row * 8 + pawn_file
                    capturer = does_have_piece(idx)
                    if capturer is not None and capturer['name'] == "pawn" and capturer['color'] == capturing_color:
                        found_capturer = True
                        break
            # Only set en passant square if a pawn can actually capture
            # This check is needed because FEN requires the en passant square to be set only when a pawn can capture it
            if found_capturer:
                en_passant = index_to_algebraic(passed_over)
    fen += " " + en_passant
    # Halfmove clock 
    halfmove_clock = 0
    if last_move is not None:
        piece = last_move['piece']
        # Check if pawn move
        if piece['name'] == "pawn":
            halfmove_clock = 0
        else:
            # Check if any capture occurred
            captured = False
            to_sq = last_move['to']
            from_sq = last_move['from']
            occupant = None
            for p in pieces:
                if p['square'] == to_sq and p is not piece:
                    occupant = p
                    break
            if occupant is not None:
                captured = True
            if piece['name'] == "pawn" and abs(to_sq % 8 - from_sq % 8) == 1 and does_have_piece(to_sq) is None:
                captured = True
            if captured:
                halfmove_clock = 0
            else:
                # Try to keep track of halfmove clock; for now, just increment by 1
                try:
                    prev_fen = getattr(exportFEN, "_halfmove_clock", 0)
                    halfmove_clock = prev_fen + 1
                except Exception:
                    halfmove_clock = 1
        # Save for next call
        exportFEN._halfmove_clock = halfmove_clock
    else:
        halfmove_clock = 0
        exportFEN._halfmove_clock = halfmove_clock
    fen += " " + str(halfmove_clock)
    fen += " " + str(full_move)
    print(fen)
    return fen
    

def get_ai_move(fen, depth=12, max_thinking_time = 50):
    url = "https://chess-api.com/v1"
    payload = {
        "fen": fen,
        "depth": depth,
        "maxThinkingTime": max_thinking_time, 
        "variants" : 1
    }
    try:
        response = requests.post(
            url, 
            headers={"Content-Type": "application/json"},
            json = payload,
            timeout=10
        )
        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            print("API ERROR", response.status_code)
            return None
    except Exception as e:
        print("REQUEST FAILED", e)
        return None

def apply_ai_move(): 
    global current_turn, last_move, full_move
    fen = exportFEN()
    result = get_ai_move(fen, depth=ai_difficulty)
    if result is None:
        return 
    from_sq = algebraic_to_index(result["from"])
    to_sq = algebraic_to_index(result['to'])
    piece = does_have_piece(from_sq)
    if piece is None:
        return
    old_square = piece['square']
    occupant = does_have_piece(to_sq)
    if occupant is not None:
        pieces.remove(occupant)
    if piece['name'] == "pawn" and occupant is None and to_sq % 8 != old_square % 8:
        direction = -1 if piece['color'] == "white" else 1
        captured_square = to_sq - (8*direction)
        captured = does_have_piece(captured_square)
        if captured:
            pieces.remove(captured)
    if piece["name"] == "king" and abs(to_sq - old_square) == 2:
        if to_sq == 62:
            rook = does_have_piece(63)
            rook["square"] = 61
        elif to_sq == 58:
            rook = does_have_piece(56)
            rook["square"] = 59
        elif to_sq == 6:
            rook = does_have_piece(7)
            rook["square"] = 5
        elif to_sq == 2:
            rook = does_have_piece(0)
            rook["square"] = 3
    piece['square'] = to_sq
    piece['has_moved'] = True
    if current_turn == "black":
        full_move += 1
    current_turn = "black" if current_turn == "white" else "white"
    last_move = {"piece": piece, "from": old_square, "to": to_sq}
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
                                    raw_moves = compute_valid_moves(selected_piece)
                                    valid_moves = []
                                    for move in raw_moves:
                                        snapshot = {
                                            "moved_piece": selected_piece,
                                            "original_square": selected_piece['square'],
                                            "has_moved": selected_piece.get('has_moved', False),
                                            "captured_piece": None,
                                            "captured_square": None,
                                            "rook": None,
                                            "rook_original_square": None,
                                            "rook_has_moved": None,
                                        }
                                        simulate_ok = True
                                        is_en_passant = False
                                        captured_piece = None
                                        captured_square = None
                                        rook = None
                                        rook_from = None
                                        rook_to = None
                                        rook_has_moved = None
                                        old_square = selected_piece['square']
                                        if selected_piece['name'] == "pawn":
                                            occupant = does_have_piece(move)
                                            if occupant is None and move % 8 != old_square % 8:
                                                is_en_passant = True
                                                direction = -1 if selected_piece['color'] == "white" else 1
                                                captured_square = move - (8 * direction)
                                                captured_piece = does_have_piece(captured_square)
                                            else:
                                                captured_piece = occupant
                                                captured_square = move if captured_piece is not None else None
                                        elif selected_piece['name'] == "king" and abs(move - old_square) == 2:
                                            if move == 62:
                                                rook = does_have_piece(63)
                                                rook_from = 63
                                                rook_to = 61
                                            elif move == 58:
                                                rook = does_have_piece(56)
                                                rook_from = 56
                                                rook_to = 59
                                            elif move == 6:
                                                rook = does_have_piece(7)
                                                rook_from = 7
                                                rook_to = 5
                                            elif move == 2:
                                                rook = does_have_piece(0)
                                                rook_from = 0
                                                rook_to = 3
                                            captured_piece = does_have_piece(move)
                                            captured_square = move if captured_piece is not None else None
                                        else:
                                            occupant = does_have_piece(move)
                                            captured_piece = occupant
                                            captured_square = move if captured_piece is not None else None
                                        if rook is not None:
                                            rook_has_moved = rook.get('has_moved', False)
                                        if captured_piece is not None:
                                            try:
                                                pieces.remove(captured_piece)
                                            except Exception:
                                                pass
                                        if rook is not None:
                                            snapshot["rook"] = rook
                                            snapshot["rook_original_square"] = rook_from
                                            snapshot["rook_has_moved"] = rook_has_moved
                                            rook['square'] = rook_to
                                        selected_piece['square'] = move
                                        if selected_piece['name'] == "pawn" and is_en_passant:
                                            if captured_piece is not None:
                                                try:
                                                    pieces.remove(captured_piece)
                                                except Exception:
                                                    pass
                                        selected_piece['has_moved'] = True
                                        king = find_king(current_turn)
                                        if king is not None and not isattacked(king):
                                            valid_moves.append(move)
                                        selected_piece['square'] = snapshot['original_square']
                                        selected_piece['has_moved'] = snapshot['has_moved']
                                        if captured_piece is not None:
                                            pieces.append(captured_piece)
                                        if rook is not None:
                                            rook['square'] = rook_from
                                            if rook_has_moved is not None:
                                                rook['has_moved'] = rook_has_moved
                                    selected_piece["valid_moves"] = valid_moves
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
                                if current_turn == "black":
                                    full_move += 1
                                current_turn = "black" if current_turn == "white" else "white"
                                if ai_enabled == False:
                                    status_message = f"{current_turn.upper()} To Move."
                                selected_piece['has_moved'] = True
                                last_move = {"piece": selected_piece, "from": old_square, "to": i}
                                king = find_king(current_turn)
                                in_check = isattacked(king)
                                legal_moves_exist = False
                                for piece in pieces:
                                    if piece['color'] == current_turn:
                                        if compute_valid_moves(piece):
                                            legal_moves_exist = True
                                            break
                                if not legal_moves_exist:
                                    if in_check:
                                        status_message = f"Checkmate!"
                                    else:
                                        status_message = "Stalemate!"
                                if ai_enabled and current_turn == "black":
                                    status_message = "AI Thinking..."
                                    apply_ai_move()
                                    status_message = "WHITE To Move."
                                for piece in pieces:
                                    if piece['color'] == current_turn:
                                        if compute_valid_moves(piece):
                                            legal_moves_exist = True
                                            break
                                if not legal_moves_exist:
                                    if in_check:
                                        status_message = f"Checkmate!"
                                    else:
                                        status_message = "Stalemate!"
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
    pygame.draw.rect(screen, (50, 50, 50), (0, 400, 400, 25))  # Dark bar at bottom
    font = pygame.font.SysFont(None, 24)
    text_surf = font.render(status_message, True, (255, 255, 255))
    screen.blit(text_surf, (5, 402))
    pygame.display.flip()
pygame.quit()
