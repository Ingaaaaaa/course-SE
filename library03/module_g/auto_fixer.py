# module_g/auto_fixer.py
import requests
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import LLM_API_URL, LLM_API_KEY, LLM_TIMEOUT, LLM_MODEL_NAME


FIX_PROMPT = """
你是学术论文专业润色改写专家，根据提供的原文与全部错误修正清单，精准修改所有标记问题，保留原文研究内容、章节结构、实验数据不变，不删减核心观点，全文统一学术书面表达。

【执行规则】
1. 严格按照下方错误清单逐条修正，每一处错误都必须替换为优化建议内的规范表述；
2. 统一全文数字、标点、术语规范，删除口语化、主观化语句；
3. 参考文献补齐缺失规范信息，正文引用标注与参考文献一一对应；
4. 不新增无关内容、不篡改实验数据、不调整原有段落顺序；
5. 最终只输出完整改写后的纯论文文本，无任何说明、对比、注释。

【传入数据】
1. 原始论文全文：
{original_text}

2. 错误修正清单（JSON数组）：
{error_list}

【输出要求】
仅输出改写完成后的完整论文正文，不要额外文字。
"""


class AutoFixer:
    """一键AI自动修正器：修正论文错误并重新排版"""

    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}"
        }

    def fix_paragraph(self, original_text: str, errors: list) -> str:
        """
        修正单个段落
        :param original_text: 原始段落文本
        :param errors: 该段落的错误列表（F模块新结构）
        :return: 修正后的文本
        """
        if not errors:
            return original_text

        error_json = json.dumps(errors, ensure_ascii=False, indent=2)

        prompt = FIX_PROMPT.format(
            original_text=original_text,
            error_list=error_json
        )

        try:
            return self._call_ai(prompt)
        except Exception as e:
            print(f"段落修正失败：{str(e)}")
            return original_text

    def fix_all(self, errors: list, content_flow: list = None) -> dict:
        """
        修正所有错误
        :param errors: F模块输出的错误JSON数组（新结构）
        :param content_flow: B模块输出的内容流（可选，用于保持顺序）
        :return: 包含修正结果的字典
        """
        if content_flow:
            return self._fix_with_flow(errors, content_flow)
        else:
            return self._fix_simple(errors)

    def _fix_with_flow(self, errors: list, content_flow: list) -> dict:
        """使用content_flow修正（保持标题和段落顺序）"""
        errors_by_para = {}
        for err in errors:
            para_idx = err.get("segment_index", 0) - 1
            if para_idx not in errors_by_para:
                errors_by_para[para_idx] = []
            errors_by_para[para_idx].append(err)

        corrected_flow = []
        para_idx = 0

        for item in content_flow:
            item_type = item.get("type", "")
            item_content = item.get("content", "")

            if item_type == "title":
                corrected_flow.append({
                    "type": "title",
                    "content": item_content,
                    "corrected": False
                })
            elif item_type == "paragraph":
                para_errors = errors_by_para.get(para_idx, [])
                if para_errors:
                    corrected_content = self.fix_paragraph(item_content, para_errors)
                    corrected_flow.append({
                        "type": "paragraph",
                        "content": corrected_content,
                        "original": item_content,
                        "corrected": True,
                        "errors": para_errors
                    })
                else:
                    corrected_flow.append({
                        "type": "paragraph",
                        "content": item_content,
                        "corrected": False
                    })
                para_idx += 1

        return {
            "corrected_flow": corrected_flow,
            "total_fixed": sum(1 for item in corrected_flow if item.get("corrected")),
            "errors": errors
        }

    def _fix_simple(self, errors: list) -> dict:
        """简单修正（仅修正段落内容）"""
        corrected_paragraphs = []
        all_errors = []

        errors_by_para = {}
        for err in errors:
            para_idx = err.get("segment_index", 0) - 1
            if para_idx not in errors_by_para:
                errors_by_para[para_idx] = []
            errors_by_para[para_idx].append(err)

        for para_idx, para_errors in errors_by_para.items():
            original_text = para_errors[0].get("raw_text", "") if para_errors else ""
            
            if para_errors:
                corrected_text = self.fix_paragraph(original_text, para_errors)
                corrected_paragraphs.append({
                    "index": para_idx,
                    "original": original_text,
                    "corrected": corrected_text,
                    "errors": para_errors
                })
                all_errors.extend(para_errors)
            else:
                corrected_paragraphs.append({
                    "index": para_idx,
                    "original": original_text,
                    "corrected": original_text,
                    "errors": []
                })

        return {
            "corrected_paragraphs": corrected_paragraphs,
            "total_fixed": len([p for p in corrected_paragraphs if p["corrected"] != p["original"]]),
            "errors": all_errors
        }

    def _call_ai(self, prompt: str) -> str:
        """调用AI进行修正"""
        request_body = {
            "model": LLM_MODEL_NAME,
            "messages": [
                {"role": "system", "content": "你是学术论文专业润色改写专家，根据错误清单精准修改论文问题，只输出改写后的纯文本，禁止任何额外解释。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4000
        }

        response = requests.post(
            url=LLM_API_URL,
            headers=self.headers,
            data=json.dumps(request_body, ensure_ascii=False).encode("utf-8"),
            timeout=LLM_TIMEOUT
        )

        if response.status_code != 200:
            raise Exception(f"API请求失败，状态码：{response.status_code}")

        api_res = response.json()
        model_output = api_res["choices"][0]["message"]["content"]
        print("====AI修正结果====")
        print(model_output[:300] if len(model_output) > 300 else model_output)
        print("==================")

        return model_output.strip()

    def generate_fix_log(self, fix_result: dict) -> str:
        """生成修改日志"""
        lines = ["=" * 60, "论文AI修正日志", "=" * 60, ""]

        if "corrected_flow" in fix_result:
            lines.append(f"共修正 {fix_result.get('total_fixed', 0)} 处内容")
            lines.append("")
            lines.append("【修改详情】")

            for i, item in enumerate(fix_result.get("corrected_flow", [])):
                if item.get("corrected"):
                    lines.append(f"\n--- 第{i+1}处修改 ---")
                    lines.append(f"原文：{item.get('original', '')}")
                    lines.append(f"修正：{item.get('content', '')}")
                    errors = item.get("errors", [])
                    if errors:
                        lines.append(f"修改类型：{errors[0].get('error_type', '未知')}")

        elif "corrected_paragraphs" in fix_result:
            lines.append(f"共修正 {fix_result.get('total_fixed', 0)} 处内容")
            lines.append("")
            lines.append("【修改详情】")

            for para in fix_result.get("corrected_paragraphs", []):
                if para.get("corrected") != para.get("original"):
                    lines.append(f"\n--- 段落{para.get('index')} ---")
                    lines.append(f"原文：{para.get('original', '')}")
                    lines.append(f"修正：{para.get('corrected', '')}")

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)

    def rebuild_struct_data(self, fix_result: dict, original_struct: dict) -> dict:
        """重建结构化数据供C模块使用"""
        new_struct = original_struct.copy()

        if "corrected_flow" in fix_result:
            new_struct["content_flow"] = [
                {"type": item["type"], "content": item["content"]}
                for item in fix_result.get("corrected_flow", [])
                if item.get("content", "").strip()
            ]
        elif "corrected_paragraphs" in fix_result:
            new_struct["paragraph_list"] = [
                para["corrected"] for para in fix_result.get("corrected_paragraphs", [])
            ]

        return new_struct


# 模块测试
if __name__ == "__main__":
    fixer = AutoFixer()

    test_errors = [
        {
            "segment_index": 1,
            "error_start": "我认为",
            "error_end": "非常好用",
            "error_type": "学术层",
            "raw_text": "我认为这个技术非常好用",
            "error_desc": "学术论文禁止第一人称主观判断",
            "optimize_suggest": "该技术展现出显著的应用价值"
        }
    ]

    test_flow = [
        {"type": "title", "content": "人工智能在教育领域的应用"},
        {"type": "paragraph", "content": "人工智能技术在教育领域得到广泛应用。我认为这个技术非常好用。"}
    ]

    result = fixer.fix_all(test_errors, test_flow)
    print(f"修正结果：修正了 {result.get('total_fixed')} 处")

    log = fixer.generate_fix_log(result)
    print(log)
