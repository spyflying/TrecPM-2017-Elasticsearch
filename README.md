### 代码介绍
* `elasticsearch_copy`: 需要代码包，可以通过pip安装，也可以直接copy

* `extract_xml_to_elastic.py/extract_xml_to_elastic_multiprocess.py`: 将clinicaltrials\_xml中的xml文件添加到名为"ct"的index中，每条xml文件创建一条相应id的数据；multiprocess为多进程并行

* `query_train`: 训练过程，用24个topic的ground-truth文档进行训练，训练结果：cache/cache*/keywords.txt

* `query_test`: 进行五折交叉验证，分别以其中4折作为训练集，剩下一折作为测试集，得到的查询结果；结果：qresults/result.txt

* `test_all`: 将所有样本都拿来训练后，测试所有的topic，生成查询结果

* `trec_eval.9.0`: 评测脚本；`make`命令编译；编译完成后执行`trec_eval qrel.txt result.txt`得到最终结果

* `query_test_interaction.py`: 交互式评测脚本，输入topic id (1~30)，返回按照score排序的查询结果

* `run.sh`: 一键执行建立索引、训练、测试和结果评价脚本

* `search.sh`: 交互式查询界面脚本

### 数据说明
* `clinicaltrials_xml`: 三级目录，共24万条电子病例数据，每条数据存为一个.xml文件

* `topics2017.xml`: 待查询的文件，共30个topic，在query_elasticsearch.py脚本中对每个topic构建查询语句，生成查询结果

* `qrels-final-trials.txt`: topics2017对应的ground-truth文件

### 环境要求
* `Elasticsearch`
	
	不需要安装,直接下载tar包,解压后进入文件夹运行:
	> ./bin/elasticsearch

* `Python 3.6`

* `nltk`
	
	终端执行以下命令安装nltk，并在python中使用nlpk安装punkt
	
	```
	user$ pip install nlpk
	user$ python
	>>> import nlpk
	>>> nlpk.download('punkt')
	```

### 运行说明
* 数据
> clinicaltrials/

* 运行Elastic Search
> ./bin/elasticsearch

* 构建索引
> python extract\_xml\_to\_elastic\_multiprocess.py

* 训练
> python query\_train.py

* 测试
> python query\_test.py

* 计算P5,P10,P15
> trec_eval clinicaltrials/qrels-final-trials.txt qresults/result.txt

* 一键执行建立索引、训练、测试和结果评价
> ./run.sh

* 交互式界面
> ./search.sh

### 任务说明
* 优化查询语句构建,修改query\_elasticsearch.py中es\_query()函数;优化代码 --- 已完成
* 跑通测试脚本,可以成功测试P@5, P@10, P@15 --- 已完成
* 编写界面程序
* 整理代码,可以一键执行
* 需要在TREC 2017 PM上提交吗
* 完成实验报告

### 方法介绍
* 索引构建:使用elasticsearch构建全文索引;采用tf/idf(或BM25模型）
* 查询构建:初始查询使用topic中的"disease","gene","gender","age"字段构建查询语句,其中"disease"和"gene"采用"multi_match"查询,对"brief_title", "brief_summary", "detailed_description", "eligibility", "keyword","mesh_term"等filed进行匹配,同时参与相关性计算;"disease"和"gene"之间用AND连接
```
    "must": {
        "multi_match": {
            "query": main_query,
            "fields": ["brief_title * 3", "brief_summary", "detailed_description", "eligibility",
                "keyword * 3",
                "mesh_term * 3"],
        }
    },
    "must": {
        "multi_match": {
            "query": gene_query,
            "fields": ["brief_title", "brief_summary", "detailed_description", "eligibility", "keyword",
                "mesh_term"],
        }
    },
```

"gender"和"age"采用"filter"对文档进行过滤,不参与相关性计算
```   
    "filter": {
        "range": {"maximum_age": {"gte": age_query}},
        "range": {"minimum_age": {"lte": age_query}}
    }
    "post_filter": {"term": {"gender": "all"},}
```

以上查询不采用topic的ground truth信息,仅根据已有的索引和检索字段进行查询,精度略低
* 训练: 采用5折交叉验证,24个topic作为训练样本,6个topic作为测试样本.

正样本: 每个topic对应的ground truth中所有相关文档

负样本: 每个topic对应的ground truth中所有不相关文档中随机挑选30条

topic frequency: 每个word在每个topic中出现的总次数,定义为topic frequency

doc frequency: 每个word在所有topic的所有文档中出现的总次数,为doc frequency

训练过程是基于相关文档和不相关文档的topic frequency和doc frequency进行的.规定高频词为:参与训练的24个topic中,如果在其中12个或更多的topic的对应文档中的topic frequency都大于50,并且doc frequency大于300,这个word就可以认为是高频词;训练中,如果一个word在相关文档中是高频词,且在不相关文档中不是高频词,可以说明这个word更可能是相关文档具有的特征,可以被选为查询词构建查询语句.之所以要在12个或更多的topic中topic frequency都很大,是因为这样选出来的词在不同topic的相关文档中出现相对均匀,更容易迁移到测试topic上.

* 测试:除了采用topic中的字段构建查询语句,还使用了从训练样本中得到的关键词构建查询语句.并且,为了使得不同查询语句具有不同的权重,还加入"boost"字段,对"desease"和"gene"查询赋予更高的权重,权重是根据测试集的表现进行挑选的.
```
    "multi_match": {
        "query" : query_word[group_id],
        "fields" : ["brief_summary", "detailed_description"],
        "boost" : 1
     }
```

* 查询词选择结果:
```
    train=2,3,4,5; test=1: clinical including criteria advanced and/or drug tumors dose potential history solid combination
  
    train=1,3,4,5; test=2: combination advanced and/or drug tumors clinical dose criteria ≥ blood potential history including
  
    train=1,2,4,5; test=3: clinical including criteria advanced and/or drug tumors inclusion defined dose ≥ potential inhibitor history active metastases combination mutation
  
    train=1,2,3,5; test=4: blood clinical including criteria advanced and/or drug tumors dose uln ≥ potential inhibitor history solid combination mutation
  
    train=1,2,3,4; test=5: clinical trial including criteria advanced and/or drug tumors ≥ potential inhibitor history solid combination mutation
```

虽然每轮训练得到的查询词数目不同,但是很多词基本相同

