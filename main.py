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
DEFUALT_AUDIO_FILE_NAME = 'Audio.wav'
DEFUALT_AUDIO_FILE_DIR  = 'resources'
DEFAULT_AUDIO_FILE_PATH = os.path.join(
                            os.path.dirname(__file__),
                            DEFUALT_AUDIO_FILE_DIR, 
                            DEFUALT_AUDIO_FILE_NAME)
DEFAULT_KEYWORDS = ['test', 'yep']
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


def do_speech_to_text(file_path, seq=False):
    """Execute speech to text via google cloud's api.
    Heavily derived from google cloud's tutorial:
        https://cloud.google.com/speech-to-text/docs/reference/libraries

    TODO: associate / maintain timestamps
    TODO: parallel implementation
    """
    text_result = ''
    if not seq:
        print('Parallel implementation of speech to text not yet implemented.')
        print('\tUse the -s option to try the sequention version.')
        return text_result

    # Instantiates a client
    client = speech.SpeechClient()
    runtime_start = time.time()

    # Loads the audio into memory
    with io.open(file_path, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

        config = types.RecognitionConfig(
                    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code='en-US')

        vprint('Attempting speech to text conversion...')

        # Detects speech in the audio file
        response = client.recognize(config, audio)

        for result in response.results:
            text_result += result.alternatives[0].transcript
            vprint('Transcript:', result.alternatives[0].transcript)
    
    vprint('Speech to text runtime:', (time.time() - runtime_start)*1000, 'ms')

    return text_result


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
        help='What file to execute the search feature on.')

    _a('--verbose', '-v', action='store_true',
        help='Print out more information during execution.')

    _a('--keywords', '-k', default=DEFAULT_KEYWORDS,
        help='What keywords to search for.')
    args = arg_parser.parse_args()

    global VERBOSE
    VERBOSE = args.verbose

    if not os.path.exists(args.input_file): 
        print('ERROR: input file {} not found!' % args.input_file)
        sys.exit(1)
    
    txt = do_speech_to_text(args.input_file, seq=args.sequential)
    search_results = do_text_search(txt, args.keywords, seq=args.sequential)
    print('search results:\n', search_results)

    
if __name__ == '__main__':
    main()
    