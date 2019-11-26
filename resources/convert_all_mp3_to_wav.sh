# script to help mp3 to wav conversion
# we only explicitly support WAV right now so ffmpeg will allow us to guarantee our audio configuration
# MUST BE EXECUTED FROM THE RESOURCES FOLDER

# ffmpeg || echo "error, ffmpeg not found! install and put it on your path first!"; exit 1

# echo "found ffmpeg converting all mp3s to wavs"

# TODO: make this smarter & verify (or just support other types. google cloud is finicky with mp3 though it seems)
ffmpeg -y -i LectureShort.mp3 -ac 1 -acodec pcm_s16le -ar 16000 LectureShort.wav
ffmpeg -y -i LectureFull.mp3 -ac 1 -acodec pcm_s16le -ar 16000 LectureFull.wav

