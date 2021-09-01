

## Tensorflow Serving&模型部署和性能优化调研总结

### 一、为什么使用tensorflow serving？

功能：

- 支持多种模型服务策略,比如用最新版本/所有版本/指定版本, 以及动态策略更新、模型的增删等
- 自动加载/卸载模型
- Batching
- 多平台支持

性能：

* Batching 
* Fast Model Loading 
* Model Warmup 
* Availability/Resource Proserving Policy

与tensorflow的关系

TFS对TF是源代码级别的依赖, 两者的版本号保持一致, TFS在加载模型、执行推理的过程中, 都是调用TF的库. TFS使用的很多基本构件, 比如多线程库/BatchScheduler, 都是直接使用TF的代码.

### 二、tensorflow serving模型&源码

## Servable（封装）

Servable是对模型的抽象, 但是任何能够提供算法或者数据查询服务的实体都可以是Servable, 不一定是机器学习模型. 

在我们常用的场景下, Servable就是模型. 所以本文有时会混用模型和Servable.

Servable Streams

一个 servable stream是一个服务对象的一系列的版本，按照版本序号递增排序。

servable是一个模型服务，一个model可以由多个servable构成，比如模型串联等，一个model也可以只是一个servable。



Loaders（加载）

Loaders管理一个servable的生命周期，加载之后的Servable也存在Loader里面.

##### Sources（发现）

**Sources**是寻找和提供servables的插件模块。每个Source提供了0个或者更多的servable streams，对于每个servable streams，一个Source对于servable的每个允许加载的版本都提供了一个Loader实例。

TensorFlow Serving应用于Sources的接口能够在任意的存储系统中发现servables。



可以理解为sources发现servable，然后使用loader加载servable。然后推送给manager进行版本控制。

##### Managers（部署）

**Managers**管理Servable的完整的声明周期，包括：

* loading Servables
* serving Servables
* unloading Servables

Managers监听Sources并且追踪所有的versions.Manager试图满足Sources的请求，但是如果需要的资源不可用，可能会拒绝加载期望的版本。Managers也可能推迟卸载，例如，一个Manager可能会等到另外的version加载后再去卸载，保证在每个时刻都至少有一个模型已经被加载。（可用性可资源节省性）



## ServerCore（系统核心服务）

整个服务系统的创建维护, 建立http rest server、grpc server和模型管理部分(AspiredVersionManager)之间的关系等.





两种服务策略：

Aspired version policy

AspiredVersionPolicy是用来决定一个模型的多个版本谁先处理, AvailabilityPreservingPolicy的目标是保证服务可用, 会临时牺牲一些资源, 而 
ResourcePreservingPolicy是优先保证占用更少的资源, 可能会牺牲服务可用性.

代码里面的注释提供了很好的解释, 可参考.

Servable Version Policy

ServableVersionPolicy 
定义了模型的多个版本如何进行选择. 注意和Aspired Version Policy的关系, 一个是如何选择版本, 一个是选择了版本后, 如何选择执行先后顺序.

目前提供3种方式： 
- all 所有的版本 
- latest 最新的N个版本 
- specific 一个或一些指定的版本号


### 三、部署以及使用

由于tensorflow serving只能部署savedmodel格式的模型，所以第一个步骤需要进行模型转换（以部署pytorch框架为例）

流程图

![截屏2021-07-20 下午12.37.48](/Users/yangyu/Desktop/截屏2021-07-20 下午12.37.48.png)

一、模型转换

torch训练完的模型$\Longrightarrow$ONNX格式$\Longrightarrow$SavedModel格式

支持onnx的框架训练完的模型$\Longrightarrow$ONNX格式$\Longrightarrow$SavedModel格式

如果需要模型优化，则还需要嵌入一个tf-trt过程

注：使用任何框架训练模型可以直接在该框架对应的容器中进行，例如训练torch模型，可以直接在anibali/pytorch镜像创建的容器中训练，训练完在该容器中完成ONNX的转换，将ONNX模型转换为pb模型需要在tensorflow环境中进行，可以使用tensorflow/tensorflow镜像创建的容器中配置onnx和onnx-tensorflow进行转换。

此处能够体现出tensorflow serving的多平台支持。

二、模型部署

推荐使用docker的部署方式

### 四、性能调优（吞吐量&时延&高可用）

一、python web和tensorflow serving模块优化

在python web模块主要实现业务逻辑和模型的前后处理

![截屏2021-07-20 上午11.44.31](/Users/yangyu/Desktop/截屏2021-07-20 上午11.44.31.png)

业务逻辑代码可以通过优化逻辑来加快代码执行速度，但是可以忽略。

重点优化在模型的前后处理，尤其是前处理（以bert系列预训练模型为例）。

bert模型需要进行tokenizer，tokenizer需要初始化，为了避免每次都进行初始化，我们将其加载，常驻内存。

使用原始的tokenizer的速度因素有两个，一个是max_length，另外一个是sentence的数量，经过实验验证，tokenizer的速度与sentence的数量线性相关，max_length对tokenizer的速度几乎无影响（试验了16、32、64长度）。

在100条长度为10的短文本中，无论max_length是多少，tokenizer的时间消耗大概为0.022（22ms）。

可以改为tokenizerfast进行优化。

flask：众所周知flask是同步的框架，

在风控场景下我们需要在吞吐量和时延达到均衡，比如限制一个时延，然后优化到最大的吞吐量。

同步请求场景：

用户一次发送一个batch的样本给web server，等到收到返回数据后再发送另外一个batch，

在给定时延下，我们优化模型的吞吐量，比如最优batch，在这种情况下，我们不需要使用tfserving的batching，因为我们可以在web端控制。

高并发请求场景：

用户一次发送一个batch的样本给web server，存在多个用户同时调用的情况。

这种情况下，web端会并发调用tfserving服务，此时可以使用tfserving的batching，在设定的时延下，tfserving端会汇集所有在时延内到达的数据，组成batch进行推理。

tensorflow serving内部通过异步调用的方式，实现高可用，可以通过自动组织batch的方式节省gpu资源。

web server的高并发配置负载均衡等属于web领域。此处从tfserving的角度介绍



为什么要组成batch？batch的大小如何设置？

经过试验，使用bert系列模型的推理速度主要受max_length以及batch的大小以及推理硬件（GPU型号或者CPU）三方面的影响。

模型的吞吐量计算结果如下：

P100 22G:

Albert  16长度吞吐量：15317，同时容纳16200条

albert 32长度吞吐量：13746 同时容纳6200条

albert 64长度吞吐量：6571同时容纳2700条



bert 16长度吞吐量：2685 同时容纳2200条

bert 32长度吞吐量：1439 同时容纳1100条

bert 64长度吞吐量：986   同时容纳400条

模型的吞吐量与硬件、max_length大小以及模型大小都有影响，需要在这几个要素之间trade-off。

模型与max_length长度的统计图。



根据分析，可以在给定时延下选定最优的batch大小以及模型选择等等。

三、模型模块

1. 模型可以进行量化（适用于对精度要求不高的模型）

2. 模型可以通过tf-trt进行模型结构的优化
3. 知识蒸馏

四、其他

如何实现指定gpu？在tfserving docker镜像创建容器时，指定可见的gpu即可。不同的模型可以通过不同的gpu

