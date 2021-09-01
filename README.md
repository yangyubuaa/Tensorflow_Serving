### TFServing部署代码
---
### 文件说明
1. model.config 模型配置文件
2. batch.config 每个serving服务的批处理参数文件
3. platform.config 控制显存占用需要使用的文件，否则显存会占满
4. start_tfserving.sh 启动cpu版本服务
5. start_tfserving_gpu.sh 启动gpu版本服务
6. start_tfserving_multi_gpu.sh 每块gpu启动多个tfserving服务
7. stop_tfserving.sh 关闭所有的tfserving服务
8. 测试tfserving模型服务接口可用性
---
### 使用说明
##### 基本
1. 使用git clone到服务器，运行start_tfserving.sh（cpu版本）或start_tfserving_gpu.sh（gpu版本）即可，如果stop_tfserving将停止tfserving服务
2. 项目会自动拷贝到/opt/app/下创建tfserving目录运行
3. 目录下文件夹为每个需要部署的模型，每个文件夹下放置不同的模型版本，如果需要更新模型，则将版本号置为最大即可
4. 如果需要添加新的模型，需要先停止tfserving服务，然后将新模型文件夹放入，更新model.config文件，重启服务即可
##### 使用gpu起多个服务的配置方法
1. 需要使用start_tfserving_multi_gpu.sh启动服务
2. 需要根据机器情况调整start_tfserving_multi_gpu.sh的参数：端口映射；gpu数目以及想要用的gpu编号；用到的gpu上每块起几个tfserving服务
3. 配置nginx使用端口转发，默认转发方式即可，配置对外的模型服务端口，将到达该端口的请求通过nginx转发到所有的tfserving服务上
---
### 环境要求
1. 服务器安装docker环境即可
---
### 每块gpu可以起多个服务的原理和方法
1. 原理：我们使用多gpu部署，每块gpu起一个tfserving woker的话，会造成显存以及算力资源的浪费，所以我们可以起多个tfserving服务，同时推理，但是需要考虑显存占用，不能起太多，需要预留出数据的显存占用，达到最优的trade off
2. 方法：docker启动容器时可以指定容器内可见的gpu编号，我们利用这个特性，能够指定gpu上启动tfserving容器服务，一块gpu上可以起多个容器服务。
---
### 参数调整建议
1. 每块gpu起几个服务
2. 每个服务的参数配置（batch.config）见tfserving官方文档
