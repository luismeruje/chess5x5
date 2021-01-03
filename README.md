# chess5x5
A manager for handling 5x5 chess, where plays are given through a file assigned to each player.

To setup:
pip3 install -r requirements.txt

To run: 
python3 Manager.py

To make moves:
-Edit files player1.txt and player2.txt that the Manager creates. (file names will be passed by argument in the future). 
-White plays first.
-You may need to reload the file to see modifications between plays, depending on the text editor you are using.
-Files player1.txt and player2.txt in this repository show an example of a full game.
-Don't forget to save the file after writing your move. (When testing manually)
-When a pawn is to be promoted, the figure to promote to must be added at the end, e.g. to promote to queen: b4b5q

-For now the board is printed to the console after each move. I will try to add a GUI.

TODO:
- Allow pawns to promote when they reach rank 5
- GUI
- Implement time limits
