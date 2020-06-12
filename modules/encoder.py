import json
import os
from pathlib import Path
import subprocess

from tools.colors import ConsoleColors
from tools.logger import Logger


class Encoder:
    DEFAULT = {
        'FPS': '60/1',
        'WIDTH': '1920',
        'HEIGHT': '1080',
        'TBN': '1/15360',
        'HZ': '1/44100'
    }

    def __init__(self, error_messages, packager):
        self.__error_messages = error_messages
        self.__packager = packager

        self.__logger = Logger()

    def commander(self, command, args):
        '''
            encode (package name[0]):
                encodes clips to make all clips has the same parameters options
        '''
        if command == 'encode':
            filter = self.__filter(args, 1)
            if filter:
                name = args[0]
                package = self.__packager.get(name)

                if not package:
                    return True

                folder = package.get_data()['clips_folder']
                for subdir, dirs, files in os.walk(folder):
                    for file in files:
                        mp4_file = Path(folder) / file
                        opt = self.__check_video(mp4_file)
                        if opt == '':
                            continue
                        else:
                            self.__logger.log('Re-encoding video {}'.format(mp4_file))
                            cmd = 'ffmpeg -i ' + str(mp4_file) + opt + str(mp4_file).replace('.mp4', '') + 'converted.mp4'
                            r = subprocess.run(cmd, capture_output=True, shell=True)

                            os.remove(mp4_file)
                self.__logger.separator()
            return True
        else:
            return False
    
    def __filter(self, args, ammount):
        if len(args) >= ammount:
            return True
        else:
            print(ConsoleColors.RED + 'Error: {0}'.format(self.__error_messages[0]) + ConsoleColors.RESET)

    def __check_video(self, video):
        cmd = 'ffprobe -v error -of json -show_entries stream=time_base,r_frame_rate,width,height ' + str(video)
        r = os.popen(cmd).read()
        streams = json.loads(r)['streams']

        opt = ''
        if str(streams[0]['width']) != self.DEFAULT['WIDTH']:
            opt = opt + ' -vf scale=' + self.DEFAULT['WIDTH'] + ':' + self.DEFAULT['HEIGHT']
            opt = opt + ' -video_track_timescale ' + self.DEFAULT['TBN'][2:]
            opt = opt + ' -r ' + self.DEFAULT['FPS'][:-2]
        else:
            if streams[0]['time_base'] != self.DEFAULT['TBN']:
                opt = opt + ' -video_track_timescale ' + self.DEFAULT['TBN'][2:]
            if streams[0]['r_frame_rate'] != self.DEFAULT['FPS']:
                opt = opt + ' -r ' + self.DEFAULT['FPS'][:-2]

        if streams[1]['time_base'] != self.DEFAULT['HZ']:
            opt = opt + ' -ar ' + self.DEFAULT['HZ'][2:]

        if opt != '':
            opt = opt + ' '

        return opt
