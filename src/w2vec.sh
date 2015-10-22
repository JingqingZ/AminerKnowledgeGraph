#! /bin/bash
# prepare data, word2vec training and calculate cosine distance 

# input should be data_mining, not data mining
# output1 BIN_FILE is needed for distance tool provided by word2vec
# output2 TXT_FILE is the file vector of each word

if [ $# -ne 1 ]
then
    echo 'Error:  Number of parameter should be 1'
    echo 'Usage:  $ ./w2vec.sh <topic>'
    exit
fi

python3.4 convert_abs.py $1

TRAIN_FILE=../results/pub_$1.abs
BIN_FILE=../results/vec_$1.bin
TXT_FILE=../results/vec_$1.txt

word2vec -train $TRAIN_FILE -output $BIN_FILE -size 200 -window 5 -sample 1e-4 -negative 5 -hs 0 -binary 1 -cbow 1 -iter 3
word2vec -train $TRAIN_FILE -output $TXT_FILE -size 200 -window 5 -sample 1e-4 -negative 5 -hs 0 -binary 0 -cbow 1 -iter 3
