# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import threading
import time

from definitions import OUTPUT_DIR, DATA_DIR
from migration.calculator.base import CombineSimResultCollection, MultiCombineSimResultCollection
from migration.converter.filter import NodeFilter
from migration.evaluate.base import SimEvaluator
from migration.evaluate.dataset import DataSet
from migration.rapim.model import TfIdfModel
from migration.rapim.sentence_pipeline import SentencePipeline
from migration.rapim.pipeline import RApiM
from migration.util.db_util import DBUtil
from migration.util.file_util import FileUtil
from migration.util.milvus_util import MilvusUtil
from migration.util.path_util import PathUtil


# test/big + /transE/rank + /icpc_saner/segicpc +  /single  +retrieve/rarank + method/class + /filter + model/evaluate/export_result

type = "big"
filter = "_filter"



def gene_temp_data(index, start, end):
    library_method_dic = FileUtil.load_data_list(os.path.join(DATA_DIR, "icpc_saner", "all_library_method_dic_{}.json".format(type)))
    pipe = SentencePipeline()
    tfidf = TfIdfModel(pipe)
    tfidf.load_model_and_dictionary("tfidf_{}".format(type), "token2id_{}.txt".format(type))
    if type == "big":
        graph_util = DBUtil.get_large_api_kg_util()
        graph = DBUtil.get_large_api_kg()
    else:
        graph_util = DBUtil.get_test_api_kg_util()
        graph = DBUtil.get_test_api_kg()
    if filter == "":
        library_method_info_dic = None
    else:
        library_method_info_dic = FileUtil.load_data_list(os.path.join(DATA_DIR, "icpc_saner", "all_library_method_info_dic_{}.json".format(type)))
    migration = RApiM(library_method_dic, tfidf, graph, graph_util, NodeFilter(graph_util), library_method_info_dic)
    top_n = 100
    csv_path = os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}.csv'.format(type))
    dataset = DataSet(data_type="method")
    dataset.load_from_csv(csv_path)
    count = 0
    mcsrc = MultiCombineSimResultCollection()
    for ind, query_pair in enumerate(dataset.query_data):
        if ind < start or ind > end:
            continue
        temp_query_pair = [
            {"query_id": int(query_pair[dataset.position_a]), "target_id": int(query_pair[dataset.position_b])},
            {"query_id": int(query_pair[dataset.position_b]), "target_id": int(query_pair[dataset.position_a])}]
        for t in temp_query_pair:

            count = count + 1
            print("thread", index, "process ", count, str(t["query_id"]) + "_" + str(t["target_id"]))
            if filter == "":
                re: CombineSimResultCollection = migration.run(start_api_id=t["query_id"], rerank_topN=top_n, type=type)
            else:
                re: CombineSimResultCollection = migration.run(start_api_id=t["query_id"], target_api_id=t["target_id"], rerank_topN=top_n, type=type)

            mcsrc.add(str(t["query_id"]) + "_" + str(t["target_id"]), re)
    mcsrc.save(PathUtil.temp_multi_combine_sim_collection("{}_icpc_rerank_method{}_model_{}".format(type, filter, str(index))))

def merge(thread_num):
    rerank_result = None
    for index in range(thread_num):
        if rerank_result is None:
            rerank_result: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.temp_multi_combine_sim_collection("{}_icpc_rerank_method{}_model_{}".format(type, filter, str(index + 1))))

        else:
            rerank: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.temp_multi_combine_sim_collection("{}_icpc_rerank_method{}_model_{}".format(type, filter, str(index + 1))))
            id2csrc = rerank.id2name2sim_collection
            rerank_result.id2name2sim_collection.update(id2csrc)

    rerank_result.save(PathUtil.multi_combine_sim_collection("{}_icpc_rerank_method{}_model".format(type, filter)))
    print("save {}_icpc_rerank_method{}_model success".format(type, filter))


if __name__ == '__main__':

    time1 = time.time()
    # 加载数据
    # csv_path = os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}.csv'.format(type))
    # dataset = DataSet("method")
    # dataset.load_from_csv(csv_path)
    # length = len(dataset.query_data)
    # batch_size = 500
    # batch_num = length // batch_size
    # if length % batch_size != 0:
    #     batch_num = batch_num + 1
    # threads = []
    # for index in range(batch_num):
    #     start = index * batch_size
    #     end = (index + 1) * batch_size
    #
    #     threads.append(threading.Thread(
    #         target=gene_temp_data,
    #         args=(index + 1, start, end)
    #     ))
    # for index, t in enumerate(threads):
    #     t.start()
    #     print("start thread", index)
    #     time.sleep(10)
    #
    # for t in threads:
    #     t.join()
    # merge(batch_num)
    time2 = time.time()
    '''
    ==============================================================================================================
    ==============================================================================================================
    '''
    # top_n = 200
    # top_n_list = [1, 3, 5, 10, 20, 30, 50, 100, 200, 300, 500]
    # se = SimEvaluator(top_n)
    # csv_path = os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}.csv'.format(type))
    # dataset = DataSet("method")
    # dataset.load_from_csv(csv_path)
    #
    #
    # mcsrc: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.multi_combine_sim_collection("{}_icpc_rerank_method{}_model".format(type, filter)))
    # se.evaluate(dataset=dataset, top_n_list=top_n_list, multi_combine_sim_result_collection=mcsrc, combine_sim_result_collection_type="rerank", msimcol_name="{}_icpc_rerank_method{}_model".format(type, filter))
    # re = [se.eval_result]
    # FileUtil.write2json(os.path.join(OUTPUT_DIR, "evaluate", "{}_icpc_method{}_evaluate.json".format(type, filter)), re)
    # print("write {}_icpc_method{}_evaluate success".format(type, filter))
    time3 = time.time()



    '''
    ==============================================================================================================
    ==============================================================================================================
    '''
    top_n = 300
    namew2weight = {"model": 1}

    csv_path = os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}.csv'.format(type))
    dataset = DataSet("method")
    dataset.load_from_csv(csv_path)
    milvus = DBUtil.get_milvus()
    if type == "test":
        graph_util = DBUtil.get_test_api_kg_util()
    else:
        graph_util = DBUtil.get_large_api_kg_util()
    milvus_util = MilvusUtil(milvus)

    rerank_combine_sim_collection: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.multi_combine_sim_collection("{}_icpc_rerank_method{}_model".format(type, filter)))

    result_list = []
    count = 0
    err_count = 0
    for query_pair in dataset.query_data:
        temp_query_pair = [
            {"query_id": int(query_pair[dataset.position_a]), "target_id": int(query_pair[dataset.position_b])},
            {"query_id": int(query_pair[dataset.position_b]), "target_id": int(query_pair[dataset.position_a])}
        ]
        for t in temp_query_pair:
            result = {"top_n": top_n}
            result["start_node_info"] = graph_util.get_node_by_id(t["query_id"])
            result["position"] = -1
            try:
                combine_results = rerank_combine_sim_collection.id2name2sim_collection[
                    str(t["query_id"]) + "_" + str(t["target_id"])].get_combine_sim_result(name2weight=namew2weight)
                result["combine_results"] = []
                for inde, te in enumerate(combine_results[:result["top_n"]]):
                    combine_result = {
                        "node_info": graph_util.get_node_by_id(te.end_id),
                        "score": te.score,
                        "extra": te.extra
                    }
                    result["combine_results"].append(combine_result)
                    if te.end_id == t["target_id"]:
                        result["position"] = inde
                count = count + 1
                err_count = err_count + 1
                print("process: ", count)
                result_list.append(result)
            except BaseException as e:
                print("error count: ", err_count, e)

    FileUtil.write2json(
        os.path.join(OUTPUT_DIR, "export_result", "{}_icpc_rerank_method{}_export_result.json".format(type, filter)),
        result_list)
    print("write ", "{}_icpc_rerank_method{}_export_result.json".format(type, filter), "success")
    print(time1)
    print(time2)
    print(time3)