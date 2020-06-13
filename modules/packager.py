import json
import random
import os
import shutil

from tools.colors import ConsoleColors

class Packager:
    __DEFAULT_DATA = {
        'limit': 20,
        'period': 'week',
        'language': 'es',
        'upload_google': True,
        'upload_youtube':  True
    }

    def __init__(self, error_messages, p_packages, p_clips, p_outputs, p_videos_media):
        self.__error_messages = error_messages
        self.__p_packages = p_packages
        self.__p_clips = p_clips
        self.__p_outputs = p_outputs
        self.__p_videos_media = p_videos_media

        self.__p_packages_file = ''
        self.__check_paths()

        self.__packages = list()
        self.__load_packages()
    
    def commander(self, command, args):
        '''
            package (action [0] + action args [1]):
                contains all actions performed to any package
                - create (name): creates package/s
                - delete (name): deletes package/s
                - get (name): returns package/s
                - purge (name): deletes package/s paths
        '''
        if command == 'package':
            filter = self.__filter(args, 2)
            if filter:
                action, name = args[0:2]
                if action == 'create':
                    self.__create(name)
                elif action == 'delete':
                    self.__delete(name)
                elif action == 'get':
                    return self.get(name)
                elif action == 'purge':
                    self.__purge(name)
                else:
                    print(ConsoleColors.RED + 'Action not registered' + ConsoleColors.RESET)

            return True
        return False
    
    def __filter(self, args, ammount):
        if len(args) >= ammount:
            return True
        else:
            print(ConsoleColors.RED + 'Error: {0}'.format(self.__error_messages[0]) + ConsoleColors.RESET)
    
    def __check_paths(self):
        self.__p_packages_file = self.__p_packages / 'packages.json'
        
        if not os.path.exists(self.__p_packages_file):
            with open(self.__p_packages_file, 'w') as f:
                f.write('[]')

    def __create(self, name):
        print(ConsoleColors.GREEN + 'Creating package with the name of {}'.format(name) + ConsoleColors.RESET, end='\n\n')

        streamers = list()
        streamer = input('Enter streamer name: ')
        while streamer or not streamers:
            if streamer:
                streamers.append(streamer)
            streamer = input('Enter streamer name: ')

        limit = input('Enter ammount of clips per video (20): ')
        period = input('Enter time period for clips (week): ')
        thumbnails_folder = input('Enter thumbnails folder ({}): '.format(streamers[0]))
        language = input('Enter video language (es): ')
        upload_google = input('Upload videos to google storage? (True): ')
        upload_youtube = input('Upload videos to YouTube? (True): ')

        if not limit:
            limit = self.__DEFAULT_DATA['limit']
        if not period:
            period = self.__DEFAULT_DATA['period']
        if not thumbnails_folder:
            thumbnails_folder = streamers[0]
        if not language:
            language = self.__DEFAULT_DATA['language']
        if not upload_google:
            upload_google = self.__DEFAULT_DATA['upload_google']
        if not upload_youtube:
            upload_youtube = self.__DEFAULT_DATA['upload_youtube']
        
        twitch_urls = list()
        for streamer in streamers:
            twitch_urls.append('https://twitch.tv/{}'.format(streamer))

        package = {
            'name': name,
            'streamers': streamers,
            'twitch_urls': twitch_urls,
            'limit': limit,
            'period': period,
            'clips_folder': str(self.__p_clips / name),
            'output_folder': str(self.__p_outputs / name),
            'thumbanils_folder': str(self.__p_videos_media / 'thumbnails' / thumbnails_folder),
            'language': language,
            'upload_google': bool(upload_google),
            'upload_youtube': bool(upload_youtube),
            'additional_info': {'output_video': '', 'games': []}
        }

        found = False
        for p in self.__packages:
            if p.get_data()['name'] == name:
                found = True
        
        if not found:
            p = _Package(self.__p_packages_file, package)
            p.write()
            self.__packages.append(p)
        else:
            print(ConsoleColors.RED + 'Error: Duplicated package with same name' + ConsoleColors.RESET)
    
    def __delete(self, name):
        if name == 'all':
            for p in self.__packages:
                p.delete()

            self.__packages = list()
            print(ConsoleColors.GREEN + 'Successfully deleted al packages' +  ConsoleColors.RESET)
        else:
            found = False

            new_packages = list()
            for p in self.__packages:
                if p.get_data()['name'] != name:
                    new_packages.append(p)
                else:
                    p.delete()
                    found = True
            
            self.__packages = new_packages
            
            if not found:
                print(ConsoleColors.RED + 'Error: We couldn´t find package with name {}'.format(name) + ConsoleColors.RESET)
            else:
                print(ConsoleColors.GREEN + 'Successfully deleted package with name {}'.format(name) + ConsoleColors.RESET)

    def get(self, name):
        if name == 'all':
            return self.__packages
        else:
            for p in self.__packages:
                if p.get_data()['name'] == name:
                    p.create_paths()
                    return p

        return str(ConsoleColors.RED + 'Error: Package with name {} does not exist'.format(name) + ConsoleColors.RESET)
    
    def __purge(self, name):
        if name == 'all':
            for package in self.__packages:
                package.delete_paths()
        else:
            for package in self.__packages:
                if name == package.get_data()['name']:
                    package.delete_paths()
    
    def __load_packages(self):
        with open(self.__p_packages_file, 'r') as f:
            packages = json.load(f)
        
        for p in packages:
            self.__packages.append(_Package(self.__p_packages_file, p))

# Private class, it SHOULD NOT be able to be used in other classes
class _Package:
    def __init__(self, p_package_file, package):
        self.__package = package
        self.__p_packages_file = p_package_file

    def write(self):
        packages = list()
        with open(self.__p_packages_file, 'r') as f:
            packages = json.load(f)
        
        packages.append(self.__package)
        with open(self.__p_packages_file, 'w') as f:
            json.dump(packages, f, indent=4)
    
    def update(self):
        with open(self.__p_packages_file, 'r') as f:
            packages = json.load(f)

        updated_packages = list()
        for p in packages:
            if p['name'] != self.__package['name']:
                updated_packages.append(p)
            else:
                updated_packages.append(self.__package)
        
        with open(self.__p_packages_file, 'w') as f:
            json.dump(updated_packages, f, indent=4)
    
    def delete(self):
        packages = list()
        with open(self.__p_packages_file, 'r') as f:
            packages = json.load(f)

        updated_packages = list()
        for p in packages:
            if p['name'] != self.__package['name']:
                updated_packages.append(p)
        
        with open(self.__p_packages_file, 'w') as f:
            json.dump(updated_packages, f, indent=4)
    
    def get_data(self):
        return self.__package
    
    def create_paths(self):
        if not os.path.exists(self.__package['clips_folder']):
            os.mkdir(self.__package['clips_folder'])
        
        if not os.path.exists(self.__package['output_folder']):
            os.mkdir(self.__package['output_folder'])
    
    def delete_paths(self):
        shutil.rmtree(self.__package['clips_folder'])
        shutil.rmtree(self.__package['output_folder'])
