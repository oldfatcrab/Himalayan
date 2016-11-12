import pip
from sys import exit

packages = ['ffmpy']

for package in packages:
    try:
        __import__(package)
    except ImportError:
        print('Package "' + package + '" not found, installing...')
        pip.main(['install', '--user', package])

import ffmpy
ff = ffmpy.FFmpeg(global_options = '-loglevel quiet')

try:
    ff.run()
except ffmpy.FFExecutableNotFoundError:
    sys.exit('ffmpeg not installed, please install it')
except ffmpy.FFRuntimeError:
    pass
