"""textsearcher.py
functions, utilities, and tests for text search code
"""
import concurrent.futures as concf
import helpers as _h
import os
import time

vprint = _h.vprint


# TODO: update to object, dict, or named tuples for more clarity/readability...
#       or at least provide helper functions / constants
#
# NOTE: hits format:
#
#   results: size = number of chunks for text_input provided given chunk_size
#       0...n = chunk-hits
#
#   chunk-hits: size = 3 
#       0 = list of single-hits in chunk
#       1 = words in chunk
#       2 = base word index for this chunk
#
#   single-hit: size = 2
#       0 = word
#       1 = word index in chunk
#


def _extract_global_results(chunk_hit_data):
    """given list of chunks with list hits, provide the meaningful information
    (global word indexing for each hit rather than in-chunk)
    """
    simple_out = []
    for chunk in chunk_hit_data:
        for hit in chunk[0]:
            simple_out.append([hit[0], hit[1] + chunk[2]])
    return simple_out


def _seq_text_search(text_input, keywords):
    """Execute sequential search for keywords in text_input.

    NOTE: can't pass base word index without superfluous preprocessing,
        just notate number of words checked and do post-processing outside
    """
    hits = []
    for word_info in text_input:
        vprint('checking word:', word_info)
        # vprint('checking word:', word_info['word'])
        if word_info['word'] in keywords:
            hits.append(word_info)
    return hits


def do_text_search(text_input, keywords, search_method, chunk_size=10000, overlap=20):
    """Execute text search.

    TODO: use this in main.py (potentially abstract into class maybe?)
    TODO: parallel (gpu) implementation
    """
    chunk_hits = []
    vprint('keywords:', keywords)
    vprint('search_method:', search_method)
    vprint('text_input size:', len(text_input))
    vprint('chunk_size:', chunk_size)
    vprint('overlap:', overlap)
    runtime_start = time.time()

    # single thread/process search
    if search_method == _h.SEQUENTIAL_FLAG:
        chunk_hits = _seq_text_search(text_input, keywords)
    # parallel search via ThreadPoolExecutor
    elif search_method == _h.PARALLEL_FLAG:
        print('DISCLAIMER: for text-search, we are not handling partial words/overlap...')
        print('DISCLAIMER: so the results will be approximate')
        futs = []
        with concf.ThreadPoolExecutor() as executor:
            for i in range(0, len(text_input), chunk_size):
                if i == 0:
                    chunk = text_input[i:i+chunk_size] 
                else:
                    chunk = text_input[i-overlap:i+chunk_size]
                futs.append(executor.submit(_seq_text_search, chunk, keywords))
            for fut in futs:
                res = list(fut.result())
                for r in res:
                    chunk_hits.append(r)
    # parallel search via GPU technology (CUDA)   
    elif search_method == _h.GPU_FLAG:
        print('DISCLAIMER: we are currently not handling partial words/overlap in global indexing...')
        print('DISCLAIMER: so the results will be approximate')
        # TODO: implement parallel text search with cuda bindings
        print('(GPU) Parallel implementation of text search not yet implemented.')
        print('\tUse the -s option to try the sequention version.')
        return ''
    else:
        print('UNKNOWN SEARCH METHOD (', search_method, ')!')
        print('use the -h option for more usage information.')
        return ''

    print('Search runtime:', (time.time() - runtime_start)*1000, 'ms')

    #return _extract_global_results(chunk_hits)
    return chunk_hits


if __name__ == '__main__':
    # if this file is run directly, execute some arbitrary tests
    _h.VERBOSE = True

    CHUNK_SIZE = 5000
    OVERLAP = 20

    arbitrary_text_1 = '''
    This is just some arbitrary block of text.
    It's relatively small, for a larger test consider finding and using 
        a large text file from somewhere on the internet.
    Metrics may not be very conclusive as it is small.
    Some arbitrary hits: assignment, exam, test, project, important, critical, useful.
    Continued rambling text for the purpose of filler only...
    Done, finished, over, complete, run a test with this now.
    '''

    time.sleep(0.5) # arbitrary sleep
    arbitrary_keywords_1 = [word.strip() for word in 'test, assignment, exam'.split(',')]

    print('==================================================')
    print('Starting sequential search test with small-scale text input')
    print('==================================================')
    print(do_text_search(   arbitrary_text_1, arbitrary_keywords_1, _h.SEQUENTIAL_FLAG, 
                            chunk_size=CHUNK_SIZE, overlap=OVERLAP))
    print('')

    print('==================================================')
    print('Starting parallel (non-gpu) search test with small-scale text input')
    print('==================================================')
    print(do_text_search(   arbitrary_text_1, arbitrary_keywords_1, _h.PARALLEL_FLAG, 
                            chunk_size=CHUNK_SIZE, overlap=OVERLAP))
    print('')
    
    # TODO: implement parallel text search with cuda bindings
    vprint('==================================================')
    vprint('Starting parallel (gpu) search test with small-scale text input')
    vprint('==================================================')
    print(do_text_search(   arbitrary_text_1, arbitrary_keywords_1, _h.GPU_FLAG,
                            chunk_size=CHUNK_SIZE, overlap=OVERLAP))
    vprint('')

    sample_lecture_text = ''
    with open(os.path.join( _h.THIS_DIR, 
                            _h.DEFAULT_AUDIO_FILE_DIR, 
                            'LectureFull.txt')) as f:
                            #'big.txt')) as f:
        sample_lecture_text = f.read()
    
    time.sleep(0.5) # arbitrary sleep
    print('==================================================')
    print('Starting sequential search test with large-scale text input')
    print('==================================================')
    print(do_text_search(   sample_lecture_text, arbitrary_keywords_1, _h.SEQUENTIAL_FLAG, 
                            chunk_size=CHUNK_SIZE, overlap=OVERLAP))
    print('')

    print('==================================================')
    print('Starting parallel (non-gpu) search test with large-scale text input')
    print('==================================================')
    print(do_text_search(   sample_lecture_text, arbitrary_keywords_1, _h.PARALLEL_FLAG,
                            chunk_size=CHUNK_SIZE, overlap=OVERLAP))
    print('')
    
    vprint('==================================================')
    vprint('Starting parallel (gpu) search test with large-scale text input')
    vprint('==================================================')
    print(do_text_search(   sample_lecture_text, arbitrary_keywords_1, _h.GPU_FLAG,
                            chunk_size=CHUNK_SIZE, overlap=OVERLAP))
    vprint('')

    # novel to test on: https://norvig.com/big.txt
    # for a bigger test curl that file and uncomment the following
    #   i.e. curl -o resources/big.txt https://norvig.com/big.txt
    # novel_text = ''
    # with open(os.path.join( _h.THIS_DIR, 
    #                         _h.DEFAULT_AUDIO_FILE_DIR, 
    #                         'big.txt')) as f:
    #     novel_text = f.read()
    # print('Note: turning off verbose output for massive text input...')
    # _h.VERBOSE = False
    
    # time.sleep(0.5) # arbitrary sleep
    # print('==================================================')
    # print('Starting sequential search test with massive text input')
    # print('==================================================')
    # print(do_text_search( novel_text, arbitrary_keywords_1, _h.SEQUENTIAL_FLAG, 
    #                       chunk_size=CHUNK_SIZE, overlap=OVERLAP))
    # print('')

    # print('==================================================')
    # print('Starting parallel (non-gpu) search test with massive text input')
    # print('==================================================')
    # print(do_text_search( novel_text, arbitrary_keywords_1, _h.PARALLEL_FLAG, 
    #                       chunk_size=CHUNK_SIZE, overlap=OVERLAP))
    # print('')
    
    # vprint('==================================================')
    # vprint('Starting parallel (gpu) search test with massive text input')
    # vprint('==================================================')
    # print(do_text_search(novel_text, arbitrary_keywords_1, _h.GPU_FLAG))
    # vprint('')
