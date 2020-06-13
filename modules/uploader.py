import json
import random
from pathlib import Path
import subprocess
import os

from tools.colors import ConsoleColors
from tools.logger import Logger

class Uploader:
    def __init__(self, error_mesages, packager, p_tokens, p_videos_media):
        self.__error_messages = error_mesages
        self.__packager = packager
        
        self.__p_request_token = p_tokens / 'youtube/request.token'
        self.__p_client_secrets = p_tokens / 'youtube/client_secrets.json'
        self.__p_videos_metada = p_videos_media / 'metadata.json'
        
        self.__logger = Logger()

    def commander(self, command, args):
        '''
            upload (package name[0]):
                uploads video to google storage and youtube depending on package settings
        '''
        if command == 'upload':
            filter = self.__filter(args, 1)
            if filter:
                name = args[0]
                package = self.__packager.get(name)

                if not package:
                    return True

                if package.get_data()['upload_google']:
                    self.__upload_google(package)

                if package.get_data()['upload_youtube']:
                    url = self.__upload_youtube(package)

                return url

            return True
        else:
            return False
    
    def __filter(self, args, ammount):
        if len(args) >= ammount:
            return True
        else:
            print(ConsoleColors.RED + 'Error: {0}'.format(self.__error_messages[0]) + ConsoleColors.RESET)

    def __upload_google(self, package):
        cmd = 'gsutil cp {} gs://clipperstorage/output/'.format(package.get_data()['additional_info']['output_video'])
        r = subprocess.run(cmd, shell=True, capture_output=True)
        self.__logger.log('Video {} uploaded to google storage'.format(package.get_data()['additional_info']['output_video']))
        self.__logger.separator()

    def __upload_youtube(self, package):
        with open(self.__p_videos_metada, 'r') as f:
            lang = package.get_data()['language']

            for md in json.loads(f.read())['video_metadata']:
                if md['language'] == lang:
                    data = md

        number = str(random.randint(1, 15))
        thumbnail = Path(package.get_data()['thumbanils_folder']) / str(number + '.png')

        name = package.get_data()['streamers'][0]
        meta = {
            'title': data['title'].format(name),
            'description': data['description'].format(name, package.get_data()['twitch_urls'][0]),
            'privacyStatus': 'public',
            'playlistTitles': [data['playlist'].format(name)],
            'tags': data['tags'].format(name).split(','),
            'language': data['language']
        }

        meta['title'] += ' || '
        for game in package.get_data()['additional_info']['games']:
            meta['title'] += game + ' - '
            meta['tags'].append(game)
            meta['tags'].append(game + ' ' + name)
        meta['title'] = meta['title'][:-2]

        meta_file = Path(package.get_data()['output_folder']) / 'meta_file.json'
        if os.path.exists(meta_file):
            os.remove(meta_file)

        with open(meta_file, 'x') as f:
            json.dump(meta, f)

        cmd = './youtubeuploader -metaJSON {0} -thumbnail {1} -filename {2} -cache {3} -secrets {4}'.format(meta_file, thumbnail, package.get_data()['additional_info']['output_video'], self.__p_request_token, self.__p_client_secrets)
        r = subprocess.run(cmd, shell=True, capture_output=True)

        output = r.stdout
        error = str(r.stderr)
        if 'quota' in error:
            self.__logger.log('Video {} cold not be uploaded to YouTube due to API quota limits'.format(package.get_data()['additional_info']['output_video']))
            self.__logger.separator()
        else:
            self.__logger.log('Video {} uploaded to YouTube'.format(package.get_data()['additional_info']['output_video']))
            self.__logger.separator()
            output = output.decode('utf-8')

            list_output = output.split(' ')
            for i in range(len(list_output)):
                if list_output[i] == 'ID:':
                    index = i + 1

            video_id = list_output[index].replace('\nThumbnail', '')

            url = 'https://www.youtube.com/watch?v=' + video_id
            return url
