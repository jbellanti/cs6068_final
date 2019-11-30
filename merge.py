from multiprocessing import Pool

PROCESSING_POOL_SIZE = 10

test_strings = ['one two three four',
                'three four five six seven eight nine',
                'nine ten eleven this is a test of merging',
                'merging a bunch of sentences together']


def merge_strings(strings):

    # Convert list of strings into list of word lists
    word_lists = list(map(lambda string: string.split(' '), strings))

    overlaps = get_overlaps(word_lists)

    # Put the lists together by taking the whole first list and the part of every other list that does not overlap
    # with the previous list
    merged_words = word_lists[0]
    for i, overlap in enumerate(overlaps):
        merged_words.extend(word_lists[i+1][overlap:])

    print(' '.join(merged_words))


def get_overlaps(word_lists):
    """
    Takes a list of word lists and returns a list with the overlaps between each one

    Example input:
    [['one', 'two', 'three'],
    'three', 'four', 'five', 'six'],
    ['five', 'six', 'seven', 'eight', 'nine'],
    ['nine']]

    Returns:
    [1, 2, 1]

    """

    # Create tuples of word lists to be matched; we have to do this because multiprocessing.Pool.map can only take a
    # single iterable
    words_pairs = zip(word_lists[:-1], word_lists[1:])

    pool = Pool(PROCESSING_POOL_SIZE)
    overlaps = list(pool.map(_get_overlap, words_pairs))

    return overlaps


def _get_overlap(words):

    max_overlap = min(len(words[0]), len(words[1]))
    best_overlap = 0

    for i in range(1, max_overlap):
        if words[0][-i:] == words[1][:i]:
            best_overlap = i

    return best_overlap


if __name__ == "__main__":
    merge_strings(test_strings)
