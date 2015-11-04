./OpenCRF_Main -est -niter 30 -nbpiter 30 -dstmodel ./train_model.txt -method gradient -gradientstep 0.02 -hasvalue -trainfile ../results/train.txt -testfile ../results/test.txt
./OpenCRF_Main -inf -niter 30 -nbipter 30 -srcmodel ./train_model.txt -method gradient -gradientstep 0.02 -hasvalue -trainfile ../results/train.txt -testfile ../results/unlabel.txt
cp ./pred.txt ../results/pred.txt
python3.4 generate_predict_link.py