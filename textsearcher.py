"""textsearcher.py
functions, utilities, and tests for text search code
"""
import helpers
import time
import concurrent.futures as concf

vprint = helpers.vprint


def seq_text_search(text_input, keywords):
    """Execute sequential search for keywords in text_input.

    TODO: text_input will eventually be words/lines/data paired with timestamps
        handle lists/dictionaries when that data shape is more known/understood
    """
    hits = []
    for idx, word in enumerate(text_input.split(' ')):
        # vprint('checking word:', word)
        if word in keywords:
            vprint('Hit at word index', idx)
            hits.append([word, idx])
    return hits


def do_text_search(text_input, keywords, seq=False, gpu=False):
    """Execute text search.

    TODO: paste this into main.py or abstract this functionality into class
    TODO: associate / maintain timestamps (till then the idx of the hit means very little)
    TODO: parallel implementation
    """
    hits = []
    vprint('keywords:', keywords)
    # vprint('text_input:', text_input)
    runtime_start = time.time()

    # single thread/process search
    if seq:
        hits = seq_text_search(text_input, keywords)
    # parallel search via ThreadPoolExecutor
    elif not seq and not gpu:
        futs = []
        with concf.ThreadPoolExecutor() as executor:
            for line in text_input.split('\n'):
                futs.append(executor.submit(seq_text_search, line, keywords))
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

    # TODO: convert one of our lecture files into text format and execute these
    # vprint('==================================================')
    # vprint('Starting sequential search test with large-scale text input')
    # vprint('==================================================')
    # print(do_text_search(arbitrary_text_1, arbitrary_keywords_1, seq=True, gpu=False))
    # vprint('')

    # vprint('==================================================')
    # vprint('Starting parallel (non-gpu) search test with large-scale text input')
    # vprint('==================================================')
    # print(do_text_search(arbitrary_text_1, arbitrary_keywords_1, seq=False, gpu=False))
    # vprint('')
    
    # vprint('==================================================')
    # vprint('Starting parallel (gpu) search test with large-scale text input')
    # vprint('==================================================')
    # print(do_text_search(arbitrary_text_1, arbitrary_keywords_1, seq=False, gpu=True))
    # vprint('')
