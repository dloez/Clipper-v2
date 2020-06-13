import sys
import os

from tools.colors import ConsoleColors


class Helper:
    def commander(self, command, args):
        '''
            clear:
                clears console
            exit:
                exits Clipper
        '''
        if command == 'clear':
            filter = self.__filter(args, 0)
            if filter:
                if sys.platform.startswith('linux'):
                    os.system('clear')
                elif sys.platform.startswith('win32'):
                    os.system('cls')
            
            return True
        elif command == 'exit':
            print('I am gonna miss u....')
            sys.exit()
            return True
        return False

    def __filter(self, args, ammount):
        if len(args) >= ammount:
            return True
        else:
            print(ConsoleColors.RED + 'Error: {0}'.format(self.__error_messages[0]) + ConsoleColors.RESET)