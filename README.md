# chess5x5
A manager for handling 5x5 chess, where plays are given through a file assigned to each player.

To setup:
```
pip3 install -r requirements.txt
```
To run: 
```
python3 Manager.py
```

## Manager
The Manager offers the following configurations which can be edited at the top of the manager.py file:
- NR_GAMES -> How many games to play
- FILE_POLLING_INTERVAL -> How often to poll the file for changes. Time interval in seconds.
- MAX_INFRACTIONS -> How many illegal moves before a player is disqualified.
- GUI_ACTIVE -> Boolean value. When set to True will show a graphical interface of the chess board, otherwise the board is printed to the terminal after each play.
- PAUSE_BETWEEN_GAMES -> Boolean value. If set to True, the manager will wait for the user to press a key before proceeding to the next game.

To make moves manually:
- Edit files 'player1.txt' and 'player2.txt' created by the manager. 
- White plays first.
- You may need to reload the file to see modifications between plays, depending on the text editor you are using.
- Files player1.txt and player2.txt in this repository show an example of a full game.
- Don't forget to save the file after writing your move. (When testing manually)
- When a pawn is to be promoted, the figure to promote to must be added at the end, e.g. to promote to queen: b4b5q

## Python client
The use of files to convey plays between players allows for the chess bots to be programmed in any language.

For Python chess bots however, a client is provided.

Usage:

```
# Pseudo-code
import pythonClient

# Will block until manager initiates file
client = pythonClient.FileClient('../player1.txt')

# Possible colors are 'Black' and 'White'
my_color = client.get_color()

if my_color == 'Black':
  #Opponent moves first, so must wait for his play
  (opponent_move,illegal, winner) = self.client.get_opponent_move()

loop:
  #You'll want to compute your move here, in UCI format. e.g. my_move = 'a2a3'
  my_move = compute_move(opponent_move, ...) 
  
  # Winner can take special value of None, if the game hasn't ended, or 'Black', 'White' and 'None' strings. 'None' string (not special value None) means there was a draw.
  # illegal will be True if the move you played is not valid. You must choose a different move in that case.
  # opponent_move returns the opponent move in case your play was valid and if you didn't reach a draw or checkmate with your move.
  (opponent_move,illegal, winner) = client.play_move(my_move)
  

```
TODO:
- Implement time limits
