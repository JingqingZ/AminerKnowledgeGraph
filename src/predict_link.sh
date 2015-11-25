if [ $# -ne 1 ]
then
    echo 'Error:  Number of parameter should be 1'
    echo 'Usage:  sh predict_link.sh <topic>'
    exit
fi

python3.4 generate_predict_link.py $1
cp ../social_tie/results/$1/results.txt ../views/pattern_analysis/results/$1/results.txt
cp ../social_tie/results/$1/results_label.txt ../views/pattern_analysis/results/$1/results_label.txt
cp ../social_tie/results/$1/results_pred.txt ../views/pattern_analysis/results/$1/results_pred.txt
python3.4 generate_link_view.py $1 label
python3.4 generate_link_view.py $1 pred
python3.4 generate_link_view.py $1 all