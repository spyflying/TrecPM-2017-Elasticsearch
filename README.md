#### 代码介绍
* elasticsearch_copy: 需要代码包,可以通过pip安装,也可以直接copy
* extract\_xml\_to_elastic.py: 将clinicaltrials\_xml中的xml文件添加到名为"ct"的index中,每条xml文件创建一条相应id的数据
* query\_elasticsearch.py/ query\_elasticsearch_multiprocess.py: 构建查询语句,生成查询结果文件;multiprocess多进程并行
* trec_eval.9.0: 评测脚本;make命令编译,编译好调用
> trec_eval qrel.txt result.txt

得到最终结果

#### 数据说明
* clinicaltrials\_xml: 三级目录,共24万条电子病例数据,每条数据存为一个.xml文件
* topics2017.xml: 待查询的文件,共30个topic,在query_elasticsearch.py脚本中对每个topic构建查询语句,生成查询结果
* qrels-final-trials.txt: topics2017对应的ground truth文件

#### 环境要求
* Elasticsearch
不需要安装,直接下载tar包,解压后进入文件夹运行:
> ./bin/elasticsearch

* python 3.6
* nltk

#### 任务说明
* 优化查询语句构建,修改query\_elasticsearch.py中es\_query()函数;优化代码-已完成
* 跑通测试脚本,可以成功测试P@5, P@10, P@15(或者自己想办法写一个)-已完成
* 编写界面程序
* 整理代码,可以一键执行
* 需要在TREC 2017 PM上提交吗
* 完成实验报告
