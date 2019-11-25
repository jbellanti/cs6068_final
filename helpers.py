"""helpers.py
Generic utilities/ functions for use 
    in conjunction with cs6068 final project
"""

VERBOSE = False


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
