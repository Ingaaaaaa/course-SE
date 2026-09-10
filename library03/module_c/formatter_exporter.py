# module_c/formatter_exporter.py
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from config import (
    FONT_MAIN, FONT_TITLE, SIZE_MAIN, SIZE_TITLE1,
    SIZE_TITLE2, SIZE_TITLE3, LINE_SPACING, INDENT_CHAR
)


def generate_final_doc(struct_data: dict, save_path: str, style_params: dict = None) -> bool:
    """
    接收B模块结构化JSON，生成并导出标准化排版Word文档
    :param struct_data: B模块输出的标准字典（新结构：包含paper_title/author/sub_title_list/paragraph_list/ref_list）
    :param save_path: 最终docx文件保存绝对/相对路径
    :param style_params: 自定义排版参数，可选，包含：
        font_main: 正文字体
        font_title: 标题字体
        size_main: 正文字号(pt)
        size_author: 作者字号(pt)
        size_title1: 一级标题字号(pt)
        size_title2: 二级标题字号(pt)
        line_spacing: 行距
        indent_char: 首行缩进字符数
    :return: 成功返回True，失败返回False
    """
    try:
        params = {
            "font_main": FONT_MAIN,
            "font_title": FONT_TITLE,
            "size_main": SIZE_MAIN,
            "size_author": SIZE_TITLE3,
            "size_title1": SIZE_TITLE1,
            "size_title2": SIZE_TITLE2,
            "line_spacing": LINE_SPACING,
            "indent_char": INDENT_CHAR
        }
        if style_params and isinstance(style_params, dict):
            params.update(style_params)

        required_keys = ["task_id", "paper_title", "author", "sub_title_list", "content_flow", "ref_list"]
        for key in required_keys:
            if key not in struct_data:
                print(f"缺失必填字段：{key}")
                return False

        paper_title = struct_data.get("paper_title", "")
        author_info = struct_data.get("author", "")
        sub_title_list = struct_data.get("sub_title_list", [])
        content_flow = struct_data.get("content_flow", [])
        ref_list = struct_data.get("ref_list", [])

        doc = Document()

        doc.styles['Normal'].font.name = params["font_main"]
        doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), params["font_main"])
        doc.styles['Normal'].font.size = Pt(params["size_main"])
        doc.styles['Normal'].paragraph_format.line_spacing = params["line_spacing"]

        indent_value = Pt(params["indent_char"] * 12)

        # ========== 1. 论文总标题 ==========
        if paper_title.strip():
            p_title = doc.add_paragraph()
            run_title = p_title.add_run(paper_title)
            run_title.font.name = params["font_title"]
            run_title._element.rPr.rFonts.set(qn('w:eastAsia'), params["font_title"])
            run_title.font.size = Pt(params["size_title1"])
            run_title.font.bold = True
            p_title.paragraph_format.space_after = Pt(15)
            p_title.paragraph_format.alignment = 1

        # ========== 2. 作者信息 ==========
        if author_info.strip():
            p_author = doc.add_paragraph()
            run_author = p_author.add_run(author_info)
            run_author.font.name = params["font_title"]
            run_author._element.rPr.rFonts.set(qn('w:eastAsia'), params["font_title"])
            run_author.font.size = Pt(params["size_author"])
            p_author.paragraph_format.space_after = Pt(12)
            p_author.paragraph_format.alignment = 1

        # ========== 3. 正文内容（按content_flow顺序渲染） ==========
        for item in content_flow:
            if not isinstance(item, dict):
                continue

            item_type = item.get("type", "").strip()
            item_content = item.get("content", "").strip()

            if not item_content:
                continue

            if item_type == "title":
                p_sub = doc.add_paragraph()
                run_sub = p_sub.add_run(item_content)
                run_sub.font.name = params["font_title"]
                run_sub._element.rPr.rFonts.set(qn('w:eastAsia'), params["font_title"])
                run_sub.font.size = Pt(params["size_title2"])
                run_sub.font.bold = True
                p_sub.paragraph_format.space_before = Pt(10)
                p_sub.paragraph_format.space_after = Pt(6)

            elif item_type == "paragraph":
                p_main = doc.add_paragraph()
                __add_text_with_superscript(p_main, item_content, params)
                p_main.paragraph_format.first_line_indent = indent_value
                p_main.paragraph_format.line_spacing = params["line_spacing"]
                p_main.paragraph_format.space_after = Pt(8)

        # ========== 4. 参考文献区域 ==========
        if ref_list and isinstance(ref_list, list):
            p_ref_title = doc.add_paragraph()
            run_ref_title = p_ref_title.add_run("参考文献")
            run_ref_title.font.name = params["font_title"]
            run_ref_title._element.rPr.rFonts.set(qn('w:eastAsia'), params["font_title"])
            run_ref_title.font.size = Pt(params["size_title2"])
            run_ref_title.font.bold = True
            p_ref_title.paragraph_format.space_before = Pt(10)
            p_ref_title.paragraph_format.space_after = Pt(6)

            for ref_item in ref_list:
                if isinstance(ref_item, dict):
                    ref_content = ref_item.get("content", "").strip()
                    if ref_content:
                        p_ref = doc.add_paragraph()
                        run_ref = p_ref.add_run(ref_content)
                        run_ref.font.name = params["font_main"]
                        run_ref._element.rPr.rFonts.set(qn('w:eastAsia'), params["font_main"])
                        run_ref.font.size = Pt(params["size_main"])
                        p_ref.paragraph_format.line_spacing = params["line_spacing"]

        doc.save(save_path)
        return True

    except Exception as e:
        print(f"生成文档异常：{str(e)}")
        return False


def __add_text_with_superscript(paragraph, text, params):
    """
    将文本中的引用标记[数字]转换为上角标格式
    :param paragraph: docx段落对象
    :param text: 原始文本
    :param params: 排版参数
    """
    import re

    parts = re.split(r'(\[\d+\])', text)

    for part in parts:
        if not part:
            continue

        if re.match(r'^\[\d+\]$', part):
            run = paragraph.add_run(part)
            run.font.name = params["font_main"]
            run._element.rPr.rFonts.set(qn('w:eastAsia'), params["font_main"])
            run.font.size = Pt(params["size_main"] * 0.7)
            __set_superscript(run)
        else:
            run = paragraph.add_run(part)
            run.font.name = params["font_main"]
            run._element.rPr.rFonts.set(qn('w:eastAsia'), params["font_main"])
            run.font.size = Pt(params["size_main"])


def __set_superscript(run):
    """
    设置run为上角标
    :param run: docx run对象
    """
    rPr = run._element.get_or_add_rPr()
    vertAlign = OxmlElement('w:vertAlign')
    vertAlign.set(qn('w:val'), 'superscript')
    rPr.append(vertAlign)
