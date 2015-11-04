if [ $# -ne 1 ]
then
    echo 'Error:  Number of parameter should be 1'
    echo 'Usage:  sh ./train.sh <query>'
    exit
fi

./OpenCRF_Main -est -niter 30 -nbpiter 30 -dstmodel ./train_model.txt -method gradient -gradientstep 0.02 -hasvalue -trainfile ../results/$1/train.txt -testfile ../results/$1/test.txt
./OpenCRF_Main -inf -niter 30 -nbipter 30 -srcmodel ./train_model.txt -method gradient -gradientstep 0.02 -hasvalue -trainfile ../results/$1/train.txt -testfile ../results/$1/unlabel.txt
cp ./pred.txt ../results/$1/pred.txt
python3.4 generate_predict_link.py
cp ../results/$1/results.txt ../../views/pattern_analysis/results/$1/results.txt
cp ../results/$1/results_label.txt ../../views/pattern_analysis/results/$1/results_label.txt
cp ../results/$1/results_pred.txt ../../views/pattern_analysis/results/$1/results_pred.txt