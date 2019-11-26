"""textsearcher.py
functions, utilities, and tests for text search code
"""
import concurrent.futures as concf
import helpers
import os
import time

vprint = helpers.vprint


def seq_text_search(text_input, keywords, base_index=0):
    """Execute sequential search for keywords in text_input.

    TODO: text_input should be words/lines/data paired with timestamps
    """
    hits = []
    for idx, word in enumerate(text_input.split(' ')):
        # vprint('checking word:', word)
        if word in keywords:
            vprint('Hit at word index', idx + base_index)
            hits.append([word, idx + base_index])
    return hits


def do_text_search(text_input, keywords, seq=False, gpu=False, chunk_size=2048, overlap=20):
    """Execute text search.

    TODO: paste this into main.py or abstract this functionality into class
    TODO: associate / maintain timestamps (till then the idx of the hit means very little)
    TODO: parallel (gpu) implementation
    """
    hits = []
    vprint('keywords:', keywords)
    vprint('text_input size:', len(text_input))
    # vprint('text_input:', text_input)
    runtime_start = time.time()

    # single thread/process search
    if seq:
        hits = seq_text_search(text_input, keywords)
    # parallel search via ThreadPoolExecutor
    elif not seq and not gpu:
        vprint('DISCLAIMER: parallel outputs have hybrid character/word indexing for hits')
        futs = []
        with concf.ThreadPoolExecutor() as executor:
            for i in range(0, len(text_input), chunk_size):
                if i == 0:
                    chunk = text_input[i:i+chunk_size] 
                else:
                    chunk = text_input[i-overlap:i+chunk_size]
                futs.append(executor.submit(seq_text_search, chunk, keywords, base_index=i))
            for fut in futs:
                hits += fut.result()
    # parallel search via GPU technology (CUDA)   
    elif not seq and gpu:
        # TODO: implement parallel text search with cuda bindings
        print('(GPU) Parallel implementation of text search not yet implemented.')
        print('\tUse the -s option to try the sequention version.')
        return ''

    vprint('Search runtime:', (time.time() - runtime_start)*1000, 'ms')

    return hits


if __name__ == '__main__':
    # if this file is run directly, execute some arbitrary tests
    helpers.VERBOSE = True

    arbitrary_text_1 = '''
    This is just some arbitrary block of text.
    It's relatively small, for a larger test consider finding and using 
        a large text file from somewhere on the internet.
    Metrics may not be very conclusive as it is small.
    Some arbitrary hits: assignment, exam, test, project, important, critical, useful.
    Continued rambling text for the purpose of filler only...
    Done, finished, over, complete, run a test with this now.
    '''

    time.sleep(0.5)
    arbitrary_keywords_1 = [word.strip() for word in 'test, assignment, exam, important'.split(',')]

    vprint('==================================================')
    vprint('Starting sequential search test with small-scale text input')
    vprint('==================================================')
    print(do_text_search(arbitrary_text_1, arbitrary_keywords_1, seq=True, gpu=False))
    vprint('')

    vprint('==================================================')
    vprint('Starting parallel (non-gpu) search test with small-scale text input')
    vprint('==================================================')
    print(do_text_search(arbitrary_text_1, arbitrary_keywords_1, seq=False, gpu=False))
    vprint('')
    
    # TODO: implement parallel text search with cuda bindings
    # vprint('==================================================')
    # vprint('Starting parallel (gpu) search test with small-scale text input')
    # vprint('==================================================')
    # print(do_text_search(arbitrary_text_1, arbitrary_keywords_1, seq=False, gpu=True))
    # vprint('')

    sample_lecture_text = ''
    with open(os.path.join( helpers.THIS_DIR, 
                            helpers.DEFAULT_AUDIO_FILE_DIR, 
                            'LectureFull.txt')) as f:
        sample_lecture_text = f.read()
    
    time.sleep(0.5)
    vprint('==================================================')
    vprint('Starting sequential search test with large-scale text input')
    vprint('==================================================')
    print(do_text_search(sample_lecture_text, arbitrary_keywords_1, seq=True, gpu=False))
    vprint('')

    vprint('==================================================')
    vprint('Starting parallel (non-gpu) search test with large-scale text input')
    vprint('==================================================')
    print(do_text_search(sample_lecture_text, arbitrary_keywords_1, seq=False, gpu=False))
    vprint('')
    
    # vprint('==================================================')
    # vprint('Starting parallel (gpu) search test with large-scale text input')
    # vprint('==================================================')
    # print(do_text_search(arbitrary_text_1, arbitrary_keywords_1, seq=False, gpu=True))
    # vprint('')
