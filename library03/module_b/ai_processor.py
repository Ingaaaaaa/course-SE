# module_b/ai_processor.py
import sys
import requests
import json
from pathlib import Path
from config import LLM_API_URL, LLM_API_KEY, LLM_TIMEOUT, AI_SYSTEM_PROMPT, B_TO_C_JSON_TPL, LLM_MODEL_NAME


def process_text(raw_data: dict) -> dict:
    """
    接收A模块清洗后的字典，调用大模型API处理文本，返回标准结构化字典
    :param raw_data: dict 模块A输出的 {task_id, clean_text} 字典
    :return: dict 符合 B_TO_C_JSON_TPL 规范的结构化字典
    :raises Exception: 网络异常、API请求失败、返回格式错误、解析失败
    """
    if not isinstance(raw_data, dict) or "task_id" not in raw_data or "clean_text" not in raw_data:
        raise Exception("上游数据格式错误，缺少 task_id 或 clean_text 字段")

    task_id = raw_data.get("task_id", "")
    clean_text = raw_data.get("clean_text", "")

    if not clean_text.strip():
        result = B_TO_C_JSON_TPL.copy()
        result["task_id"] = task_id
        return result

    request_body = {
        "model": LLM_MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": AI_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": clean_text
            }
        ],
        "temperature": 0
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}"
    }

    try:
        response = requests.post(
            url=LLM_API_URL,
            headers=headers,
            data=json.dumps(request_body, ensure_ascii=False).encode("utf-8"),
            timeout=LLM_TIMEOUT
        )
    except requests.exceptions.Timeout:
        raise Exception(f"API请求超时，超时时间：{LLM_TIMEOUT}秒")
    except requests.exceptions.ConnectionError:
        raise Exception("无法连接大模型API，请检查接口地址与网络")
    except Exception as e:
        raise Exception(f"网络请求异常：{str(e)}")

    if response.status_code != 200:
        raise Exception(f"API请求失败，状态码：{response.status_code}，响应内容：{response.text}")

    try:
        api_res = response.json()
    except json.JSONDecodeError:
        raise Exception("大模型返回内容非标准JSON格式")

    try:
        model_output = api_res["choices"][0]["message"]["content"]
        print("====AI原始返回内容====")
        print(model_output)
        print("======================")
    except (KeyError, IndexError):
        raise Exception("解析大模型返回结果失败，返回结构不匹配")

    try:
        structured_data = json.loads(model_output.strip())
    except json.JSONDecodeError as e:
        start_idx = model_output.find('[')
        end_idx = model_output.rfind(']') + 1
        if start_idx >= 0 and end_idx > start_idx:
            try:
                structured_data = json.loads(model_output[start_idx:end_idx])
            except:
                raise Exception(f"AI返回内容无法解析为JSON，报错信息：{str(e)}，AI原始输出：{model_output}")
        else:
            raise Exception(f"AI返回内容无法解析为JSON，报错信息：{str(e)}，AI原始输出：{model_output}")

    return _convert_to_b_to_c_format(structured_data, task_id)


def _convert_to_b_to_c_format(segments: list, task_id: str) -> dict:
    """
    将新的段落数组格式转换为B_TO_C_JSON_TPL格式
    :param segments: AI返回的段落数组
    :param task_id: 任务ID
    :return: 符合B_TO_C_JSON_TPL规范的结构化字典
    """
    final_data = B_TO_C_JSON_TPL.copy()
    final_data["task_id"] = task_id

    paper_title = ""
    author = ""
    sub_title_list = []
    content_flow = []
    ref_list = []
    ref_index = 1

    if isinstance(segments, list):
        for seg in segments:
            if not isinstance(seg, dict):
                continue
            
            seg_type = seg.get("segment_type", "").strip()
            seg_text = seg.get("text", "").strip()
            
            if not seg_text:
                continue

            if seg_type == "标题" and not paper_title:
                paper_title = seg_text
                content_flow.append({"type": "title", "content": seg_text})
            elif seg_type == "作者" and not author:
                author = seg_text
            elif seg_type in ["一级标题", "二级标题"]:
                clean_title = seg_text
                num_end = 0
                while num_end < len(clean_title) and (clean_title[num_end].isdigit() or clean_title[num_end] in " ."):
                    num_end += 1
                clean_title = clean_title[num_end:].strip()
                
                if clean_title:
                    sub_title_list.append({"title_content": clean_title})
                    content_flow.append({"type": "title", "content": seg_text})
            elif seg_type == "正文段落":
                content_flow.append({"type": "paragraph", "content": seg_text})
            elif seg_type == "参考文献":
                ref_list.append({
                    "index": ref_index,
                    "type": "期刊",
                    "content": seg_text
                })
                ref_index += 1
            elif seg_type in ["摘要", "关键词", "图注", "表注"]:
                content_flow.append({"type": "paragraph", "content": seg_text})

    final_data["paper_title"] = paper_title
    final_data["author"] = author
    final_data["sub_title_list"] = sub_title_list
    final_data["content_flow"] = content_flow
    final_data["ref_list"] = ref_list

    return final_data


if __name__ == "__main__":
    mock_a_data = {
        "task_id": "test_001",
        "clean_text": "人工智能在教育领域的应用研究\n李华\n摘要：随着人工智能技术的发展，教育领域发生了深刻变革。\n关键词：人工智能；教育应用；智能化\n1 相关研究现状\n随着人工智能技术飞速发展，文本分类在信息检索、内容审核等场景得到广泛应用[1]。传统分类方法依赖人工特征工程，效率较低。\n1.1 研究背景\n近年来，深度学习技术取得显著进展。\n2 算法设计\n本文提出一种改进特征提取算法，实验结果表明准确率提升12.3%[2]。\n参考文献\n[1] 张三. 机器学习入门[M]. 北京: 清华大学出版社, 2023.\n[2] 李四. 深度学习应用[J]. 计算机学报, 2024, 40(1): 50-60."
    }
    try:
        res = process_text(mock_a_data)
        print("=== B模块输出结果 ===")
        print(json.dumps(res, ensure_ascii=False, indent=2))
    except Exception as e:
        print("测试报错：", e)
