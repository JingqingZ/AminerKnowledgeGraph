if [ $# -ne 1 ]
then
    echo 'Error:  Number of parameter should be 1'
    echo 'Usage:  $ ./w2vec.sh <topic>'
    exit
fi

echo "knoledge graph"
# python3.4 ./knowledge_graph.py $1

echo "word2vec"
# sh ./w2vec.sh $1

echo "get factor"
python3.4 ./get_topic_factor.py $1

echo "social tie"
../social_tie/src/OpenCRF_Main -est -niter 30 -nbpiter 30 -dstmodel ../social_tie/src/train_model.txt -method gradient -gradientstep 0.02 -hasvalue -trainfile ../social_tie/results/$1/train.txt -testfile ../social_tie/results/$1/test.txt
../social_tie/src/OpenCRF_Main -inf -niter 30 -nbipter 30 -srcmodel ../social_tie/src/train_model.txt -method gradient -gradientstep 0.02 -hasvalue -trainfile ../social_tie/results/$1/train.txt -testfile ../social_tie/results/$1/unlabel.txt
cp ./pred.txt ../social_tie/results/$1/pred.txt


echo "generate predict link"
# python3.4 ./generate_predict_link.py $1
# cp ../social_tie/results/$1/results.txt ../views/pattern_analysis/results/$1/results.txt
# cp ../social_tie/results/$1/results_label.txt ../views/pattern_analysis/results/$1/results_label.txt
# cp ../social_tie/results/$1/results_pred.txt ../views/pattern_analysis/results/$1/results_pred.txt


echo "generate html to review"
# python3.4 ./generate_labeled_view.py $1