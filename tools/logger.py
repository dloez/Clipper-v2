import os
from datetime import datetime as date
from datetime import timezone
import pytz


class Logger:
    def __init__(self):
        self.log_file = ''

    def __check_file(self):
        if not os.path.exists('log.txt'):
            with open('log.txt', 'x') as f:
                f.write('New log file\n')
        self.log_file = 'log.txt'

    def log(self, data):
        self.__check_file()

        with open(self.log_file, 'a+') as f:
            time = self.__as_localtimezone(date.now())
            f.write(time.strftime('%Y-%m-%d#%H:%M:%S-> ') + data + '\n')

    def separator(self):
        self.__check_file()
        
        with open(self.log_file, 'a+') as f:
            f.write('####################################################\n')

    def __as_localtimezone(self, utc):
        return utc.replace(tzinfo=timezone.utc).astimezone(pytz.timezone('Europe/Madrid'))
