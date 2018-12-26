import xml.etree.ElementTree as ET
import collections
import elasticsearch_copy
import os

topic_division = [[28, 29, 25, 22, 6, 7], [26, 11, 1, 18, 21, 4], [19, 24, 27, 30, 12, 23], [13, 14, 3, 16, 8, 9], [15, 20, 5, 10, 17, 2]]
group_boost = [5, 5, 2, 2, 2]

# query_word = ["clinical including criteria advanced and/or drug tumors dose potential history solid combination", "combination advanced and/or drug tumors clinical dose criteria ≥ blood potential history including", \
#               "clinical including criteria advanced and/or drug tumors inclusion defined dose ≥ potential inhibitor history active metastases combination mutation", \
#               "blood clinical including criteria advanced and/or drug tumors dose uln ≥ potential inhibitor history solid combination mutation", \
#               "clinical trial including criteria advanced and/or drug tumors ≥ potential inhibitor history solid combination mutation"]

cache_root = "cache"
result_root = "qresults"
data_root = "clinicaltrials"

def query_word_generate():
    """Generating query words according to keywords.txt"""
    query_word = []
    for i in range(1, 6):
        s = ""
        with open(cache_root+"/cache{}/keyword.txt".format(str(i)), "r") as keyword:
            for line in keyword:
                w = line.strip()
                s += w
                s += " "
        query_word.append(s)

    return query_word

query_word = query_word_generate()

def extract_query_xml(group_id):
    """
    The query topics are provided in an XML file. This function is used to extract query terms from that XML file.
    After extracting the query terms, it is stored in an ordered dictionary. This dictionary is then passed to the es_query function which will query Elasticsearch with those terms.
    """

    # Provide the path to the query xml file
    query_file = open(os.path.join(data_root, "topics2017.xml"), "r")

    tree = ET.parse(query_file)
    root = tree.getroot()

    # Create an ordered dictionary to store the query terms
    extracted_data = collections.OrderedDict()

    # There are 30 query topics provided. First we store all the topics and iterate over each of them using a for loop.
    # Each query topic contains multiple fields. In the try-except block we try to extract the terms for each particular query. These extracted terms are stored in an ordered dictionary with key as the field name and value as the extracted terms.
    try:
        print("generating group ", group_id)
        topics = root.findall('topic')
        for index, item in enumerate(topics):
            tnum = index + 1
            if tnum in topic_division[group_id]:
                print("docid ", tnum)
                disease = item.find('disease').text
                gene = item.find('gene').text
                demographic = item.find('demographic').text
                other = item.find('other').text
                extracted_data['tnum'] = tnum
                extracted_data['disease'] = disease
                extracted_data['gene'] = gene
                extracted_data['age'] = int(demographic.split('-')[0])
                extracted_data['sex'] = demographic.split(' ')[1]
                extracted_data['other'] = other
                es_query(group_id, extracted_data)
    except:
        extracted_data['tnum'] = None
        extracted_data['disease'] = None
        extracted_data['gene'] = None
        extracted_data['age'] = None
        extracted_data['sex'] = None
        extracted_data['other'] = None

    return


def es_query(group_id, extracted_data):
    """
    This function is used to query Elasticsearch and write results to an output file.
    It receives a dictionary containing the extracted query terms from the extract_query_xml function. After querying Elasticsearch, the retrieved results are written to an output file in the standard trec_eval format.
    """

    try:
        # Store the disease name from the received dictionary in the variable named query
        main_query = extracted_data['disease']
        age_query = int(extracted_data['age'])
        sex_query = extracted_data['sex']
        gene_query = extracted_data['gene']
        if extracted_data['other'] != 'None':
            aux_query = extracted_data['other']
        else:
            aux_query = None
        # print("main_query : {}, age_query : {}, sex_query : {}, aux_query : {}, gene_query : {}".format(main_query, age_query, sex_query, aux_query, gene_query))
        # For a simple query without any customizations, uncomment the following line
        # res = es.search(index='ct', q=query, size=1000)['hits']['hits']
        # Current implementation uses a customized query with multi-match and post-filters in a manner deemed best possible for the current retrieval process. Comment the following query if you plan to use the simple query in the previous line.
        # We limit the retrieved results to 1000. The results are arranged in decreasing order of their assigned scores. We assign a rank to each result starting from 1 to 1000 based on decreasing scores. We normalize the score for each result based on the score of the first result with the maximum score.
        # res = es.search(index = 'ct', body = {
        #     "query" :{
        #         "bool" :{
        #             "must":{
        #                 "multi_match" : {
        #                     "query" : main_query,
        #                     "type" : "phrase_prefix",
        #                     "fileds" : ["brief_title", "brief_summary", "detailed_description", "eligibility", "keyword", "mesh_term"],
        #                     "fuzziness" : "AUTO"
        #                 }
        #             },
        #             # "" : {"match" : {"gender" : sex_query}},
        #             "must" : {"range" : {"maximum_age" : {"gte" : age_query}}},
        #             "must" : {"range" : {"minimum_age": {"lte" : age_query}}},
        #             "should" : [
        #                 {"term" : {"eligibility" : main_query}},
        #                 {"term" : {"brief_summary" : main_query}},
        #                 {"term" : {"detailed_description" : main_query}},
        #                 {"term" : {"keyword" : main_query}},
        #                 {"term" : {"brief_title" : main_query}},
        #                 {"term" : {"mesh_term" : main_query}}
        #             ],
        #         },
        #         # "post_filter" : {
        #         #     "term" : {"gender" : "All"}
        #         # }
        #     }
        # }, size = 10)['hits']["hits"]

        # match gene and disease
        # res = es.search(index = 'ct', body = {
        #     "query" : {
        #         "bool" : {
        #             "must":{
        #                     "multi_match": {
        #                         "query": main_query,
        #                         "fields": ["brief_title", "brief_summary", "detailed_description", "eligibility", "keyword", "mesh_term"]
        #                     }
        #                 },
        #             "must": {
        #                 "multi_match": {
        #                     "query": gene_query,
        #                     "fields": ["brief_title", "brief_summary", "detailed_description", "eligibility", "keyword",
        #                                "mesh_term"]
        #                 }
        #             },
        #         }
        #     }
        # }, size=1000)['hits']['hits']

        # match gene and disease, filter gender
        # res = es.search(index = 'ct', body = {
        #     "query" : {
        #         "bool" : {
        #             "must":{
        #                     "multi_match": {
        #                         "query": main_query,
        #                         "fields": ["brief_title", "brief_summary", "detailed_description", "eligibility", "keyword", "mesh_term"]
        #                     }
        #                 },
        #             "must": {
        #                 "multi_match": {
        #                     "query": gene_query,
        #                     "fields": ["brief_title", "brief_summary", "detailed_description", "eligibility", "keyword",
        #                                "mesh_term"]
        #                 }
        #             },
        #         }
        #     },
        #     "post_filter":
        #         {"term":
        #              {"gender": "all"}
        #          }
        # }, size=1000)['hits']['hits']

        # filter with age
        # res = es.search(index='ct', body={
        #     "query": {
        #         "bool": {
        #             "must": {
        #                 "multi_match": {
        #                     "query": main_query,
        #                     "fields": ["brief_title", "brief_summary", "detailed_description", "eligibility", "keyword",
        #                                "mesh_term"]
        #                 }
        #             },
        #             "must": {
        #                 "multi_match": {
        #                     "query": gene_query,
        #                     "fields": ["brief_title", "brief_summary", "detailed_description", "eligibility", "keyword",
        #                                "mesh_term"]
        #                 }
        #             },
        #             "filter" : {
        #                 "range" : {"maximum_age" : {"gte" : age_query}},
        #                 "range" : {"minimum_age" : {"lte" : age_query}}
        #             }
        #         }
        #     },
        #     "post_filter":
        #         {"term" : {"gender": "all"},
        #          },
        # }, size=1000)['hits']['hits']

        #
        # res = es.search(index='ct', body={
        #     "query": {
        #         "bool": {
        #             "must": {
        #                 "multi_match": {
        #                     "query": main_query,
        #                     "fields": ["brief_title * 3", "brief_summary", "detailed_description", "eligibility",
        #                                "keyword * 3",
        #                                "mesh_term * 3"],
        #                 }
        #             },
        #             "must": {
        #                 "multi_match": {
        #                     "query": gene_query,
        #                     "fields": ["brief_title", "brief_summary", "detailed_description", "eligibility", "keyword",
        #                                "mesh_term"],
        #                 }
        #             },
        #             "should": {
        #                 "multi_match": {
        #                     "query": "cancer",
        #                     "fields": ["brief_title", "brief_summary", "detailed_description", "eligibility", "keyword",
        #                                "mesh_term"]
        #                 }
        #             },
        #             "filter": {
        #                 "range": {"maximum_age": {"gte": age_query}},
        #                 "range": {"minimum_age": {"lte": age_query}}
        #             }
        #         }
        #     },
        #     "post_filter":
        #         {"term": {"gender": "all"},
        #          },
        # }, size=1000)['hits']['hits']
        # print("query_word ", query_word[group_id])
        res = es.search(index='ct', body={
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": main_query,
                            "fields": ["brief_title * 3", "brief_summary", "detailed_description", "eligibility",
                                       "keyword * 3",
                                       "mesh_term * 3"],
                            "boost" : group_boost[group_id]
                        }
                    },
                    "must": {
                        "multi_match": {
                            "query": gene_query,
                            "fields": ["brief_title", "brief_summary", "detailed_description", "eligibility", "keyword",
                                       "mesh_term"],
                            "boost" : group_boost[group_id]
                        }
                    },
                    "should":{
                        "multi_match": {
                            "query" : query_word[group_id],
                            "fields" : ["brief_summary", "detailed_description"],
                            "boost" : 1
                        }
                    },
                    "filter": {
                        "range": {"maximum_age": {"gte": age_query}},
                        "range": {"minimum_age": {"lte": age_query}}
                    }
                }
            },
            "post_filter":
                {"term": {"gender": "all"},
                 },
        }, size=1000)['hits']['hits']

        max_score = res[0]['_score']
        rank_ctr = 1
        # with open('/home/sofiahuang/code/TREC_pm/TREC-2017-PM-CDS-Track/qresults/mini_output.txt', 'w') as f:
        #     f.write(json.dumps(res, indent=2, ensure_ascii=False))
        # # print(json.dumps(res, indent=2, ensure_ascii=False))

        # input()

        # Write the retrieved results to an output file in the standard trec_eval format
        with open('qresults/results.txt', 'a') as op_file:
            for i in res:
                op_file.write(
                    '{}\tQ0\t{}\t{}\t{}\t2_ec_complex\n'.format(extracted_data['tnum'], i['_source']['nct_id'],
                                                                rank_ctr, round(i['_score'] / max_score, 4)))
                rank_ctr += 1

        print("finish_writing")

    except Exception as e:
        print("\nUnable to query/write!")
        print('Error Message:', e, '\n')

    return


if __name__ == '__main__':
    # Create connection to Elasticsearch listening on localhost port 9200. It uses the Python Elasticsearch API which is the official low-level client for Elasticsearch.
    try:
        es = elasticsearch_copy.Elasticsearch([{'host': 'localhost', 'port': 9200}])
    except Exception as e:
        print('\nCannot connect to Elasticsearch!')
        print('Error Message:', e, '\n')
    # Call the function to start extracting the queries
    for i in range(5):
        extract_query_xml(i)