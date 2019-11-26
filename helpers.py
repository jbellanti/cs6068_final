"""helpers.py
Generic utilities/ functions for use 
    in conjunction with cs6068 final project
"""
import os

VERBOSE = False

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
DEFUALT_AUDIO_FILE_NAME = 'Audio.wav'
DEFUALT_AUDIO_FILE_DIR  = 'resources'
DEFAULT_AUDIO_FILE_PATH = os.path.join(THIS_DIR,
                            DEFUALT_AUDIO_FILE_DIR, 
                            DEFUALT_AUDIO_FILE_NAME)
DEFAULT_KEYWORDS = ['test', 'exam', 'important'] # , 'yep']


def vprint(*args):
    """
    custom print, only actually prints if VERBOSE is set globally
    """
    global VERBOSE
    if VERBOSE:
        print(*args)


# def fprint(*args, file_path='./test.log', file_mode='w+')
#     """
#     print to file
#     """
#     with f as open(file_path, file_mode):
#         f.write(*args)
