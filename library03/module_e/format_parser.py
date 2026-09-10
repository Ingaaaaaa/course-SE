# module_e/format_parser.py
import requests
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import LLM_API_URL, LLM_API_KEY, LLM_TIMEOUT, LLM_MODEL_NAME


FORMAT_PARSE_PROMPT = """
你是论文格式规则提取专家，仅从提供的格式原文中提取排版参数，禁止编造原文不存在的规则；原文未提及参数填写通用默认值。

【强制输出格式：仅输出标准JSON，禁止多余文字、注释、解释】
{
  "template_name": "自动识别的规范名称（如XX大学本科计算机毕业论文格式）",
  "confidence": 0~1浮点数字（原文信息完整度越高数值越高，低于0.6代表信息不足）,
  "params": {
    "正文字体": "",
    "正文字号": 数字(pt),
    "标题字体": "",
    "作者字号": 数字(pt),
    "一级标题字号": 数字(pt),
    "二级标题字号": 数字(pt),
    "行距": 小数(如1.5),
    "首行缩进字符": 数字,
    "margin_top": 页面上边距cm,
    "margin_bottom": 页面下边距cm,
    "margin_left": 页面左边距cm,
    "margin_right": 页面右边距cm,
    "ref_standard": "参考文献标准（GB/T7714-2015/APA/MLA等）"
  }
}

【提取规则】
1. 字体识别：区分中文字体（宋体、黑体、楷体、仿宋、微软雅黑）和英文字体（Times New Roman、Arial等）
2. 字号识别：二号=18pt、小二=16pt、小三=15pt、四号=14pt、小四=12pt、五号=10.5pt
3. 行距识别：单倍行距=1.0、1.25倍行距=1.25、1.5倍行距=1.5、双倍行距=2.0
4. 缩进识别：首行缩进2字符=2、首行缩进0=0
5. 单位换算：1英寸=2.54cm，学校常用边距约2.5-3cm
6. 原文未提及的参数使用通用默认值：正文字体=宋体、正文字号=12、标题字体=黑体、一级标题字号=18、二级标题字号=15、作者字号=14、行距=1.5、首行缩进=2、边距=2.54cm、ref_standard=GB/T7714-2015

【提取原文内容】
{format_text}
"""


class FormatParser:
    """智能格式解析器：分析格式规范文本，生成结构化排版参数"""

    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}"
        }

    def parse_format_text(self, format_text: str) -> dict:
        """
        解析粘贴的格式规范文字
        :param format_text: 用户粘贴的格式要求文本
        :return: 标准化格式参数JSON（包含template_name, confidence, params）
        """
        if not format_text.strip():
            return self._get_empty_result()

        prompt = FORMAT_PARSE_PROMPT.replace("{format_text}", format_text)

        try:
            response = self._call_ai(prompt)
            if response and isinstance(response, dict):
                return self._validate_and_complete(response)
            return self._get_empty_result()
        except Exception as e:
            print(f"格式解析失败：{str(e)}")
            return self._get_empty_result()

    def parse_format_doc(self, doc_path: str) -> dict:
        """
        解析上传的格式规范Word文档
        :param doc_path: Word文档路径
        :return: 标准化格式参数JSON
        """
        try:
            from module_a.ui_doc_handler import read_and_clean_doc
            result = read_and_clean_doc(doc_path)
            format_text = result.get("clean_text", "")
            return self.parse_format_text(format_text)
        except Exception as e:
            print(f"格式文档解析失败：{str(e)}")
            return self._get_empty_result()

    def _call_ai(self, prompt: str) -> dict:
        """调用AI解析格式"""
        request_body = {
            "model": LLM_MODEL_NAME,
            "messages": [
                {"role": "system", "content": "你是论文格式规则提取专家，仅输出标准JSON格式，禁止任何额外解释。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0,
            "max_tokens": 2000
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
        print("====格式解析AI返回内容====")
        print(model_output)
        print("==========================")

        try:
            return json.loads(model_output.strip())
        except json.JSONDecodeError:
            start_idx = model_output.find('{')
            end_idx = model_output.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                return json.loads(model_output[start_idx:end_idx])
            raise

    def _validate_and_complete(self, result: dict) -> dict:
        """验证和补全格式参数"""
        if "params" not in result:
            result["params"] = {}
        
        if "template_name" not in result:
            result["template_name"] = "自动解析格式模板"
        
        if "confidence" not in result:
            result["confidence"] = 0.5

        default_params = self._get_default_params()

        for key in default_params:
            if key not in result["params"] or result["params"][key] == "" or result["params"][key] is None:
                result["params"][key] = default_params[key]

        if isinstance(result["params"].get("正文字号"), str):
            try:
                result["params"]["正文字号"] = float(result["params"]["正文字号"])
            except:
                result["params"]["正文字号"] = 12

        if isinstance(result["params"].get("一级标题字号"), str):
            try:
                result["params"]["一级标题字号"] = float(result["params"]["一级标题字号"])
            except:
                result["params"]["一级标题字号"] = 18

        if isinstance(result["params"].get("二级标题字号"), str):
            try:
                result["params"]["二级标题字号"] = float(result["params"]["二级标题字号"])
            except:
                result["params"]["二级标题字号"] = 15

        if isinstance(result["params"].get("作者字号"), str):
            try:
                result["params"]["作者字号"] = float(result["params"]["作者字号"])
            except:
                result["params"]["作者字号"] = 14

        if isinstance(result["params"].get("行距"), str):
            try:
                result["params"]["行距"] = float(result["params"]["行距"])
            except:
                result["params"]["行距"] = 1.5

        if isinstance(result["params"].get("首行缩进字符"), str):
            try:
                result["params"]["首行缩进字符"] = int(result["params"]["首行缩进字符"])
            except:
                result["params"]["首行缩进字符"] = 2

        for key in ["margin_top", "margin_bottom", "margin_left", "margin_right"]:
            if isinstance(result["params"].get(key), str):
                try:
                    result["params"][key] = float(result["params"][key])
                except:
                    result["params"][key] = 2.54

        return result

    def _get_empty_result(self) -> dict:
        """获取空结果模板"""
        return {
            "template_name": "自动解析格式模板",
            "confidence": 0.0,
            "params": self._get_default_params()
        }

    def _get_default_params(self) -> dict:
        """获取默认参数模板"""
        return {
            "正文字体": "宋体",
            "正文字号": 12,
            "标题字体": "黑体",
            "作者字号": 14,
            "一级标题字号": 18,
            "二级标题字号": 15,
            "行距": 1.5,
            "首行缩进字符": 2,
            "margin_top": 2.54,
            "margin_bottom": 2.54,
            "margin_left": 3.17,
            "margin_right": 3.17,
            "ref_standard": "GB/T7714-2015"
        }

    def generate_format_report(self, result: dict) -> str:
        """生成格式解读报告"""
        params = result.get("params", {})
        report_lines = [
            "========== 论文格式解读报告 ==========",
            "",
            f"模板名称：{result.get('template_name', '未知')}",
            f"识别置信度：{result.get('confidence', 0.0):.2f}",
            "",
            "一、字体设置",
            f"  正文字体：{params.get('正文字体', '宋体')}",
            f"  标题字体：{params.get('标题字体', '黑体')}",
            "",
            "二、字号设置",
            f"  正文字号：{params.get('正文字号', 12)}pt",
            f"  一级标题字号：{params.get('一级标题字号', 18)}pt",
            f"  二级标题字号：{params.get('二级标题字号', 15)}pt",
            f"  作者字号：{params.get('作者字号', 14)}pt",
            "",
            "三、段落格式",
            f"  行距：{params.get('行距', 1.5)}倍",
            f"  首行缩进：{params.get('首行缩进字符', 2)}字符",
            "",
            "四、页面边距",
            f"  上边距：{params.get('margin_top', 2.54)}cm",
            f"  下边距：{params.get('margin_bottom', 2.54)}cm",
            f"  左边距：{params.get('margin_left', 3.17)}cm",
            f"  右边距：{params.get('margin_right', 3.17)}cm",
            "",
            "五、特殊格式",
            f"  参考文献格式：{params.get('ref_standard', 'GB/T7714-2015')}",
        ]

        report_lines.append("")
        report_lines.append("========================================")
        return "\n".join(report_lines)

    def params_to_style(self, result: dict) -> dict:
        """将格式参数转换为C模块style_params格式"""
        params = result.get("params", {})
        return {
            "font_main": params.get("正文字体", "宋体"),
            "font_title": params.get("标题字体", "黑体"),
            "size_main": params.get("正文字号", 12),
            "size_author": params.get("作者字号", 14),
            "size_title1": params.get("一级标题字号", 18),
            "size_title2": params.get("二级标题字号", 15),
            "line_spacing": params.get("行距", 1.5),
            "indent_char": params.get("首行缩进字符", 2)
        }


# 模块测试
if __name__ == "__main__":
    fp = FormatParser()

    test_format_text = """
    论文格式要求：
    1. 正文字体宋体，小四号12pt，1.5倍行距，首行缩进2字符
    2. 一级标题黑体三号18pt，二级标题黑体小三15pt
    3. 页边距上下2.54cm，左右3.17cm
    4. 参考文献采用GB/T7714-2015标准格式
    """

    result = fp.parse_format_text(test_format_text)
    print("解析结果：")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    report = fp.generate_format_report(result)
    print("\n格式报告：")
    print(report)
