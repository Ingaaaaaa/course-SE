# ===================== 全局配置文件 全员共用 禁止私自修改 =====================
import json

# 1. 大模型 API 配置（自行替换密钥/地址）
# LLM_API_URL = "你的大模型API接口地址"
# LLM_API_KEY = "你的API密钥"
# LLM_TIMEOUT = 30  # 请求超时时间 单位：秒
# LLM_API_URL = "你的大模型API接口地址"
# LLM_API_KEY = "你的API密钥"
# LLM_TIMEOUT = 30  # 请求超时时间 单位：秒
# 大模型 API 配置（阿里云百炼）
LLM_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
LLM_API_KEY = "sk-ws-H.RELPPYY.MzbE.MEUCIQCU0p7hm12lWrExa1T9Sn2tq2KFfHNjMY6wAiWgL84vZwIgFqw93nTkeyKO2gIJ4hSWzPJsyOzCjhC9er9dxbC2ySg"
LLM_TIMEOUT = 30

# LLM模型名称（阿里云百炼可用模型，任选其一）
# 可选：qwen-turbo / qwen-plus / qwen-long
# LLM_MODEL_NAME = "qwen-turbo"
LLM_MODEL_NAME = "qwen-plus"

# 2. 论文排版全局样式（python-docx 使用）
FONT_MAIN = "宋体"
FONT_TITLE = "黑体"
SIZE_MAIN = 12       # 小四 12pt
SIZE_TITLE1 = 18     # 二号 18pt
SIZE_TITLE2 = 15     # 小三 15pt
SIZE_TITLE3 = 14     # 四号 14pt
LINE_SPACING = 1.5   # 1.5倍行距
INDENT_CHAR = 2      # 首行缩进2字符

# 3. 固定接口 JSON 模板（A→B / B→C 标准格式）
# A 传给 B 的格式
A_TO_B_JSON_TPL = {
    "task_id": "",
    "clean_text": ""
}

# B 传给 C 的格式
B_TO_C_JSON_TPL = {
    "task_id": "",
    "paper_title": "",
    "author": "",
    "sub_title_list": [],
    "content_flow": [],
    "ref_list": []
}

# 4. AI 固定系统提示词（B模块专用）
AI_SYSTEM_PROMPT = """
你是文档结构识别助手，拆分论文文本，识别章节类型：标题、作者、摘要、关键词、一级标题、二级标题、正文段落、图注、表注、参考文献；
输出JSON数组，每条包含segment_index段落序号、segment_type段落类型、text段落原文，仅输出JSON，无多余文字。

【segment_type可选值】标题、作者、摘要、关键词、一级标题、二级标题、正文段落、图注、表注、参考文献

【输出格式】
[
    {"segment_index": 1, "segment_type": "标题", "text": "论文总标题"},
    {"segment_index": 2, "segment_type": "作者", "text": "作者姓名"},
    {"segment_index": 3, "segment_type": "摘要", "text": "摘要内容"},
    {"segment_index": 4, "segment_type": "关键词", "text": "关键词1；关键词2"},
    {"segment_index": 5, "segment_type": "一级标题", "text": "1 相关研究现状"},
    {"segment_index": 6, "segment_type": "正文段落", "text": "正文内容，包含引用标记[1]"},
    {"segment_index": 7, "segment_type": "二级标题", "text": "1.1 研究背景"},
    {"segment_index": 8, "segment_type": "正文段落", "text": "正文内容"},
    {"segment_index": 9, "segment_type": "参考文献", "text": "[1] 作者. 标题[文献类型]. 期刊, 年份, 卷(期):页码."}
]

【规则】
1. 严格按原文顺序排列，段落序号从1开始递增
2. 不修改原文文字，完整保留引用标记[1][2]
3. 长正文按语义切分为多个段落，不合并
4. 无对应内容不输出，不编造信息
5. 仅输出纯净JSON数组，禁止任何额外文字
"""