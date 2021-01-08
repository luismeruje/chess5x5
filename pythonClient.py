import manager
import time 
import os
class FileClient:
    #Time between read attempts of file, in seconds
    FILE_POLLING_INTERVAL = 2

    def __init__(self, filename):
        self.initialize_game(filename)

    def initialize_game(self, filename):
        self.file = open(filename,"a+")
        self.file.seek(0)
        #Read start game line
        self.file.readline()
        #Get color
        self.color = self.file.readline().replace('\n','').replace(' ','')

    def get_color(self):
        return self.color

    def write_move(self,move):
        self.file.write(move + os.linesep)

    #Receives moves in UCI format. Returns move played by opponent also in UCI.
    def play_move(self,move):
        self.write_move(move)
        reply = self.process_reply()
        return reply

    def get_opponent_move(self):
        return self.process_reply()

    def process_reply(self):
        reply_read = False
        file_position = self.file.tell()
        while not reply_read:
            self.file = manager.reload_reader(self.file)
            reply = self.file.readline()
            if self.file.tell() == file_position or reply == '':
                self.file.seek(file_position)
                time.sleep(self.FILE_POLLING_INTERVAL)
            else:
                if not "Illegal move" in reply:
                    reply = reply.split(' ')[2]
                    reply = manager.cleanup_move_string(reply)
                reply_read = True
        return reply