if [ $# -ne 1 ]
then
    echo 'Error:  Number of parameter should be 1'
    echo 'Usage:  sh traid.sh <topic>'
    exit
fi

python3.4 traid_detection.py $1 'test'
python3.4 traid_detection.py $1 'train'
python3.4 traid_detection.py $1 'label'
python3.4 traid_detection.py $1 'unlabel'