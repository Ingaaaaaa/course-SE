# module_a/ui_doc_handler.py
from docx import Document
import time
import re


def read_and_clean_doc(file_path: str) -> dict:
    """
    读取docx文档 + 基础文本清洗
    :param file_path: str  本地Word文档绝对路径
    :return: dict  固定A→B字典结构 {task_id, clean_text}
    :raises Exception: 文件不存在、非docx、空文档等异常
    """
    # 1. 生成唯一任务ID（使用时间戳）
    task_id = str(int(time.time()))

    # 2. 读取docx文档
    try:
        doc = Document(file_path)
    except Exception:
        raise Exception("文件不存在、文件损坏或不是docx格式，请检查文件路径与格式")

    # 3. 提取文档所有文本
    full_text = []
    for para in doc.paragraphs:
        para_text = para.text.strip()
        if para_text:
            full_text.append(para_text)
    raw_content = "\n".join(full_text)

    # 校验：文档无有效内容
    if not raw_content:
        raise Exception("文档内容为空，无需处理")

    # 4. 基础文本清洗（按需求：去多余空格、空行、外链、广告、无效符号）
    # 去除网址链接
    content = re.sub(r"http[s]?://\S+", "", raw_content)
    # 去除连续多个空格、制表符
    content = re.sub(r"\s+", " ", content)
    # 去除首尾空格
    content = content.strip()
    # 去除常见广告类无关字符（可按需扩展）
    content = re.sub(r"点击查看|阅读原文|广告|下载", "", content)

    # 5. 组装约定格式字典（A→B 标准结构，严禁增删字段）
    result = {
        "task_id": task_id,
        "clean_text": content
    }

    return result


# 本地自测入口（仅自己测试使用，不影响主程序）
if __name__ == "__main__":
    # 替换为你本地 test_file 下的测试docx路径
    test_file_path = r"./test_file/测试文档.docx"
    try:
        data = read_and_clean_doc(test_file_path)
        print("===== A模块输出结果 =====")
        print(f"task_id: {data['task_id']}")
        print(f"clean_text:\n{data['clean_text']}")
    except Exception as e:
        print("运行出错：", e)