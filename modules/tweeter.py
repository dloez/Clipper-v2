import tweepy
import json

from tools.colors import ConsoleColors


class Tweeter:
    def __init__(self, error_messages, p_tokens_file):
        self.__error_messages = error_messages
        self.__p_tokens_file = p_tokens_file

        self.api = ''
        self.__create_connection()

    def commander(self, command, args):
        '''
            tweet (text[0]):
                It tweets, could you believe it?!!! text argument should have '€' character instead of ' ', example -> 'How€u€all€doing?'
        '''
        if command == 'tweet':
            filter = self.__filter(args, 1)
            if filter:
                text = args[0]
                self.api.update_status(text.replace('€', ' '))
            return True
        else:
            return False

    def __filter(self, args, ammount):
        if len(args) >= ammount:
            return True
        else:
            print(ConsoleColors.RED + 'Error: {0}'.format(self.__error_messages[0]) + ConsoleColors.RESET)

    def __get_credentials(self):
        with open(self.__p_tokens_file, 'r') as f:
            credentials = json.load(f)['twitter']

        self.CONSUMER_KEY = credentials['consumer_key']
        self.CONSUMER_SECRET = credentials['consumer_secret']
        self.ACCESS_TOKEN = credentials['access_token']
        self.ACCESS_TOKEN_SECRET = credentials['access_token_secret']
    
    def __create_connection(self):
        self.__get_credentials()

        auth = tweepy.OAuthHandler(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        auth.set_access_token(self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)

        self.api = tweepy.API(auth)