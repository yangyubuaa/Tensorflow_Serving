if [ ! -d "/opt/app/tfserving" ]; then
    mv ../tfserving /opt/app/
fi
docker run --gpus=all  -p 8501:8501 -v /opt/app/tfserving/:/models/MultiModel --name=tfserving -t tensorflow/serving:latest-gpu --config=cuda --model_config_file=/models/MultiModel/model.config --enable_batching=true --batching_parameters_file=/models/MultiModel/batch.config
