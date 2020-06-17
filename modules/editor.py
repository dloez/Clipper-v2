import os
from datetime import datetime
import random
import json
from pathlib import Path
import subprocess

from tools.colors import ConsoleColors
from tools.logger import Logger

class Editor:
    def __init__(self, error_messages, packager, p_videos_media):
        self.__error_messages = error_messages
        self.__packager = packager
        self.__p_videos_media = p_videos_media

        self.__logger = Logger()

    def commander(self, command, args):
        '''
            edit (package name[0]):
                concatenates all clips + outro, then inserts video intro at the beginning
        '''
        if command == 'edit':
            filter = self.__filter(args, 1)
            if filter:
                name = args[0]
                package = self.__packager.get(name)

                if not package:
                    return True

                p_clips = package.get_data()['clips_folder']
                p_output = package.get_data()['output_folder']
                concat_output = Path(p_output) / 'concat.txt'

                if os.path.exists(concat_output):
                    os.remove(concat_output)

                with open(concat_output, 'x') as f:
                    for subdir, dirs, files in os.walk(p_clips):
                        files.sort()
                        for file in files:
                            mp4_file = Path(p_clips) / file
                            f.write('file ' + str(mp4_file) + '\n')
                    f.write('file ' + str(self.__p_videos_media / 'outro.mp4'))

                date = datetime.now()
                output_video = Path(p_output) / str(name + date.strftime('%Y-%m-%d') + '.mp4')
                self.__generate_video(package, concat_output, output_video)
                self.__logger.log('video {} created'.format(output_video))
                self.__logger.separator()
            return True
        else:
            return False
    
    def __filter(self, args, ammount):
        if len(args) >= ammount:
            return True
        else:
            print(ConsoleColors.RED + 'Error: {0}'.format(self.__error_messages[0]) + ConsoleColors.RESET)

    def __generate_video(self, p, of, ov):
        cmd = 'ffmpeg -f concat -safe 0 -i {} -c copy {}'.format(of, ov)
        r = subprocess.run(cmd, shell=True, capture_output=True)
        
        intro = Path(self.__p_videos_media) / 'intro.mov'
        final_ov = str(ov).replace('mp4', '') + 'final.mp4'
        cmd = 'ffmpeg -i {} -i {} -filter_complex "[1:v]setpts=PTS-0/TB[a]; [0:v][a]overlay=enable=gte(t\,0):eof_action=pass[out]; [0][1]amix[a]" -map [out] -map [a] -c:v libx264 -crf 18 -pix_fmt yuv420p {}'.format(ov, intro, final_ov)
        r = subprocess.run(cmd, shell=True, capture_output=True)

        p.get_data()['additional_info']['output_video'] = str(final_ov)
        p.update()

        '''
        create twitter_video
        '''
        twitter_video = 'test.mp4'
        p.get_data()['additional_info']['twitter_video'] = twitter_video
        p.update()
