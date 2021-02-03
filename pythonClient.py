import manager
import time 
import os



class FileClient:
    #Time between read attempts of file, in seconds
    FILE_POLLING_INTERVAL = 0.2

    def __init__(self, filename):
        self.initialize_game(filename)

    def close(self):
        self.file.close()

    def wait_file_ready(self,filename):
        while(not os.path.exists(filename)):
            time.sleep(self.FILE_POLLING_INTERVAL)
        file_not_ready = True
        while file_not_ready:
            self.file = open(filename,"a+")
            self.file.seek(0)
            #White will be 2, Black can be 2 or 3 if opponent has cast first move
            if len(self.file.readlines()) not in [2,3]:
                self.file.close()
                time.sleep(self.FILE_POLLING_INTERVAL)
            else:
                file_not_ready = False

    def initialize_game(self, filename):
        self.wait_file_ready(filename)
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
        (reply, illegal, winner) = self.process_reply()
        return (reply, illegal, winner)

    def get_opponent_move(self):
        return self.process_reply()

    def process_reply(self):
        reply_read = False
        file_position = self.file.tell()
        illegal = False
        winner = None
        move = None
        while not reply_read:
            self.file = manager.reload_reader(self.file)
            reply = self.file.readline()
            if self.file.tell() == file_position or reply == '':
                self.file.seek(file_position)
                time.sleep(self.FILE_POLLING_INTERVAL)
            else:
                if "Illegal move" in reply:
                    illegal = True
                elif 'win' in reply:
                    split_words = reply.split(' ')
                    if len(split_words) > 4:
                        winner = split_words[3]
                        move = split_words[2]
                        move = manager.cleanup_move_string(move)
                    else:
                        winner = split_words[0]
                    self.file.write('Next game' + os.linesep)
                    #Wait for file to be archived 
                    try:
                        while len(manager.reload_reader(self.file).readlines()) > 3:
                            time.sleep(self.FILE_POLLING_INTERVAL)
                    #Exception ocurring is ok
                    except:
                        print('No file, no problem')
                else:
                    move = reply.split(' ')[2]
                    move = manager.cleanup_move_string(move)
                
                reply_read = True
        return (move, illegal, winner)