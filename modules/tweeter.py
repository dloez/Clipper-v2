import tweepy
import json
import random

from tools.colors import ConsoleColors
from tools.logger import Logger


class Tweeter:
    def __init__(self, error_messages, p_tokens_file, packager, p_tweets):
        self.__error_messages = error_messages
        self.__p_tokens_file = p_tokens_file
        self.__packager = packager
        self.__p_tweets = p_tweets

        self.__api = ''
        self.__create_connection()

        self.__logger = Logger()

    def commander(self, command, args):
        '''
            tweet (text[0]):
                It tweets, could you believe it?!!! text argument should have '€' character instead of ' ', example -> 'How€u€all€doing?'
        '''
        if command == 'tweet':
            filter = self.__filter(args, 1)
            if filter:
                name = args[0]
                package = self.__packager.get(name)

                with open(self.__p_tweets, 'r') as f:
                    tweets = json.load(f)

                tweet = random.choice(tweets)
                twitter_video = package.get_data()['twitter_video']
                res = self.__api.media_upload(twitter_video)
                print(res)
                '''
                self.__api.update_status(status=tweet.replace('€', ' ').format(package.get_data()['url_video']), media_ids=[twitter_video])
                '''
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

        self.__api = tweepy.API(auth)