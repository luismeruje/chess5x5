import chess
import chess.svg
import random 
import time
import os
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget
import sys
import multiprocessing as mp
import _thread 

#Based on: https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python/
#Try to order moves on how likely they are to be good for best alpha-beta pruning improvement
# https://www.youtube.com/watch?v=l-hh51ncgDI


#Time between attempts to read file, in seconds
NR_GAMES = 10
FILE_POLLING_INTERVAL = 0.5
MAX_INFRACTIONS = 3
GUI_ACTIVE = True
PAUSE_BETWEEN_GAMES = True
#Not implemented yet

#Time limit per player in seconds
#TIME_LIMIT= 120
#TIME_LIMIT_ACTIVE = True

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
    if not GUI_ACTIVE:
        print(board)
    if player1_color == 'White':
        return (player1_file, player2_file, board, player1_color, player2_color)
    else:
        return (player2_file, player1_file, board, player1_color, player2_color)

def cleanup_move_string(move):
    return move.lower().replace(" ","").replace("\n","")

def is_move_legal(move,board):
    pawn_double__moves = ["a2a4","b2b4","c2c4","d2d4","e2e4", "a4a2","b4b2","c4c2","d4d2","e4e2"]
    castling = ["e1c1"]
    pawn_promotion_rank5 = ["a5b","b5b","c5b","d5b","e5b","a5n","b5n","c5n","d5n","e5n","a5r","b5r","c5r","d5r","e5r","a5q","b5q","c5q","d5q","e5q"]
    move = move.uci()
    #print('Testing move: ', move)
    if board.piece_at(chess.SQUARES[chess.SQUARE_NAMES.index(move[:2])]).symbol() == 'P':
        if (chess.Move.from_uci(move) in board.legal_moves) and (not move in pawn_double__moves) and is_move_within_5x5_borders(move):
            return True
        #Check if pawn
        elif (move[-3:] in pawn_promotion_rank5) and (chess.Move.from_uci(move[:4]) in board.legal_moves):
            return True
        else:
            return False
    elif (chess.Move.from_uci(move) in board.legal_moves) and (not move in castling) and is_move_within_5x5_borders(move):
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

def is_draw(board):
    if board.is_game_over(claim_draw=True):
        return True
    else:
        possible_moves = board.legal_moves
        for move in possible_moves:
            if is_move_within_5x5_borders(move.uci()):
                return False
    return True

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
            #print("Move raw string:", move)
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

def game_loop(whites_file, blacks_file, board, GUI_enabled = False, window = None):
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
        
        if GUI_enabled:
            window.replaceBoard(board)
            window.reload()

        if is_checkmate(board):
            winner = 'White'
            blacks_file.write('White played ' + str(move) + ' ' + str(winner) + ' wins' + os.linesep)
            whites_file.write(str(winner) + ' wins' + os.linesep)
            whites_file.flush()
            blacks_file.flush()
            game_finished = True
            break
        elif disqualified:
            winner = 'Black'
            blacks_file.write(str(winner) + ' wins' + os.linesep)
            whites_file.write(str(winner) + ' wins' + os.linesep)
            whites_file.flush()
            blacks_file.flush()
            game_finished = True
            break
        elif is_draw(board):
            winner = None
            blacks_file.write('White played ' + str(move) + ' ' + str(winner) + ' wins' + os.linesep)
            whites_file.write(str(winner) + ' wins' + os.linesep)
            whites_file.flush()
            blacks_file.flush()
            game_finished = True
            break
        else:
            blacks_file.write('White played ' + str(move) + os.linesep)
            blacks_file.flush()
            blacks_file_position = blacks_file.tell()

        (blacks_file,move,disqualified) = process_move(blacks_file, blacks_file_position, board)

        if GUI_enabled:
            window.replaceBoard(board)
            window.reload()
        else:
            print(board)
        
        if is_checkmate(board):
            winner = 'Black'
            whites_file.write('Black played ' + str(move) + ' ' + str(winner) + ' wins' + os.linesep)
            blacks_file.write(str(winner) + ' wins' + os.linesep)
            whites_file.flush()
            blacks_file.flush()
            game_finished = True
        elif disqualified:
            winner = 'White'
            whites_file.write(str(winner) + ' wins' + os.linesep)
            blacks_file.write(str(winner) + ' wins' + os.linesep)
            whites_file.flush()
            blacks_file.flush()
            game_finished = True
        elif is_draw(board):
            winner = None
            whites_file.write('Black played ' + str(move) + ' ' + str(winner) + ' wins' + os.linesep)
            blacks_file.write(str(winner) + ' wins' + os.linesep)
            whites_file.flush()
            blacks_file.flush()
            game_finished = True
        else:
            whites_file.write('Black played ' + str(move) + os.linesep)
            whites_file.flush()
            whites_file_position = whites_file.tell()
    return (winner, whites_file, blacks_file)
        


# https://stackoverflow.com/questions/61439815/how-to-display-an-svg-image-in-python
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 850, 850)

        self.widgetSvg = QSvgWidget(parent=self)
        self.widgetSvg.setGeometry(10, 10, 800, 800)

        self.board=chess.Board()#'8/8/8/rnbqk3/ppppp3/8/PPPPP3/RNBQK3')

        self.boardSvg = chess.svg.board(self.board).encode("UTF-8")
        self.widgetSvg.load(self.boardSvg)
    
    def reload(self):
         self.boardSvg = chess.svg.board(self.board).encode("UTF-8")
         self.widgetSvg.load(self.boardSvg) 
        
    def replaceBoard(self, board):
        self.board = board


def run_GUI(app, window):
    window.show()

    app.exec_()

def wait_for_read_confirmation(file):
    confirmation_read = False
    file_position = file.tell()
    while not confirmation_read:
        file = reload_reader(file)
        reply = file.readline()
        if file.tell() == file_position or reply == '':
            file.seek(file_position)
            time.sleep(FILE_POLLING_INTERVAL)
        else:
            confirmation_read = True

def update_scores(player1_wins, player2_wins, winner, player1_color, player2_color, output=False):
    index = None
    if winner == 'Black':
        index = 1
    else:
        index = 0

    if winner == player1_color:
        player1_wins[index] += 1
    else:
        player2_wins[index] += 1

    if output:
        print('Player1 win count')
        print('  White', player1_wins[0])
        print('  Black', player1_wins[1])
        print('Player2 win count')
        print('  White', player2_wins[0])
        print('  Black', player2_wins[1])

    return (player1_wins, player2_wins)
def run_game(GUI_enabled=False, window=None, nr_games=1):
    player1_file_name = 'player1.txt'
    player2_file_name = 'player2.txt'
    #Wins as White/Black
    player1_wins = [0,0]
    player2_wins = [0,0]
    for game_nr in range(nr_games):
        print('\nGame nr.', game_nr)
        
        (whites_file,blacks_file, board, player1_color, player2_color) = setup_new_game(player1_file_name, player2_file_name)
        if GUI_enabled:
            window.replaceBoard(board)
            window.reload()
        (winner, whites_file, blacks_file) = game_loop(whites_file, blacks_file, board, GUI_enabled, window)
        print(str(winner) + ' wins')

        (player1_wins, player2_wins) = update_scores(player1_wins, player2_wins, winner, player1_color, player2_color, output=True)

        wait_for_read_confirmation(whites_file)
        wait_for_read_confirmation(blacks_file)

        whites_file.close()
        blacks_file.close()
        os.rename(player1_file_name, player1_file_name + 'game-' + str(game_nr) + '.txt')
        os.rename(player2_file_name, player2_file_name + 'game-' + str(game_nr) + '.txt')
        if PAUSE_BETWEEN_GAMES:
            input('Press any key for next game...')

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    if GUI_ACTIVE:
        #QApplication doesn't like running on non-main Thread, so run game backend in different thread instead
        try:
            _thread.start_new_thread(run_game, (True,window, NR_GAMES) )
        except Exception as e:
            print("Error: unable to start thread")
            print(e)
        run_GUI(app, window)
    else:
        run_game()
    


if __name__ == "__main__":
    main()
