import os

# SQLite版本兼容性修复 - 必须在导入chromadb之前
try:
    import pysqlite3
    import sys
    sys.modules['sqlite3'] = pysqlite3
except ImportError:
    pass

# 上层 API
from langchain_chroma import Chroma
from langchain_community.document_compressors import DashScopeRerank
from langchain_community.embeddings import DashScopeEmbeddings
from utils.logger import Logger

# 初始化日志记录器
logger = Logger("tools")

# 项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
# prompt文件路径
prompt_root = os.path.join(project_root, 'data/Prompt')
chromadb_path = os.path.join(project_root, 'data/chroma_data')
# logger.debug(f'chromadb_path: {chromadb_path}')

import json
import os


def load_info(info_type, json_file='config.json'):
    """从JSON文件中加载指定的模型信息。
    Args:
        info_type (str): 信息类型，如 'models' 或 'keys'。
        json_file (str): 包含信息的JSON文件路径。
    Returns:
        str: 加载的信息值。
    """
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, json_file)
    # 读取配置文件
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        config = {}

    return config[info_type]


# 读取prompt文件
def read_prompt_file(dept):
    """
        读取prompt文件
        dept: 科室名称
        return: prompt内容
    """
    with open(os.path.join(prompt_root, f"{dept}.md"), "r") as file:
        return file.read()


# 收集文档
def collect_documents(segments):
    """
        收集文档
        segments: 文档列表
        return: 文档内容
    """
    text = []
    for segment in segments:
        text.append(segment.page_content)
    return text


def get_context_from_db(query="你好吗？",
                        num_recall=5,
                        score_threshold=0.5):
    """
        根据query，检索相关的上下文
        query: 查询问题
        num_recall: 召回的文档数量
        score_threshold: 召回的文档分数阈值
        return: 相关的上下文
    """

    os.environ["DASHSCOPE_API_KEY"] = load_info("keys")["DASHSCOPE_API_KEY"]
    rerank = DashScopeRerank(model="text-embedding-v3", top_n=4)  # 连接
    
    # 连接向量化模型
    embed = DashScopeEmbeddings(model='text-embedding-v3')

    # collection - 使用本地持久化存储，不需要 HttpClient
    # db1 = Chroma(collection_name="db1", embedding_function=embed, persist_directory=chromadb_path)
    db2 = Chroma(collection_name="db2", embedding_function=embed, persist_directory=chromadb_path)
    db3 = Chroma(collection_name="db3", embedding_function=embed, persist_directory=chromadb_path)
    db4 = Chroma(collection_name="db4", embedding_function=embed, persist_directory=chromadb_path)

    # 1，先做召回

    recall_results = []

    # 第1路召回
    # results1 = db1.similarity_search_with_relevance_scores(query=query, k=num_recall)
    #
    # # 第1路筛选
    # for doc, score in results1:
    #     if score > score_threshold:
    #         # 执行 metadata 的校验
    #         recall_results.append(doc.page_content)
    #     else:
    #         break

    # 第 2 路召回
    results2 = db2.similarity_search_with_relevance_scores(query=query, k=num_recall)
    # 第 2 路筛选
    for doc, score in results2:
        if score > score_threshold:
            # 执行 metadata 的校验
            recall_results.append(doc.page_content)
        else:
            break

    # 第 3 路召回
    results3 = db3.similarity_search_with_relevance_scores(query=query, k=num_recall)
    # 第 3 路筛选
    for doc, score in results3:
        if score > score_threshold:
            # 执行 metadata 的校验
            recall_results.append(doc.page_content)
        else:
            break

    # 第 4 路召回
    results4 = db4.similarity_search_with_relevance_scores(query=query, k=num_recall)
    # 第 4 路筛选
    for doc, score in results4:
        if score > score_threshold:
            # 执行 metadata 的校验
            recall_results.append(f"{doc.page_content} ")
        else:
            break

    logger.debug(f"召回结果数量", {"count": len(recall_results)})

    # 2，重排序

    # 拿着 问题 跟多有结果进行 二次 计算相似度
    # 重排序模型会更精准的计算分数
    rerank_results = rerank.rerank(documents=recall_results, query=query)
    final_results = []
    for idx, result in enumerate(rerank_results):
        # logger.debug(f"重排序结果", {"index": idx, "content": recall_results[result["index"]], "score": result["relevance_score"]})
        final_results.append(recall_results[result["index"]] + "\n\n")

    return final_results


if __name__ == "__main__":
    query = "小儿急性支气管炎"
    logger.info(f"测试查询", {"query": query})
    logger.debug("分隔线", {"line": "*" * 100})
    context = get_context_from_db(query)
    logger.info(f"查询结果", {"context": context})
