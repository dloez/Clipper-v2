from pathlib import Path
import json


P_TWEETS_JSON = Path('../../twitter/tweets.json')
P_TWEETS_TXT = Path('tweets.txt')

tweets = list()
with open(P_TWEETS_TXT, 'r') as f:
    tweet = ''
    for line in f:
        if line.startswith('#'):
            tweets.append(tweet.replace('(Enlace del vídeo)', '{0}').replace(' ', '€'))
            tweet = ''
            continue

        tweet += line

with open(P_TWEETS_JSON, 'r') as f:
    tweets_json = json.load(f)

tweets_json.extend(tweets)
with open(P_TWEETS_JSON, 'w') as f:
    json.dump(tweets_json, f, ensure_ascii=False, indent=4)