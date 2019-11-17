"""
execute basic speech recognition on a wav file
DISCLAIMER: this is just pseudo/theoretical code at the moment it wont actually do anything/run

Training is directly from:
https://github.com/tensorflow/docs/blob/master/site/en/r1/tutorials/sequences/audio_recognition.md

NOTE: We would need to obtain a lot of training data for our desired words
    the example/tutorial only supports about 30 words by default
    once we get the training data we would have to organize audio files into folders named after the keyword
    then set up a testing_list and validation_list

The model being used will be created by doing the following:
    cp <our_training_data> /tmp/speech_dataset
    git clone git@github.com:tensorflow/tensorflow.git
    cd tensorflow
    python3 tensorflow/examples/speech_commands/train.py \
        --wanted_words "exam,test,assignment,homework,important"

    Note: it will take awhile so run it overnight or something

    Then copy the training results into here:
    cp /tmp/speech_commands_train/* <repo_path>/resources/learn

    and modify the checkpoint file to have the appropriate paths if necessary

Usage
    python3 profiler.py

"""
import numpy as np
import tensorflow as tf

import input_data
import models

# DISCLAIMER-RE: once again, this is pseudocode for now, do not expect it to work
# been using https://github.com/tensorflow/tensorflow/blob/master/tensorflow/examples/speech_commands/train.py as a reference

# Load the graph and start a session
with tf.gfile.FastGFile('chkpt_path/conv.pbtxt', "rb") as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    g_in = tf.import_graph_def(graph_def, name="")
sess = tf.Session(graph=g_in)

# Load the weights
models.load_variables_from_checkpoint(sess, 'chkpt_path/checkpoint')
tf.import_graph_def(graph_def_path)

# Load the labels
labels = []
with gfile.GFile('chkpt_path/conv_labels.txt', 'r') as f:
    labels.append(f.readline(audio_processor.words_list).strip())

# unclear how yet but load the input wav data and evaluate it
timestamps = sess.run([], feed_dict={ input: audio_input })

sess.close()
