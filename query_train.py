import glob
import xml.etree.ElementTree as ET
import collections
import time
import nltk
import pickle
import os

data_root = "clinicaltrials/"
cache_root = "cache"

all_tf = [collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict()]
all_df = [collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict()]
all_tf_un = [collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict()]
all_df_un = [collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict()]

count_field = ["brief_title", "brief_summary", "detailed_description", "eligibility", "keyword","mesh_term"]
topic_division = [[28, 29, 25, 22, 6, 7], [26, 11, 1, 18, 21, 4], [19, 24, 27, 30, 12, 23], [13, 14, 3, 16, 8, 9], [15, 20, 5, 10, 17, 2]]
punc_list = [",", "<", ">", ".", "?", "/", ":", ";", "'", "[", "]", "{", "}", "\\", "|", "-", "_", "+", "=", "*", "!", "@", "#", "$", "%", "^", "(", ")", " "]


stop_list = []

# create stop_list according to stop_list.txt
with open("stop_list.txt", "r") as f:
    for line in f:
        w = line.strip()
        stop_list.append(w)



def count_tf(group_id, extracted_data, topic_id, is_rel):
    """This function is to count tf and idf for given doc's extracted_data"""

    tmp_df = collections.OrderedDict()
    # print("group {}, tmp_df {}".format(group_id, tmp_df))

    for field in count_field:
        msg = extracted_data[field]
        if msg:
            word_list = nltk.word_tokenize(msg)
            for w in word_list:
                if len(w) > 0:
                    # translate to lower
                    w = w.lower()

                    # get rid of stop_word and punctuations
                    if (w not in stop_list) and (w not in punc_list) and (not w.isdigit()):

                    # get rid of postfix like 's, 've
                        for postfix in stop_list[0:7]:
                            i = w.find(postfix)
                            if i != -1:
                                w = w[ : i]

                                # add in all_tf
                        if is_rel:
                            if w not in all_tf[group_id]:
                                all_tf[group_id][w] = [0] * 24
                                all_tf[group_id][w][topic_id] = 1
                            else:
                                all_tf[group_id][w][topic_id] += 1

                        else:
                            if w not in all_tf_un[group_id]:
                                all_tf_un[group_id][w] = [0] * 24
                                all_tf_un[group_id][w][topic_id] = 1

                            else:
                                all_tf_un[group_id][w][topic_id] += 1

                        # add in tmp_df
                        if w not in tmp_df:
                            tmp_df[w] = 1

    # print("all_tf : ", all_tf)
    # print("all_tf_un : ", all_tf_un)
    # add in all_df
    for k in tmp_df.keys():
        if is_rel:
            if k not in all_df[group_id]:
                all_df[group_id][k] = 1
            else:
                all_df[group_id][k] += 1
        else:
            if k not in all_df_un[group_id]:
                all_df_un[group_id][k] = 1
            else:
                all_df_un[group_id][k] += 1
    # print("all_df : ", all_df)
    # print("all_df_un : ", all_df_un)
    # input()



def extract_doc(group_id):
    """given group id, this function is to count tf and idf for all related docs and 30 unrelated docs which are randomly chosen for each topics"""

    ct = 0
    topic_list = []
    for i in range(5):
        if i != group_id:
            topic_list += topic_division[i]
    # print("topic list ", topic_list)
    gt_dict = dict()
    unrel_ct_dict = dict()
    for topic_id in topic_list:
        gt_dict[topic_id] = []
    idx_dict = dict()
    for idx, topic_id in enumerate(topic_list):
        idx_dict[topic_id] = idx
        unrel_ct_dict[topic_id] = 0
    # print(idx_dict)

    with open(os.path.join(data_root, 'qrels-final-trials.txt'), 'r') as gt:
        for line in gt:
            topic_id, _, doc_id, rel = line.strip().split(' ')
            rel = int(rel)
            topic_id = int(topic_id)
            if topic_id in gt_dict:
                if rel > 0:
                    ct += 1
                    print("processing {}/{} rel".format(doc_id, ct))
                    gt_dict[topic_id].append(doc_id)
                    extract_data = xml_extract(doc_id)
                    count_tf(group_id, extract_data, idx_dict[topic_id], True)
                else:
                    if unrel_ct_dict[topic_id] < 30:
                        unrel_ct_dict[topic_id] += 1
                        ct += 1
                        print("processing {}/{} unrel".format(doc_id, ct))
                        gt_dict[topic_id].append(doc_id)
                        extract_data = xml_extract(doc_id)
                        count_tf(group_id, extract_data, idx_dict[topic_id], False)

    print("ct is {}".format(ct))


def xml_extract(doc_id):
    """extract some fields of xml data and return extracted_data"""

    file_path = data_root + "/clinicaltrials_xml/*/*/{}.xml".format(doc_id)
    file_list = glob.glob(file_path)
    if len(file_list) != 1:
        raise Exception("Length is not 1!")

    # create xml tree
    tree = ET.parse(file_list[0])
    root = tree.getroot()
    extracted_data = collections.OrderedDict()

    # brief_title
    try:
        brief_title = root.find('brief_title').text
        extracted_data['brief_title'] = brief_title
    except:
        extracted_data['brief_title'] = None

    # brief_summary
    try:
        brief_summary = root.find('brief_summary').find('textblock').text
        extracted_data['brief_summary'] = brief_summary
    except:
        extracted_data['brief_sumamry'] = None

    # detailed_description
    try:
        detailed_description = root.find('detailed_description').find('textblock').text
        extracted_data['detailed_description'] = detailed_description
    except:
        extracted_data['detailed_description'] = None

    # eligibility
    try:
        eligibility = root.find('eligibility').find('criteria').find('textblock').text
        extracted_data['eligibility'] = eligibility
    except:
        extracted_data['eligibility'] = None

    # keyword
    keyword_str = ""
    try:
        keyword = root.findall('keyword')
        for index, item in enumerate(keyword):
            keyword_str += item.text
        extracted_data['keyword'] = keyword_str
    except:
        extracted_data['keyword'] = None

    # meshterm
    mesh_term_str = ""
    try:
        mesh_term = root.find('condition_browse').findall('mesh_term')
        for index, item in enumerate(mesh_term):
            mesh_term_str += item.text
            mesh_term_str += " "
        extracted_data['mesh_term'] = mesh_term_str
    except:
        extracted_data['mesh_term'] = None

    # print(extracted_data)
    return extracted_data

def range_count(group_id, df_dict, tf_dict, df_un_dict, tf_un_dict):
    """This function is to filter words with its tf and idf"""
    # count df_dict > 200
    df_tf_dict = dict()
    df_tf_un_dict = dict()

    f = open(cache_root + "/cache{}/keyword.txt".format(str(group_id+1)), "w")

    # related docs
    ct = 0
    # f.write("df > 300 : \n")
    for key, value in df_dict.items():
        if value > 300:
            # print(key, value)
            # f.write("{}, {}\n".format(key, value))
            ct += 1
    print("df > 300 : ", ct)
    # f.write("------------------------------------------------------\n")

    ct = 0
    # f.write("tf > 50:\n")
    tf_50 = dict()

    for key, value in tf_dict.items():
        flag = 0
        for v in value:
            if v > 30:
                flag += 1
        if flag > 12:
            ct += 1
            # f.write("{}, {}\n".format(key, value))
            tf_50[key] = value

    print("tf > 50 : ", ct)
    # f.write("-------------------------------------------------------\n")

    # f.write("tf > 100 and df > 200:\n")
    ct = 0
    for key, value in tf_50.items():
        if (key in df_dict) and (df_dict[key] > 300):
            # f.write("{} \t {}, df : {}\n".format(key, value, df_dict[key]))
            df_tf_dict[key] = [value, df_dict[key]]
            ct += 1

    print("tf_df : ", ct)
    # f.write("--------------------------------------------------------\n")

    # unrelated docs
    ct = 0
    # f.write("df_un > 300 : \n")
    for key, value in df_un_dict.items():
        if value > 300:
            # print(key, value)
            # f.write("{}, {}\n".format(key, value))
            ct += 1
    print("df_un > 300 : ", ct)
    # f.write("------------------------------------------------------\n")

    ct = 0
    tf_un_50 = dict()
    # f.write("tf_un > 50:\n")
    for key, value in tf_un_dict.items():
        flag = 0
        for v in value:
            if v > 30:
                flag += 1
        if flag > 12:
            # f.write("{}, {}\n".format(key, value))
            ct += 1
            tf_un_50[key] = value
    print("tf_un > 50 : ", ct)
    # f.write("-------------------------------------------------------\n")

    # f.write("tf_un > 50 and df_un > 300:\n")
    ct = 0
    for key, value in tf_un_50.items():
        if (key in df_un_dict) and (df_un_dict[key] > 100):
            # f.write("{} \t {}, df : {}\n".format(key, value, df_un_dict[key]))
            ct += 1
            df_tf_un_dict[key] = [value, df_un_dict[key]]

    print("tf_df_un : ", ct)
    # f.write("--------------------------------------------------------\n")

    # words with high frequency in related docs and low frequency in unrelated docs
    ct = 0
    # f.write("rel - unrel\n")
    for key, value in df_tf_dict.items():
        if key not in df_tf_un_dict:
            ct += 1
            f.write("{}\n".format(key))
    print("rel - unrel : ", ct)
    # f.write("-------------------------------------------------------\n")
    f.close()

def group_process(group_id):
    if not os.path.exists(cache_root + "/cache{}/all_tf.txt".format(str(group_id+1))):
        extract_doc(group_id)
        # print(all_tf[group_id].keys())
        print("------------------------")
        # print(all_df.keys())
        tf_file = open(cache_root + "/cache{}/all_tf.txt".format(str(group_id+1)), "wb")
        df_file = open(cache_root + "/cache{}/all_df.txt".format(str(group_id+1)), "wb")
        tf_un_file = open(cache_root + "/cache{}/all_tf_un.txt".format(str(group_id+1)), "wb")
        df_un_file = open(cache_root + "/cache{}/all_df_un.txt".format(str(group_id+1)), "wb")
        pickle.dump(all_tf[group_id], tf_file)
        pickle.dump(all_df[group_id], df_file)
        pickle.dump(all_tf_un[group_id], tf_un_file)
        pickle.dump(all_df_un[group_id], df_un_file)
        tf_file.close()
        df_file.close()
        range_count(group_id, all_df[group_id], all_tf[group_id], all_df_un[group_id], all_tf_un[group_id])
    else:
        tf_file = open(cache_root + "/cache{}/all_tf.txt".format(str(group_id+1)), "rb")
        df_file = open(cache_root + "/cache{}/all_df.txt".format(str(group_id+1)), "rb")
        tf_un_file = open(cache_root + "/cache{}/all_tf_un.txt".format(str(group_id+1)), "rb")
        df_un_file = open(cache_root + "/cache{}/all_df_un.txt".format(str(group_id+1)), "rb")
        tf_dict = pickle.load(tf_file)
        df_dict = pickle.load(df_file)
        tf_un_dict = pickle.load(tf_un_file)
        df_un_dict = pickle.load(df_un_file)
        range_count(group_id, df_dict, tf_dict, df_un_dict, tf_un_dict)
        tf_file.close()
        df_file.close()

def main():
    # Note the start time
    start_time = time.time()
    print("Counting tf and idf")
    for i in range(5):
        print("counting {}th group".format(i))
        group_process(i)

    print("\nExecution time: %.2f seconds" % (time.time() - start_time))

if __name__ == "__main__":
    main()



