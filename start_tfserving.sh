mv ../tfserving /opt/app/
docker run -itd -p 8501:8501 -v /opt/app/tfserving/:/models/MultiModel --name=tfserving -t tensorflow/serving --model_config_file=/models/MultiModel/model.config
