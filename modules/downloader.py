import json
import os
import requests
from pathlib import Path
from datetime import datetime, timedelta
from pyrfc3339 import generate
import pytz

from tools.colors import ConsoleColors

class Downloader:
    def __init__(self, error_messages, packager, p_tokens_file):
        self.__error_messages = error_messages
        self.__packager = packager
        self.__p_tokens_file = p_tokens_file
    
    def commander(self, command, args):
        '''
            download (package name[0]):
                downloads clips from given package
        '''
        if command == 'download':
            filter = self.__filter(args, 1)
            if filter:
                name = args[0]
                package = self.__packager.get(name)

                for streamer in package.get_data()['streamers']:
                    self.__download(streamer, package)

            return True
        return False
    
    def __filter(self, args, ammount):
        if len(args) >= ammount:
            return True
        else:
            print(ConsoleColors.RED + 'Error: {0}'.format(self.__error_messages[0]) + ConsoleColors.RESET)
    
    def __check_paths(self, path):
        if not os.path.exists(self.__p_packages_file):
            os.mkdir(path)

    def __download(self, streamer, package):
        with open(self.__p_tokens_file, 'r') as f:
            client_id = json.load(f)['twitch']['client_id']
            
        access_token, broad_id = Downloader.check_username(streamer).split("&")

        if package.get_data()['period'] == 'week':
            start = generate(datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(days=7))
            end = generate(datetime.utcnow().replace(tzinfo=pytz.utc))
        elif package.get_data()['period'] == 'month':
            start = generate(datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(days=30))
            end = generate(datetime.utcnow().replace(tzinfo=pytz.utc))

        count = 0
        pagination = ''
        times = list()
        game_ids = dict()
        while count < int(package.get_data()['limit']):
            r = requests.get(
                'https://api.twitch.tv/helix/clips?broadcaster_id=' + broad_id + '&first=' + package.get_data()['limit'] + '&started_at=' + start + '&ended_at=' + end + '&after=' + pagination,
                headers={
                    'Authorization': 'Bearer ' + access_token,
                    'Client-ID': client_id
                }
            )

            clips = r.json()['data']
            if len(clips) > 0:
                for clip in clips:
                    if type(clip) == dict:
                        if clip['game_id'] not in game_ids:
                            game_ids[clip['game_id']] = 1
                        else:
                            game_ids[clip['game_id']] += 1

                        thumbnail_url = clip['thumbnail_url']

                        mp4_url = thumbnail_url.split('-preview', 1)[0] + '.mp4'

                        file_name = Path(package.get_data()['clips_folder']) / clip['id']
                        mp4_name = str(file_name) + '.mp4'

                        #l.log("Downloading: " + str(mp4_name))

                        res = requests.get(mp4_url)
                        with open(mp4_name, 'wb') as f:
                            f.write(res.content)

                        cmd = 'ffprobe -show_entries format=duration -v quiet -of csv="p=0" ' + mp4_name
                        duration = float(os.popen(cmd).read())
                        created_at = datetime.strptime(clip['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                        ended_at = created_at + timedelta(0, duration)

                        exist = False
                        if len(times) > 0:
                            for i in range(len(times)):
                                if times[i]['created_at'] < created_at < times[i]['ended_at']:
                                    exist = True
                                    break
                                else:
                                    time_meta = {
                                        'created_at': created_at,
                                        'ended_at': ended_at
                                    }
                                    times.append(time_meta)
                        else:
                            time_meta = {
                                'created_at': created_at,
                                'ended_at': ended_at
                            }
                            times.append(time_meta)

                        if exist:
                            os.remove(mp4_name)
                        else:
                            count += 1
                            if count >= int(package.get_data()['limit']):
                                break

                pagination = r.json()['pagination']['cursor']
            else:
                raise Exception('Clips not found')
        
        games_sorted = sorted(game_ids.items(), key=lambda x: x[1], reverse=True)

        stop = 1
        if len(games_sorted) > 1:
            stop = 2

        games = list()
        for i in range(stop):
            r = requests.get(
                'https://api.twitch.tv/helix/games?id=' + games_sorted[i][0],
                headers={
                    'Authorization': 'Bearer ' + access_token,
                    'Client-ID': client_id
                }
            )

            games.append(r.json()['data'][0]['name'])

        package.get_data()['additional_info']['games'] = games
        package.update()
    
    @staticmethod
    def check_username(username):
        with open(Path('tokens/tokens.json'), 'r') as f:
            credentials = json.load(f)['twitch']

        try:
            r = requests.post(
                'https://id.twitch.tv/oauth2/token?client_id={0}&client_secret={1}&grant_type=client_credentials'.format(credentials['client_id'], credentials['client_secret'])
            )
            access_token = r.json()['access_token']

            r = requests.get(
                'https://api.twitch.tv/helix/users?login=' + username,
                headers={
                    'Authorization': 'Bearer ' + access_token,
                    'Client-ID': credentials['client_id']
                }
            )
            broad_id = r.json()['data'][0]['id']

            if not broad_id:
                print('Bad request, check username or user banned')
                return False
        except:
            print('Failed to connect to Twitch API')
            return False

        return access_token + '&' + broad_id
