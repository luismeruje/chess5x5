import chess
import random 
import time
import os

#Time between attempts to read file, in seconds
FILE_POLLING_INTERVAL = 2
MAX_INFRACTIONS = 3
#Not implemented yet

#Time limit per player in seconds
#TIME_LIMIT= 120
#TIME_LIMIT_ACTIVE = True
#GUI_ACTIVE = FALSE
""" 
#Use SVG render to show GUI
#Have to deal with draws

if move in board.legal_moves:
    board.push(move) """

def reload_reader(reader):
    reader_position = reader.tell()
    reader_file_name = reader.name
    reader.close()
    reader = open(reader_file_name,'a+')
    reader.seek(reader_position)
    return reader



def setup_new_game(player1_file_name,player2_file_name):
    player1_file = open(player1_file_name,"w+")
    player2_file = open(player2_file_name,"w+")

    player1_file.write('Start game' + os.linesep)
    player2_file.write('Start game' + os.linesep)

    colors = ['White','Black']
    player1_color = random.sample(colors, 1)[0]
    colors.remove(player1_color)
    player2_color = colors[0]
    
    player1_file.flush()
    player2_file.flush()
    
    board=chess.Board('8/8/8/rnbqk3/ppppp3/8/PPPPP3/RNBQK3')
    print(board)
    if player1_color == 'White':
        return (player1_file, player2_file, board)
    else:
        return (player2_file, player1_file, board)

def cleanup_move_string(move):
    return move.lower().replace(" ","").replace("\n","")

def is_move_legal(move,board):
    pawn_double__moves = ["a2a4","b2b4","c2c4","d2d4","e2e4", "a4a2","b4b2","c4c2","d4d2","e4e2"]
    castling = ["e1c1"]
    pawn_promotion_rank5 = ["a5b","b5b","c5b","d5b","e5b","a5n","b5n","c5n","d5n","e5n","a5r","b5r","c5r","d5r","e5r","a5q","b5q","c5q","d5q","e5q"]
    move = move.uci()
    print('Testing move: ', move)
    if (chess.Move.from_uci(move) in board.legal_moves) and (not move in pawn_double__moves) and (not move in castling) and is_move_within_5x5_borders(move):
        return True
    #Check if pawn
    elif (move[-3:] in pawn_promotion_rank5) and (chess.Move.from_uci(move[:4]) in board.legal_moves):
        return True
    else:
        return False

#Redo with ord > x and ord < y
def is_move_within_5x5_borders(move):
    cleanup_move_string(move)
    if (ord('a') <= ord(move[0]) <= ord('e')) and (ord('a') <= ord(move[2]) <= ord('e')) and (ord('1') <= ord(move[1]) <= ord('5')) and (ord('1') <= ord(move[3]) <= ord('5')):
        return True
    else:
        return False

def is_checkmate(board):
    if board.is_check():
        possible_moves = board.legal_moves
        for move in possible_moves:
            if is_move_within_5x5_borders(move.uci()):
                return False
        return True
    else:
        return False

def process_move(file, file_position, board):
    move_processed = False
    disqualified = False
    illegal_moves_count = 0
    while (not move_processed) and (illegal_moves_count < MAX_INFRACTIONS):
        file = reload_reader(file)
        move = file.readline()
        if file.tell() == file_position:
            time.sleep(FILE_POLLING_INTERVAL)
        else:
            print("Move raw string:", move)
            move = cleanup_move_string(move)
            try:
                move = chess.Move.from_uci(move)
                if is_move_legal(move, board):
                    board.push(move)
                    move_processed = True
            except Exception as e:
                print('Invalid String received')
                print(e)

            if not move_processed:
                print('Illegal move attempted')
                file.write('Illegal move' + os.linesep)
                file_position = file.tell()
                illegal_moves_count+=1
    if illegal_moves_count >= 3:
        disqualified = True

    return (file,chess.Move.uci(move), disqualified)

def game_loop(whites_file, blacks_file, board):
    #I think I can do this without the tell's everywhere
    whites_file.write('White' + os.linesep)
    whites_file.flush()
    blacks_file.write('Black' + os.linesep)
    blacks_file.flush()
    whites_file_position = whites_file.tell()
    blacks_file_position = blacks_file.tell()
    disqualified = False
    winner = None
    game_finished = False
    while not game_finished:
        (whites_file,move,disqualified) = process_move(whites_file, whites_file_position, board)
        print(board)
        blacks_file.write('White played ' + str(move) + os.linesep)
        blacks_file.flush()
        blacks_file_position = blacks_file.tell()
        if is_checkmate(board):
            winner = 'White'
            game_finished = True
            break
        elif disqualified:
            winner = 'Black'
            game_finished = True
            break
        (blacks_file,move,disqualified) = process_move(blacks_file, blacks_file_position, board)
        print(board)
        whites_file.write('Black played ' + str(move) + os.linesep)
        whites_file.flush()
        whites_file_position = whites_file.tell()
        if is_checkmate(board):
            winner = 'Black'
            game_finished = True
        elif disqualified:
            winner = 'White'
            game_finished = True
    return winner
        


def main():
    player1_file_name = 'player1.txt'
    player2_file_name = 'player2.txt'
    (whites_file,blacks_file, board) = setup_new_game(player1_file_name, player2_file_name)
    winner = game_loop(whites_file, blacks_file, board)
    print(winner + ' wins')

if __name__ == "__main__":
    main()
