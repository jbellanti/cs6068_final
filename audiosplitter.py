"""
split a wav file up into several smaller wav files, with overlap

Usage
    python3 audiosplitter.py file_name segment_ms overlap_ms [start_ms] [end_ms]

    file_name is the name of the wav file that will be split up
    segment_ms is the length of each of the split files in milliseconds
    overlap_ms is the number of milliseconds of overlap between each pair of adjacent segments
    start_ms is the time in the original audio file in milliseconds at which the splitting will start.
        If no time is specified, 0 will be assumed
    end_ms is the time in the original audio file in milliseconds at which the splitting will stop.
        If no time is specified, the end of the audio clip will be assumed

Output
    The output will be a number of wav files. Each wav file will be the original filename with _start_end.wav
        appended to it, where start is the number of ms at which the segment starts
        and end is the number of ms at which the segment ends (as compared to the original file).
"""

from pydub import AudioSegment
import sys

def split_audio_file(filename, segment_length, overlap_length, start_time, end_time, temp_dir=''):

    # load the audio file
    format_split = filename.rfind('.')
    fileprefix = filename[0:format_split]
    filesuffix = filename[format_split+1:]
    sound = AudioSegment.from_file(filename, format=filesuffix)
    segment_start_delta = segment_length - overlap_length

    # calculate the end time if none was specified
    if end_time == -1:
        end_time = len(sound)
        print('start:',start_time)
        print('end:  ',end_time)

    # return a list of the exported audio files
    output_files = []

    # loop through the audio file and export the audio
    for t1 in range(start_time, end_time, segment_start_delta):
        t2 = min(t1 + segment_length, end_time)
        newaudio = sound[t1:t2]
        new_filename = temp_dir + 'cs6068_final_' + str(t1) + '_' + str(t2) + '.' + filesuffix
        newaudio.export(new_filename, format=filesuffix)
        output_files.append(new_filename)
        if t2 == end_time:
            break

    return output_files

if __name__ == '__main__':
    # default values
    segment_length = 10
    overlap_length = 1
    start_time = 0
    end_time = -1

    # handle command line arguments
    argc = len(sys.argv)
    print(sys.argv)
    if argc < 3:
        print('ERROR: not enough arguments')
        exit()
    filename = str(sys.argv[1])
    segment_length = int(sys.argv[2])
    overlap_length = int(sys.argv[3])
    if argc >= 5:
        start_time = int(sys.argv[4])
    if argc >= 6:
        end_time = int(sys.argv[5])
    if argc > 6:
        print('ERROR: not enough arguments')
        exit()

    split_audio_file(filename, segment_length, overlap_length, start_time, end_time)