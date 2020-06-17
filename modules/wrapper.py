from datetime import datetime as date
from datetime import timezone
import datetime
import time
import pytz
import multiprocessing
import random
import json

from tools.colors import ConsoleColors
from tools.logger import Logger


class Wrapper:
    def __init__(self, error_messages, modules, p_schedule):
        self.__error_messages = error_messages
        self.__modules = modules
        self.__p_schedule = p_schedule
        self.__process = ''

        self.__logger = Logger()

    def commander(self, command, args):
        '''
            auto (hour[0]):
                automatic video processing (download, encode, edit, upload, tweet)
            stop:
                stops auto mode
        '''
        if command == 'auto':
            filter = self.__filter(args, 1)
            if filter:
                t = int(args[0])

                print('Initializing auto clipper....')
                self.__logger.log('Initializing auto clipper, waiting till {}'.format(t))

                self.__process = multiprocessing.Process(target=_auto, args=(self.__modules, self.__p_schedule, t, self.__p_tweets))
                self.__process.start()

            return True
        elif command == 'stop':
            filter = self.__filter(args, 0)
            if filter:
                if self.__process:
                    self.__process.terminate()
                    self.__process = None

                    print('Clipper auto mode stopped')
                else:
                    print('Clipper is not running in auto mode')
            return True
        return False

    def __filter(self, args, ammount):
        if len(args) >= ammount:
            return True
        else:
            print(ConsoleColors.RED + 'Error: {0}'.format(self.__error_messages[0]) + ConsoleColors.RESET)


def _auto(modules, p_schedule, t, p_tweets):
    with open(p_schedule, 'r') as f:
        schedule = json.load(f)

    t = t - 2
    if t < 0:
        t = 24 + t

    d = date.utcnow()
    if d.hour > t:
        d = date.utcnow() + datetime.timedelta(days=1)
    else:
        d = date.utcnow()

    while True:
        target_time = date(d.year, d.month, d.day, t, d.minute, d.second, d.microsecond)

        while date.utcnow() < target_time:
            time.sleep(10)

        d = _as_cest(date.today())
        dayName = d.strftime('%A')

        names = schedule[dayName]

        for name in names:
            modules[1].commander('download', [name])
            modules[2].commander('encode', [name])
            modules[3].commander('edit', [name])
            modules[4].commander('upload', [name])
            modules[5].commander('tweet', [name])
            modules[0].commander('package', ['purge', name])

        d = date.utcnow() + datetime.timedelta(days=1)


def _as_cest(utc):
    return utc.replace(tzinfo=timezone.utc).astimezone(pytz.timezone('Europe/Madrid'))
