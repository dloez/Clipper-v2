import os
from datetime import datetime
import random
import json
from pathlib import Path
import subprocess


class Editor:
    def __init__(self, error_messages, packager, p_videos_media):
        self.__error_messages = error_messages
        self.__packager = packager
        self.__p_videos_media = p_videos_media

    def commander(self, command, args):
        if command == "edit":
            if len(args) < 1:
                self.return_error(0)
            else:
                package_name = args[0]
                package = self.packager.get_package(package_name)

                if not package:
                    return True

                p_clips = package["clips_folder"]
                p_output = package["output_folder"]
                concat_output = Path(p_output) / "concat.txt"

                if not os.path.exists(p_output):
                    os.makedirs(p_output)

                if os.path.exists(concat_output):
                    os.remove(concat_output)

                intro = False
                for subdirs, dirs, files in os.walk(p_clips):
                    for file in files:
                        if not intro:
                            intro = self.check_intro(file, p_clips)

                            if intro:
                                intro_file = str(Path(p_clips) / "intro.mp4")
                                os.remove(Path(p_clips) / file)
                        else:
                            break

                f = open(concat_output, "x")
                for subdir, dirs, files in os.walk(p_clips):
                    for file in files:
                        if file != "intro.mp4":
                            mp4_file = Path(p_clips) / file
                            f.write("file " + str(mp4_file) + "\n")
                f.close()

                self.shuffle(concat_output)
                self.append_io(concat_output, intro_file)

                date = datetime.now()
                output_file = Path(p_output) / package_name
                output_file = str(output_file) + date.strftime("%Y-%m-%d") + ".mp4"
                self.generate_video(package, concat_output, output_file)
            return True
        else:
            return False

    def generate_video(self, p, of, ov):
        cmd = "ffmpeg -f concat -safe 0 -i " + str(of) + " -c copy " + str(ov)
        r = subprocess.run(cmd, shell=True, capture_output=True)

        p["output_file"] = str(ov)
        self.packager.write_packages(p["name"])
        self.logger.log("Video {0} created".format(str(ov)))
        self.logger.separator()

    def append_io(self, file, intro):
        lines = open(file).readlines()
        lines.insert(0, "file " + intro + "\n")
        lines.append("file " + str(Path(self.p_youtube) / Path("video/outro.mp4")) + " \n")
        open(file, 'w').writelines(lines)

    def shuffle(self, file):
        lines = open(file).readlines()
        random.shuffle(lines)

    def check_intro(self, video, folder):
        cmd = "ffprobe -i " + str(Path(folder) / Path(video)) + " -show_entries format=duration -v quiet -of json"
        r = os.popen(cmd).read()
        self.logger.log(r)
        self.logger.separator()

        seconds = int(json.loads(r)["format"]["duration"].split(".")[0])
        if seconds > 7:
            cmd = 'ffmpeg -i ' + str(Path(folder) / Path(video)) + ' -i ' + str(Path(self.p_youtube) / 'video/intro.mov') + ' -filter_complex "[1:v]setpts=PTS-0/TB[a]; [0:v][a]overlay=enable=gte(t\,0):eof_action=pass[out]; [0][1]amix[a]" -map [out] -map [a] -c:v libx264 -crf 18 -pix_fmt yuv420p ' + str(Path(folder) / 'intro.mp4')
            r = subprocess.run(cmd, shell=True, capture_output=True)
            self.logger.log("Intro created, deleting " + str(Path(folder) / Path(video)))
            self.logger.separator()

            return True
        else:
            return False

    def return_error(self, code):
        print(self.error_codes[code])
