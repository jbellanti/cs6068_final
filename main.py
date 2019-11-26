import argparse
import io
import os
import sys
import time

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types


# various globals (pathing etc.)
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
DEFUALT_AUDIO_FILE_NAME = 'Audio.wav'
DEFUALT_AUDIO_FILE_DIR  = 'resources'
DEFAULT_AUDIO_FILE_PATH = os.path.join(THIS_DIR,
                            DEFUALT_AUDIO_FILE_DIR, 
                            DEFUALT_AUDIO_FILE_NAME)
DEFAULT_KEYWORDS = ['test', 'exam', 'important'] # , 'yep']
VERBOSE = False

# uncomment/modify for your path otherwise set the environment var beforehand
# CRED_FILE = 'C:\\Users\\Kevin\\admin-speech2text-cs6068.json'
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CRED_FILE

def vprint(*args):
    """
    custom print, only actually prints if VERBOSE is set globally
    """
    global VERBOSE
    if VERBOSE:
        print(*args)


def do_speech_to_text(file_path, seq=False, save_text=False):
    """Execute speech to text via google cloud's api.
    Heavily derived from google cloud's tutorial:
        https://cloud.google.com/speech-to-text/docs/reference/libraries

    TODO: associate / maintain timestamps
    TODO: parallel implementation
    """
    text_result = ''
    time_offset = []
    if not seq:
        print('Parallel implementation of speech to text not yet implemented.')
        print('\tUse the -s option to try the sequention version.')
        return text_result

    # Instantiates a client
    client = speech.SpeechClient()
    runtime_start = time.time()

    # NOTE: seems to only handle mono, to convert stereo to mono do this:
    #   need to install ffmpeg for your system manually and put it on
    #       your PATH var: https://ffmpeg.zeranoe.com/builds/
    #
    # ffmpeg -y -i LectureShort.mp3 -ac 1 -acodec pcm_s16le -ar 16000 LectureShort.wav

    # NOTE: for long running (>1m), need to create a bucket and give uri
    #   https://cloud.google.com/storage/docs/creating-buckets
    # NOTE 2: this should not be an issue for our parallel implementation
    #   i imagine we'd want to splice it into 1m or less chunks anyways

    # TODO: make long running w/ bucket an option but not required here...

    #LINEAR16 # for wav #ENCODING_UNSPECIFIED # for mp3
    # NOTE: to convert to wav
    # ffmpeg -i <inputfile (mp3 or other)> <outputfile.wav>
    
    if os.path.exists(file_path): 
        # Loads the audio into memory
        with io.open(file_path, 'rb') as audio_file:
            content = audio_file.read()
        audio = types.RecognitionAudio(content=content)
    else:
        # uses bucket for long running op
        storage_uri = file_path # 'gs://cs6068-farleykm-bucket/LectureShort.wav'
        audio = types.RecognitionAudio(uri=storage_uri)
             
    config = types.RecognitionConfig(
                encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                enable_word_time_offsets=True,
                language_code='en-US')

    vprint('Attempting speech to text conversion...')

    # Detects speech in the audio file    
    vprint("Waiting for operation to complete...")
    if os.path.exists(file_path):
        response = client.recognize(config, audio) # short audio only <1m
    else:
        operation = client.long_running_recognize(config, audio)
        response = operation.result()

    for result in response.results:
        text_result += result.alternatives[0].transcript
        time_offset += result.alternatives[0].words
        vprint('Transcript:', result.alternatives[0].transcript)

    vprint('Speech to text runtime:', (time.time() - runtime_start)*1000, 'ms')

    if save_text:
        # extract file base name, make txt file and determine dump location
        if os.path.exists(file_path):
            new_fname = os.path.basename(file_path)
        else:
            new_fname = file_path.split('/')[-1]
        vprint('Trying to save text to', new_fname)
        new_fname = new_fname.split('.')[-2] + '.txt'
        new_fpath = os.path.join(THIS_DIR, DEFUALT_AUDIO_FILE_DIR, new_fname)
        with open(new_fpath, 'w') as f:
            f.write(text_result)

    return text_result, time_offset


def do_text_search(text_input, keywords, seq=False):
    """Execute text search.

    TODO: associate / maintain timestamps
    TODO: parallel implementation
    """
    hits = []

    if not seq:
        print('Parallel implementation of text search not yet implemented.')
        print('\tUse the -s option to try the sequention version.')
        return ''

    runtime_start = time.time()
    vprint('keywords:', keywords)
    vprint('text_input:', text_input)

    for idx, word in enumerate(text_input.split(' ')):
        # vprint('checking word:', word)
        if word in keywords:
            vprint('Hit at word index', idx)
            hits.append([word, idx])
    vprint('Search runtime:', (time.time() - runtime_start)*1000, 'ms')

    return hits


def main():
    """Main function for cs6068 final project.
    Note: only if we end up using python... remove comment if necessary later
    Usage: 
        python3 main.py
    
    TODO: support audio conversion / splicing (stretch goal)
    TODO: support ML / tensorflow option (stretch goal)
    """
    arg_parser = argparse.ArgumentParser()
    _a = arg_parser.add_argument
    _a('--sequential', '-ss', action='store_true', 
        help='Execute the sequential version of the audio search feature.')

    _a('--input-file', '-i', default=DEFAULT_AUDIO_FILE_PATH,
        help='What file to execute the search feature on. ' +
        'NOTE: this can (and must be) a bucket uri for long running ops (>1m) +'
        'i.e. "gs://cs6068-farleykm-bucket/LectureShort.wav"')

    _a('--verbose', '-v', action='store_true',
        help='Print out more information during execution.')

    _a('--keywords', '-k', default=DEFAULT_KEYWORDS,
        help='What keywords to search for.')

    _a('--save-text', '-s', action='store_true', 
        help='Option to save the transcript as a txt file')
    args = arg_parser.parse_args()

    global VERBOSE
    VERBOSE = args.verbose

    vprint('args used:', args)

    if not os.path.exists(args.input_file): 
        print('WARNING: input file', args.input_file, 'not found!')
        print('\tthe code will assume this is a google bucket uri else expect failure')
    
    txt, time_offset = do_speech_to_text(
        args.input_file, seq=args.sequential, save_text=args.save_text)
    search_results = do_text_search(txt, args.keywords, seq=args.sequential)

    print('search results:')
    for result in search_results:
        print(
            u"Index: {}, Word: {}, Start time: {} seconds {} nanos".format(
                result[1], result[0],
                time_offset[result[1]].start_time.seconds,
                time_offset[result[1]].start_time.nanos
            )
        )

    
if __name__ == '__main__':
    main()
    
