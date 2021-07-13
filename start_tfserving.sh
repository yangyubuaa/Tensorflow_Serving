if [ ! -d "/opt/app/tfserving" ]; then
    mv ../tfserving /opt/app/
fi
docker run  -p 8501:8501 -v /opt/app/tfserving/:/models/MultiModel --name=tfserving -t tensorflow/serving --model_config_file=/models/MultiModel/model.config --enable_batching=true --batching_parameters_file=/models/MultiModel/batch.config
