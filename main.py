import argparse
import io
import os
import sys
import time

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

# Imports for parallelization
import concurrent.futures
import audiosplitter
import merge

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
#CRED_FILE = 'C:\\Users\\Kevin\\admin-speech2text-cs6068.json'
CRED_FILE = 'Parallel Final Project-f40a7d7b14ab.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CRED_FILE

def vprint(*args):
    """
    custom print, only actually prints if VERBOSE is set globally
    """
    global VERBOSE
    if VERBOSE:
        print(*args)

def thread_function(filename, id):
    try:
        result_list.append(run_speech_to_text_client(filename, id = id))
    except Exception as e:
        print('THREAD', id, 'ERROR:', e.args[0])

def run_speech_to_text_client(file_path, id = None):
    text_result = ''
    time_offset = []
     # Instantiates a client
    client = speech.SpeechClient()
    runtime_start = time.time()

    # Loads the audio into memory
    with io.open(file_path, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

        config = types.RecognitionConfig(
                    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                    #sample_rate_hertz=16000,
                    enable_word_time_offsets=True,
                    language_code='en-US')

        # Detects speech in the audio file
        response = client.recognize(config, audio)

        for result in response.results:
            text_result += result.alternatives[0].transcript
            time_offset += result.alternatives[0].words
            vprint('Transcript:', result.alternatives[0].transcript)

    vprint('Speech to text runtime:', (time.time() - runtime_start)*1000, 'ms')

    return id, text_result, time_offset

result_list = []

def do_speech_to_text(file_path, seq=False):
    """Execute speech to text via google cloud's api.
    Heavily derived from google cloud's tutorial:
        https://cloud.google.com/speech-to-text/docs/reference/libraries

    TODO: associate / maintain timestamps
    TODO: parallel implementation
    """
    text_result = ''
    time_offset = []
    if seq:
        text_result, time_offset = run_speech_to_text_client(file_path)
    else:
        print('Parallel implementation of speech to text not yet implemented.')
        print('\tUse the -s option to try the sequention version.')
        #return text_result, time_offset

        # split the audio files
        segment_length = 50000
        overlap_length = 1000
        start_time = 0
        end_time = -1
        split_filenames = audiosplitter.split_audio_file(file_path, segment_length, overlap_length, start_time, end_time)
    
        # spin up a thread for each split of the file
        #for split_filename in split_filenames:
        with concurrent.futures.ThreadPoolExecutor() as executer:
            executer.map(thread_function, split_filenames, range(len(split_filenames)))

        print("done executing")
        
        # sort the list so that it is in order
        result_list.sort(key=lambda id:id[0])

        # combine the text results
        text_result = merge.merge_strings([s[1] for s in result_list])
    
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
    
    txt, time_offset = do_speech_to_text(args.input_file, seq=args.sequential)
    #search_results = do_text_search(txt, args.keywords, seq=args.sequential)

    #print('search results:')
    #for result in search_results:
    #    print(
    #        u"Index: {}, Word: {}, Start time: {} seconds {} nanos".format(
    #            result[1], result[0],
    #            time_offset[result[1]].start_time.seconds,
    #            time_offset[result[1]].start_time.nanos
    #        )
    #    )

    
if __name__ == '__main__':
    main()
    