import argparse
import io
import os
import sys
import time
import math

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

# local imports
from textsearcher import do_text_search

# Imports for parallelization
import concurrent.futures
import audiosplitter
import merge

# Import for temporary file directory
import tempfile

# various globals are in helpers.py, access via _h.<global>
import helpers as _h
vprint = _h.vprint

RESULT_LIST = []

# uncomment/modify for your path otherwise set the environment var beforehand
#CRED_FILE = 'C:\\Users\\Kevin\\admin-speech2text-cs6068.json'
#CRED_FILE = 'Parallel Final Project-f40a7d7b14ab.json'
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CRED_FILE


def thread_function(filename, id):
    try:
        text_result = ''
        time_offset = []

        # Get start time in milliseconds from the filename
        start = filename.rindex("cs6068_final_") + len("cs6068_final_")
        end = filename[start:].index("_")
        end += start
        ms = int(filename[start:end])
        sec = math.floor(ms / 1000)

        # print('filename:', filename)
        # print('yields:', sec, 's or', ms, 'ms')

        text_result, time_offset = run_speech_to_text_client(filename)
        for i in range(len(time_offset)):
            entry = {'word': time_offset[i].word,
                     'seconds': sec + time_offset[i].start_time.seconds,
                     'nanos': time_offset[i].start_time.nanos}
            # print(entry)
            RESULT_LIST.append(entry)

    except Exception as e:
        print('THREAD', id, 'ERROR:', e.args[0])


def run_speech_to_text_client(file_path):
    text_result = ''
    time_offset = []
     # Instantiates a client
    client = speech.SpeechClient()

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

    return text_result, time_offset


def do_speech_to_text(file_path, conversion_method, save_text=False, split_size=30000, split_overlap=1000):
    """Execute speech to text via google cloud's api.
    Heavily derived from google cloud's tutorial:
        https://cloud.google.com/speech-to-text/docs/reference/libraries

    TODO: associate / maintain timestamps
    TODO: parallel implementation
    """
    text_result = ''
    time_offset = []
    runtime_start = time.time()
    if conversion_method == _h.SEQUENTIAL_FLAG:
        text_result, time_offset = run_speech_to_text_client(file_path)
        for i in range(len(time_offset)):
            entry = {'word': time_offset[i].word,
                     'seconds': time_offset[i].start_time.seconds,
                     'nanos': time_offset[i].start_time.nanos}
            RESULT_LIST.append(entry)

        print('Speech to text runtime:', (time.time() - runtime_start)*1000, 'ms')
    elif conversion_method == _h.PARALLEL_FLAG:
        # create temp directory
        tempdir = tempfile.TemporaryDirectory()

        # split the audio files
        start_time = 0
        end_time = -1
        split_filenames = audiosplitter.split_audio_file(file_path, int(split_size), int(split_overlap), start_time, end_time, temp_dir=(tempdir.name + '/'))
    
        # spin up a thread for each split of the file
        #for split_filename in split_filenames:
        n_workers = len(split_filenames)
        with concurrent.futures.ThreadPoolExecutor(max_workers=n_workers) as executer:
            executer.map(thread_function, split_filenames, range(len(split_filenames)))

        print("done executing {} workers".format(n_workers))
        print('Speech to text runtime:', (time.time() - runtime_start)*1000, 'ms')
        
        # sort the list so that it is in order
        RESULT_LIST.sort(key=lambda x:x['seconds'])
    else:
        print('UNKNOWN CONVERSION METHOD (', conversion_method, ')!')
        print('use the -h option for more usage information.')
        return

    text_result = RESULT_LIST
    
    if save_text:
        # extract file base name, make txt file and determine dump location
        if os.path.exists(file_path):
            new_fname = os.path.basename(file_path)
        else:
            new_fname = file_path.split('/')[-1]
        vprint('Trying to save text to', new_fname)
        new_fname = new_fname.split('.')[-2] + '.txt'
        new_fpath = os.path.join(_h.THIS_DIR, _h.DEFAULT_AUDIO_FILE_DIR, new_fname)
        with open(new_fpath, 'w') as f:
            # f.write(' '.join(list(map(lambda x:x['word'], text_result))))
            f.write(
                '\n'.join(list(map(lambda x: 
                    u"Start: {} hours {} minutes {} seconds {} nanos ({})\tWord: {}"
                        .format( 
                            x['seconds'] // 60 // 60, 
                            x['seconds'] // 60, 
                            x['seconds'] % 60, 
                            x['nanos'], 
                            x['seconds'],
                            x['word']), 
                    text_result)
                ))
            )

    return text_result, time_offset


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
    _a('--search-method', '-s', choices=[_h.SEQUENTIAL_FLAG, _h.PARALLEL_FLAG, _h.GPU_FLAG],
        default=_h.SEQUENTIAL_FLAG,
        help='Execute the sequential version of the audio search feature.')
    
    _a('--conversion-method', '-c', choices=[_h.SEQUENTIAL_FLAG, _h.PARALLEL_FLAG],
        default=_h.SEQUENTIAL_FLAG,
        help='Execute the sequential version of the text to speech feature.')

    _a('--input-file', '-i', default=_h.DEFAULT_AUDIO_FILE_PATH,
        help='What file to execute the search feature on. '
        'NOTE: this can (and must be) a bucket uri for long running ops (>1m)'
        'i.e. "gs://cs6068-farleykm-bucket/LectureShort.wav"')

    _a('--verbose', '-v', action='store_true',
        help='Print out more information during execution.')

    _a('--keywords', '-k', default=_h.DEFAULT_KEYWORDS,
        help='What keywords to search for (space delimited in quotes).')

    _a('--split-size', '-z', default=_h.DEFAULT_SPLIT_SIZE,
        help='Length of the chunks that the audio will be split into to parallelize (in ms)')

    _a('--split-overlap', '-o', default=_h.DEFAULT_SPLIT_OVERLAP,
        help='Amount that each chunk of audio will overlap the adjacent chunks (in ms)')

    _a('--save-text', '-t', action='store_true', 
        help='Option to save the transcript as a txt file')
    args = arg_parser.parse_args()

    _h.VERBOSE = args.verbose

    vprint('args used:', args)

    if not os.path.exists(args.input_file): 
        print('WARNING: input file', args.input_file, 'not found!')
        print('\tthe code will assume this is a google bucket uri')
    
    txt, time_offset = do_speech_to_text(
        args.input_file, args.conversion_method.lower(), save_text=args.save_text, split_size=args.split_size, split_overlap=args.split_overlap)
    search_results = do_text_search(txt, args.keywords.lower().split(' '), args.search_method.lower(), 
                                    chunk_size=10000, overlap=20) # not parametrized as we do not care to run parallel search (little gains...)

    print('search results:')
    for result in search_results:
        hr = math.floor(result['seconds'] / 60 / 60)
        min = math.floor((result['seconds'] / 60) % 60)
        sec = result['seconds'] % 60
        print(
            u"Word: {}, Start time: {} hours {} minutes {} seconds {} nanos".format(
                result['word'], hr, min, sec, result['nanos']
            )
        )

    
if __name__ == '__main__':
    main()
    
