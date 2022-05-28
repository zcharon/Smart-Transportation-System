## YOLOv5目标检测网络

### 一、模型结构

1. #### 原始结构：

   原始YOLOv5结构采用Backbone+Neck+Head结构，其中Backbone结构基础为CSPNet，Neck结构基础为PANet，Head为回归拟合

   ​		![](README.assets\YOLOv5模型.jpg)

   模型结构与参数量：

   ![](README.assets\YOLOv5.png)

   可以发现，整体模型参数量为7071633，共有283层。

2. ### 改进结构：

   1. ##### Backbone结构改进：

      为了达到降低参数量的目的，将Backbone的CSPNet结构修改为，MobilenetV2的残差结构。具体模型配置在`models/yolov5s-mobilenetv2.yaml`文件中。

      模型结构与参数量：

      ![YOLOv5-MobilenetV2](README.assets\YOLOv5-MobilenetV2.png)

      使用可分离卷积后，可以发现，参数量有了明显的降低，网络的运行速度大大提高。

   2. ##### Neck层改进：

      谷歌在EfficientNet中提出BiFPN特征融合网络，其理论性能比原始的PANet要好不少。并且，BiFPN与PANet的不同点还有，PANet在Neck层只能使用一次，而BiFPN在Neck层可以连续使用多次，大大增加了特征融合能力。

      ![BiFPN](README.assets\BiFPN.png)

      由图片可以看出，其在PANet的基础上增加了残差边，大大加强了网络的特征融合能力，其次，其删除了单输入的节点，在对网络造成很小的影响的前提下减少了网络的参数量，最后，该网络中增加了注意力机制。BiFPN = 新型加强版的PANet(重复双向跨尺度连接) + 带权重的特征融合机制。

      ![YOLOv5_BiFPN](README.assets\YOLOv5_BiFPN.png)

      在该模型中，第16，19，22分别使用了BiFPN网络，但是模型总体参数相差不大。

3. ### 模型使用方法：

   1. 训练时：

      首先，在`yolov5/models`中选择相应的网络结构（yaml文件中不能含有中文），之后在运行train.py时，`--cfg`参数选择对应yaml文件即可。

   2. 项目使用时：

      在detector.py中填写对应权重文件路径即可，程序会根据权重文件自动调动对应的网络。

4. ### 模型训练效果：

   因为编写项目的时间问题，本人未能找到满意的数据集，数据集样本过少，所以对训练的结果不太满意。

   而且，YOLOv5的Neck层换为BiFPN后模型性能应该会有所提升，但是结果却不如原模型。。。

   橙色为使用官方coco预训练权重做迁移学习的训练效果。

   训练硬件平台：CPU: Intel(R) Xeon(R) CPU E5-2690 v4 @ 2.60GHz

   ​    					   GPU: Nvidia Tesla P100-PCIE 16G
   
   橙色：YOLOv5迁移训练；
   
   浅蓝色：YOLOv5原始模型；
   
   深蓝色：YOLOv5+BiFPN
   
   红色：YOLOv5+Mobilenet
   
   ![训练情况](README.assets\训练情况.png)

