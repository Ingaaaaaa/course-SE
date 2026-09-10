# module_f/academic_corrector.py
import requests
import json
import sys
import time
from pathlib import Path
from requests.exceptions import ReadTimeout, ConnectionError

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import LLM_API_URL, LLM_API_KEY, LLM_TIMEOUT, LLM_MODEL_NAME


CORRECTION_PROMPT_BASE = """
你是专业学术论文审校专家，严格按照三层检测标准逐段审核用户提供的论文文本，只识别真实存在的问题，不编造错误；最终只输出标准JSON，禁止任何多余解释、开场白、总结文字，不输出Markdown格式。

【三层检测判定标准（严格对照，每条匹配即生成一条错误记录）】

## 1. 基础层错误（勾选则检测，不勾选直接跳过）
1) 文字类：错别字、多字漏字、标点符号误用（中英文标点混用、逗号句号错用、顿号分号混乱）；
2) 语句类：语句不通顺、残缺句、重复冗余语句、口语化通俗短句；
3) 数字规范：学术文本数字混用汉字/阿拉伯数字（统计数据、实验数值必须阿拉伯数字）；
4) 格式细节：多余空格、无意义换行、特殊乱码符号。

## 2. 学术层错误（勾选则检测，不勾选直接跳过）
1) 主观表述：第一人称主观判断（我觉得、我认为、看上去、效果还行），论文禁止主观感性描述；
2) 术语不规范：行业术语错误、网络通俗词汇、非书面化表达（乱七八糟、很难用、挺不错）；
3) 引用缺陷：参考文献信息缺失（无卷期、页码、年份、期刊名）、正文引用上角标与参考文献不匹配；
4) 数据模糊：无量化描述（效果很好、误差不大、大部分样本），缺少具体数值支撑。

## 3. 深度学术层错误（勾选则检测，不勾选直接跳过）
1) 逻辑断层：段落论证无递进、前后观点矛盾、论据无法支撑结论；
2) 研究缺陷：缺少文献支撑、实验无对照组、未说明失败样本原因、无创新点阐述；
3) 结构缺失：章节逻辑混乱、缺少研究不足与展望、实验分析无归纳总结；
4) 学术严谨性：结论夸大、无依据推断、缺少统计学说明。

【输出强制约束（必须严格遵守，输出仅JSON，无任何额外文字）】

输出为JSON数组，数组内每一条错误对象固定字段：
[
    {
        "segment_index": 段落序号（从1开始计数）,
        "error_start": 错误起始文字（截取前后5字上下文定位）,
        "error_end": 错误结束文字,
        "error_type": 错误分类（只能填写：基础层/学术层/深度层）,
        "raw_text": 完整出错原句,
        "error_desc": 精准说明该句违反哪一条学术规范，不超过80字,
        "optimize_suggest": 给出可直接替换的标准学术改写句子
    }
]

若全文无任何匹配错误，输出空数组 []

【用户输入内容】
## 开启检测层级：{levels}
## 论文原文分段：
{content}
"""


class AcademicCorrector:
    """学术AI纠错标注器：检测论文错误并生成标记"""

    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}"
        }
        self.REQUEST_TIMEOUT = 90
        self.MAX_RETRY = 2

    def correct(self, content: str, check_levels: dict = None) -> list:
        """
        执行学术纠错（分段调用AI，解决长文本超时问题）
        :param content: 待检测文本（已分段的段落数组或纯文本）
        :param check_levels: 检测层次配置 {"basic": True, "academic": True, "deep": True}
        :return: 错误JSON数组
        """
        if check_levels is None:
            check_levels = {"basic": True, "academic": True, "deep": True}

        print(f"\n====学术纠错输入信息====")
        print(f"检测层次: {check_levels}")
        print(f"content类型: {type(content)}")
        
        paragraphs = []
        if isinstance(content, list):
            print(f"段落数量: {len(content)}")
            paragraphs = content
        else:
            text = str(content)
            print(f"文本总长度: {len(text)}")
            paragraphs = self._split_text_to_paragraphs(text)
        
        print(f"前200字符: {str(paragraphs[:2])[:200]}...")
        print(f"===========================\n")

        if not paragraphs:
            print("输入文本为空，返回空结果")
            return []

        levels_list = []
        if check_levels.get("basic"):
            levels_list.append("基础层")
        if check_levels.get("academic"):
            levels_list.append("学术层")
        if check_levels.get("deep"):
            levels_list.append("深度层")

        chunk_size = 5
        all_errors = []
        
        for i in range(0, len(paragraphs), chunk_size):
            chunk = paragraphs[i:i+chunk_size]
            start_idx = i + 1
            end_idx = min(i + chunk_size, len(paragraphs))
            
            print(f"\n====正在处理第 {start_idx}-{end_idx} 段====\n")
            
            text_chunk = "\n".join([f"段落{j+1}：{para}" for j, para in enumerate(chunk)])
            prompt = CORRECTION_PROMPT_BASE.replace("{levels}", str(levels_list)).replace("{content}", text_chunk)

            try:
                response = self._safe_call_ai(prompt)
                if response and isinstance(response, list):
                    validated = self._validate_and_filter(response, offset=i)
                    all_errors.extend(validated)
                    print(f"第 {start_idx}-{end_idx} 段检测完成，发现 {len(validated)} 处错误")
                else:
                    print(f"第 {start_idx}-{end_idx} 段AI返回为空或非列表格式")
            except Exception as e:
                print(f"第 {start_idx}-{end_idx} 段检测失败：{str(e)}")

        print(f"\n====学术纠错结果统计====")
        print(f"总错误数: {len(all_errors)}")
        print(f"===========================\n")
        
        return all_errors

    def _split_text_to_paragraphs(self, text: str) -> list:
        """将纯文本按段落分割"""
        paragraphs = []
        for line in text.split('\n'):
            line = line.strip()
            if line:
                paragraphs.append(line)
        return paragraphs

    def _safe_call_ai(self, prompt: str) -> list:
        """安全调用AI，包含超时重试机制"""
        for attempt in range(self.MAX_RETRY + 1):
            try:
                return self._call_ai(prompt, attempt + 1)
            except ReadTimeout:
                if attempt < self.MAX_RETRY:
                    print(f"第{attempt+1}次请求超时，正在进行第{attempt+2}次重试...")
                    time.sleep(2)
                else:
                    raise Exception(f"接口请求超时，已重试{self.MAX_RETRY}次，请检查网络或缩短检测文本长度")
            except ConnectionError as e:
                if attempt < self.MAX_RETRY:
                    print(f"第{attempt+1}次请求连接失败，正在进行第{attempt+2}次重试...")
                    time.sleep(3)
                else:
                    raise Exception(f"网络连接失败，已重试{self.MAX_RETRY}次：{str(e)}")

    def _call_ai(self, prompt: str, attempt: int = 1) -> list:
        """调用AI进行纠错"""
        request_body = {
            "model": LLM_MODEL_NAME,
            "messages": [
                {"role": "system", "content": "你是专业学术论文审稿专家，严格按照三层检测标准逐段审核论文文本，只输出标准JSON数组，禁止任何多余文字。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4000
        }

        print(f"\n====学术纠错AI请求信息（第{attempt}次）====")
        print(f"模型: {LLM_MODEL_NAME}")
        print(f"prompt长度: {len(prompt)}")
        print(f"超时时间: {self.REQUEST_TIMEOUT}秒")
        print(f"===========================\n")

        response = requests.post(
            url=LLM_API_URL,
            headers=self.headers,
            data=json.dumps(request_body, ensure_ascii=False).encode("utf-8"),
            timeout=self.REQUEST_TIMEOUT
        )

        if response.status_code != 200:
            raise Exception(f"API请求失败，状态码：{response.status_code}，响应：{response.text}")

        api_res = response.json()
        model_output = api_res["choices"][0]["message"]["content"]
        
        print("\n====学术纠错AI返回内容====")
        print(f"返回内容长度: {len(model_output)}")
        print(f"完整返回内容:\n{model_output}")
        print("===========================\n")

        try:
            return json.loads(model_output.strip())
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {str(e)}")
            print("尝试提取JSON部分...")
            start_idx = model_output.find('[')
            end_idx = model_output.rfind(']') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = model_output[start_idx:end_idx]
                print(f"提取的JSON: {json_str}")
                return json.loads(json_str)
            raise

    def _validate_and_filter(self, errors: list, offset: int = 0) -> list:
        """验证和过滤错误数据，修正段落序号偏移"""
        validated = []
        for err in errors:
            if not isinstance(err, dict):
                continue
            
            if not err.get("raw_text", "").strip():
                continue
            
            seg_idx = err.get("segment_index", 0)
            if seg_idx > 0:
                seg_idx += offset
            
            validated.append({
                "segment_index": seg_idx,
                "error_start": err.get("error_start", ""),
                "error_end": err.get("error_end", ""),
                "error_type": err.get("error_type", "未知"),
                "raw_text": err.get("raw_text", ""),
                "error_desc": err.get("error_desc", ""),
                "optimize_suggest": err.get("optimize_suggest", "")
            })

        return validated

    def correct_structured_data(self, struct_data: dict, check_levels: dict = None) -> list:
        """
        纠错已结构化的论文数据
        :param struct_data: B模块输出的结构化字典
        :param check_levels: 检测层次配置
        :return: 错误JSON数组
        """
        content_flow = struct_data.get("content_flow", [])
        if not content_flow:
            paragraphs = struct_data.get("paragraph_list", [])
        else:
            paragraphs = [
                item["content"] for item in content_flow
                if item.get("type") == "paragraph" and item.get("content", "").strip()
            ]

        return self.correct(paragraphs, check_levels)

    def get_error_summary(self, errors: list) -> dict:
        """生成错误汇总统计"""
        summary = {
            "总错误数": len(errors),
            "按类型统计": {},
            "按段落分布": {}
        }

        for err in errors:
            err_type = err.get("error_type", "未知")
            seg_idx = err.get("segment_index", 0)
            
            if err_type not in summary["按类型统计"]:
                summary["按类型统计"][err_type] = 0
            summary["按类型统计"][err_type] += 1
            
            if seg_idx not in summary["按段落分布"]:
                summary["按段落分布"][f"段落{seg_idx}"] = 0
            summary["按段落分布"][f"段落{seg_idx}"] += 1

        return summary

    def generate_error_report(self, errors: list, struct_data: dict = None) -> str:
        """生成错误报告"""
        lines = ["=" * 50, "论文错误检测报告", "=" * 50, ""]

        summary = self.get_error_summary(errors)
        lines.append(f"【统计汇总】")
        lines.append(f"  总错误数：{summary['总错误数']}")
        lines.append(f"  错误类型分布：")
        for err_type, count in summary["按类型统计"].items():
            lines.append(f"    - {err_type}：{count}处")
        lines.append("")

        lines.append("【错误详情】")
        for i, err in enumerate(errors, 1):
            lines.append(f"\n[{i}] 第{err.get('segment_index')}段 - {err.get('error_type')}")
            lines.append(f"  问题原文：{err.get('raw_text')}")
            lines.append(f"  错误说明：{err.get('error_desc')}")
            lines.append(f"  优化建议：{err.get('optimize_suggest')}")

        lines.append("")
        lines.append("=" * 50)
        return "\n".join(lines)

    def get_flat_errors(self, errors: list) -> list:
        """将错误数据扁平化（便于前端处理）"""
        return errors


# 模块测试
if __name__ == "__main__":
    corrector = AcademicCorrector()

    test_paragraphs = [
        "人工智能技术在教育领域得到广泛应用。我认为这个技术非常好用。",
        "机器学习是一种重要的学习方法。参考文献[1]提出了相关算法。",
        "实验结果表明，准确率提升了12.3%。这个效果很明显。",
        "深度学习模型在图像识别任务中表现不错，训练数据使用了很多图片。",
        "通过实验验证，该方法比传统方法好很多，具体原因不太清楚。",
        "本文提出了一个新方法，但是没有和其他方法对比，效果还行吧。"
    ]

    errors = corrector.correct(test_paragraphs)
    print(f"检测到 {len(errors)} 处错误")

    report = corrector.generate_error_report(errors)
    print(report)
