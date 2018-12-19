#### 代码介绍
* elasticsearch_copy: 需要代码包,可以通过pip安装,也可以直接copy
* extract\_xml\_to_elastic.py: 将clinicaltrials\_xml中的xml文件添加到名为"ct"的index中,每条xml文件创建一条相应id的数据
* query\_elasticsearch.py: 构建查询语句,生成查询结果文件
* trec_eval.8.1: 评测脚本(还不知怎么用)

#### 数据说明
* clinicaltrials\_xml: 三级目录,共24万条电子病例数据,每条数据存为一个.xml文件
* topics2017.xml: 待查询的文件,共30个topic,在query_elasticsearch.py脚本中对每个topic构建查询语句,生成查询结果
* qrels-final-trials.txt: topics2017对应的ground truth文件

#### 环境要求
* Elasticsearch
不需要安装,直接下载tar包,解压后进入文件夹运行:
> ./bin/elasticsearch

* python 2.7

#### 任务说明
* 优化查询语句构建,修改query\_elasticsearch.py中es\_query()函数;优化代码
* 跑通测试脚本,可以成功测试P@5, P@10, P@15(或者自己想办法写一个)
* 编写界面程序
前三个任务可以同步进行
* 得到最终的查询结果,测试精度
* 五折交叉验证? 好像不需要
* 完成实验报告
