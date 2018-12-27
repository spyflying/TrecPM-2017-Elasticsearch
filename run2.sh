#!/usr/bin/env bash

BASE_PATH=$(pwd)

pip install nltk

echo "Creating index, it takes a long time..."
python extract_xml_to_elastic_multiprocess.py

echo "Training..."
python query_train.py

echo "Testing..."
python query_test.py

echo "Calculating Precision"
cd trec_eval.9.0
make clean
make
trec_eval ./clinicaltrials/qrels-final-trials.txt ./qresults/results.txt
