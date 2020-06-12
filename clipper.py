from pathlib import Path
import json
import os

from modules.packager import Packager
from modules.downloader import Downloader
from modules.encoder import Encoder
from modules.editor import Editor
from modules.uploader import Uploader


def welcome():
    with open(P_CONFIG_DATA, 'r') as f:
        data = json.load(f)

    name = data['name']
    version = data['version']

    print('Welcome to {}\nVersion: {}'.format(name, version), end='\n\n')

def user_input(command, args):
    for module in modules:
        exists = module.commander(command, args)

        if exists:
            if type(exists) != bool:
                print(exists)
            break

    if not exists or not command:
        print('Command not registered')

def check_paths():
    for path in dirs_paths:
        if not os.path.exists(path):
            os.mkdir(path)

ERROR_MESSAGES = {
    0: 'Missing arguments'
}

# files
P_CONFIG_DATA = Path('config/data.json').absolute()
P_TOKENS_FILE = Path('tokens/tokens.json').absolute()

#paths
P_TOKENS = Path('tokens').absolute()

# paths that needs to be checked
P_PACKAGES = Path('packages').absolute()
P_CLIPS = Path('clips').absolute()
P_OUTPUTS = Path('outputs').absolute()
P_VIDEOS_MEDIA = Path('videos').absolute()
dirs_paths = list([P_PACKAGES, P_CLIPS, P_OUTPUTS, P_VIDEOS_MEDIA])

modules = list()
modules.append(Packager(ERROR_MESSAGES, P_PACKAGES, P_CLIPS, P_OUTPUTS, P_VIDEOS_MEDIA))
modules.append(Downloader(ERROR_MESSAGES, modules[0], P_TOKENS_FILE))
modules.append(Encoder(ERROR_MESSAGES, modules[0]))
modules.append(Editor(ERROR_MESSAGES, modules[0], P_VIDEOS_MEDIA))
modules.append(Uploader(ERROR_MESSAGES, modules[0], P_TOKENS, P_VIDEOS_MEDIA))

check_paths()
welcome()
while True:
    user_inp = input('>> ')

    if user_inp:
        inp = user_inp.split(' ')

        command = inp[0]
        args = inp[1:]

        user_input(command, args)
