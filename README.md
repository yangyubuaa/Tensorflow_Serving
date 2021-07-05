### TFServing部署代码
1. 使用git clone到服务器，运行start_tfserving.sh即可，如果stop_tfserving将停止tfserving服务
2. 项目会自动拷贝到/opt/app/下创建tfserving目录运行
3. 目录下文件夹为每个需要部署的模型，每个文件夹下放置不同的模型版本，如果需要更新模型，则将版本号置为最大即可
4. 如果需要添加新的模型，需要先停止tfserving服务，然后将新模型文件夹放入，更新model.config文件，重启服务即可
