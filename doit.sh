#!/bin/bash

# script to batch process audio (wav files)
# USAGE:
#     ./doit.sh ./resources test final critical important
#         # this would process every wav file (in background) for test, final, critical, important and record/display results

#if [ -z $1 ] then
#  python3 ./main.py -c parallel -i ./resources/LectureShort.wav -z 59000 -o 750 -t -k "test exam final midterm study critical important"
#else
#  python3 ./main.py -c parallel -i ./resources/LectureShort.wav -z 59000 -o 750 -t -k "$*"
#fi


echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo "STARTING DOIT"
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

if [ ! -e "$1" ]; then
	echo "arg1 ($1) not valid location"
	exit 1
fi

if [ "$#" -lt 2 ]; then
	KEYWORDS="test exam final midterm study critical important"
else
	KEYWORDS="$*"
fi;

#echo $KEYWORDS
#exit 0

if [ -d $1 ]; then 
	echo "$1 is dir"; 
	for f in $(ls $1/*.wav); do 
		python3 ./main.py -c parallel -i "$f" -z 59000 -o 750 -t -k "$KEYWORDS" > $f.results 2>&1 &
	done;
elif [ -f $1 ]; then
	echo "$1 is file";
	python3 ./main.py -c parallel -i $1 -z 59000 -o 750 -t -k "$KEYWORDS"
else
	echo "unsure what '$1' is";
	exit 1;
fi

wait
echo "done"


if [ -d $1 ]; then 
	echo "=============================="
	echo "results:"
	echo "=============================="
	for f in $(ls $1/*.results); do
		echo "------------------------------"
		echo "$f: ";
		echo "------------------------------"
		cat $f;
	done;
fi


