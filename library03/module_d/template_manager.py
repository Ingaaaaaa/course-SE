# module_d/template_manager.py
import json
import os
from pathlib import Path
from datetime import datetime


class TemplateManager:
    """模板管理器：负责内置模板管理、自定义模板的保存/加载/导入/导出"""

    def __init__(self, template_dir: str = None):
        if template_dir is None:
            self.template_dir = Path(__file__).parent.parent / "template_lib"
        else:
            self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)

        self.built_in_templates = self._init_built_in_templates()

    def _init_built_in_templates(self) -> list:
        """初始化内置模板库"""
        return [
            {
                "id": "builtin_1",
                "name": "本科毕业论文（文科）",
                "category": "学位类",
                "tags": ["本科", "文科", "通用"],
                "is_builtin": True,
                "create_time": "2026-01-01",
                "params": {
                    "font_main": "宋体",
                    "font_title": "黑体",
                    "size_main": 12,
                    "size_author": 14,
                    "size_title1": 18,
                    "size_title2": 15,
                    "size_title3": 14,
                    "line_spacing": 1.5,
                    "indent_char": 2,
                    "margin_top": 2.54,
                    "margin_bottom": 2.54,
                    "margin_left": 3.17,
                    "margin_right": 3.17,
                    "ref_format": "GB/T7714-2015"
                }
            },
            {
                "id": "builtin_2",
                "name": "本科毕业论文（理工科）",
                "category": "学位类",
                "tags": ["本科", "理工科", "通用"],
                "is_builtin": True,
                "create_time": "2026-01-01",
                "params": {
                    "font_main": "宋体",
                    "font_title": "黑体",
                    "size_main": 12,
                    "size_author": 14,
                    "size_title1": 18,
                    "size_title2": 15,
                    "size_title3": 14,
                    "line_spacing": 1.5,
                    "indent_char": 2,
                    "margin_top": 2.54,
                    "margin_bottom": 2.54,
                    "margin_left": 3.17,
                    "margin_right": 3.17,
                    "ref_format": "GB/T7714-2015"
                }
            },
            {
                "id": "builtin_3",
                "name": "硕士学位论文",
                "category": "学位类",
                "tags": ["硕士", "研究生", "通用"],
                "is_builtin": True,
                "create_time": "2026-01-01",
                "params": {
                    "font_main": "宋体",
                    "font_title": "黑体",
                    "size_main": 12,
                    "size_author": 14,
                    "size_title1": 18,
                    "size_title2": 15,
                    "size_title3": 14,
                    "line_spacing": 1.5,
                    "indent_char": 2,
                    "margin_top": 2.54,
                    "margin_bottom": 2.54,
                    "margin_left": 3.17,
                    "margin_right": 3.17,
                    "ref_format": "GB/T7714-2015"
                }
            },
            {
                "id": "builtin_4",
                "name": "博士学位论文",
                "category": "学位类",
                "tags": ["博士", "研究生", "通用"],
                "is_builtin": True,
                "create_time": "2026-01-01",
                "params": {
                    "font_main": "宋体",
                    "font_title": "黑体",
                    "size_main": 12,
                    "size_author": 14,
                    "size_title1": 18,
                    "size_title2": 15,
                    "size_title3": 14,
                    "line_spacing": 1.5,
                    "indent_char": 2,
                    "margin_top": 2.8,
                    "margin_bottom": 2.8,
                    "margin_left": 3.0,
                    "margin_right": 3.0,
                    "ref_format": "GB/T7714-2015"
                }
            },
            {
                "id": "builtin_5",
                "name": "中文核心期刊投稿",
                "category": "期刊投稿类",
                "tags": ["期刊", "核心", "中文"],
                "is_builtin": True,
                "create_time": "2026-01-01",
                "params": {
                    "font_main": "宋体",
                    "font_title": "黑体",
                    "size_main": 10.5,
                    "size_author": 11,
                    "size_title1": 16,
                    "size_title2": 14,
                    "size_title3": 12,
                    "line_spacing": 1.5,
                    "indent_char": 2,
                    "margin_top": 2.5,
                    "margin_bottom": 2.5,
                    "margin_left": 2.8,
                    "margin_right": 2.8,
                    "ref_format": "GB/T7714-2015"
                }
            },
            {
                "id": "builtin_6",
                "name": "SCI/SSCI外文期刊",
                "category": "期刊投稿类",
                "tags": ["SCI", "SSCI", "英文"],
                "is_builtin": True,
                "create_time": "2026-01-01",
                "params": {
                    "font_main": "Times New Roman",
                    "font_title": "Arial",
                    "size_main": 11,
                    "size_author": 10,
                    "size_title1": 14,
                    "size_title2": 12,
                    "size_title3": 11,
                    "line_spacing": 2.0,
                    "indent_char": 0,
                    "margin_top": 2.54,
                    "margin_bottom": 2.54,
                    "margin_left": 2.54,
                    "margin_right": 2.54,
                    "ref_format": "APA"
                }
            },
            {
                "id": "builtin_7",
                "name": "课程小论文",
                "category": "课程作业类",
                "tags": ["课程", "小论文", "通用"],
                "is_builtin": True,
                "create_time": "2026-01-01",
                "params": {
                    "font_main": "宋体",
                    "font_title": "黑体",
                    "size_main": 12,
                    "size_author": 12,
                    "size_title1": 16,
                    "size_title2": 14,
                    "size_title3": 12,
                    "line_spacing": 1.5,
                    "indent_char": 2,
                    "margin_top": 2.54,
                    "margin_bottom": 2.54,
                    "margin_left": 3.17,
                    "margin_right": 3.17,
                    "ref_format": "GB/T7714-2015"
                }
            },
            {
                "id": "builtin_8",
                "name": "实验报告",
                "category": "课程作业类",
                "tags": ["实验", "报告", "通用"],
                "is_builtin": True,
                "create_time": "2026-01-01",
                "params": {
                    "font_main": "宋体",
                    "font_title": "黑体",
                    "size_main": 12,
                    "size_author": 12,
                    "size_title1": 18,
                    "size_title2": 14,
                    "size_title3": 12,
                    "line_spacing": 1.5,
                    "indent_char": 0,
                    "margin_top": 2.54,
                    "margin_bottom": 2.54,
                    "margin_left": 3.17,
                    "margin_right": 3.17,
                    "ref_format": "GB/T7714-2015"
                }
            }
        ]

    def get_all_templates(self) -> dict:
        """获取所有模板（内置+自定义）"""
        custom_templates = self._load_custom_templates()
        return {
            "built_in": self.built_in_templates,
            "custom": custom_templates
        }

    def _load_custom_templates(self) -> list:
        """从本地加载自定义模板"""
        custom_templates = []
        if self.template_dir.exists():
            for file in self.template_dir.glob("*.json"):
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        template = json.load(f)
                        if isinstance(template, dict) and "name" in template:
                            template["is_builtin"] = False
                            custom_templates.append(template)
                except Exception:
                    continue
        return custom_templates

    def save_template(self, name: str, params: dict, tags: list = None, category: str = "自定义") -> bool:
        """保存自定义模板"""
        try:
            template_id = f"custom_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            template = {
                "id": template_id,
                "name": name,
                "category": category,
                "tags": tags or [],
                "is_builtin": False,
                "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "params": params
            }

            file_path = self.template_dir / f"{template_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存模板失败：{str(e)}")
            return False

    def delete_template(self, template_id: str) -> bool:
        """删除自定义模板"""
        try:
            if template_id.startswith("builtin_"):
                return False
            file_path = self.template_dir / f"{template_id}.json"
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False

    def export_template(self, template_id: str, export_path: str) -> bool:
        """导出模板为文件"""
        try:
            template = None
            for t in self.built_in_templates:
                if t["id"] == template_id:
                    template = t.copy()
                    break
            if not template:
                file_path = self.template_dir / f"{template_id}.json"
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        template = json.load(f)

            if template:
                with open(export_path, "w", encoding="utf-8") as f:
                    json.dump(template, f, ensure_ascii=False, indent=2)
                return True
            return False
        except Exception:
            return False

    def import_template(self, import_path: str) -> bool:
        """导入模板文件"""
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                template = json.load(f)

            if isinstance(template, dict) and "name" in template:
                template["id"] = f"custom_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                template["is_builtin"] = False
                template["create_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                file_path = self.template_dir / f"{template['id']}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(template, f, ensure_ascii=False, indent=2)
                return True
            return False
        except Exception as e:
            print(f"导入模板失败：{str(e)}")
            return False

    def get_template_by_id(self, template_id: str) -> dict:
        """根据ID获取模板"""
        for t in self.built_in_templates:
            if t["id"] == template_id:
                return t

        file_path = self.template_dir / f"{template_id}.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def search_templates(self, keyword: str) -> list:
        """搜索模板"""
        results = []
        for t in self.built_in_templates:
            if keyword in t.get("name", "") or keyword in str(t.get("tags", [])):
                results.append(t)
        for t in self._load_custom_templates():
            if keyword in t.get("name", "") or keyword in str(t.get("tags", [])):
                results.append(t)
        return results


# 模块测试
if __name__ == "__main__":
    tm = TemplateManager()
    all_templates = tm.get_all_templates()
    print(f"内置模板数量: {len(all_templates['built_in'])}")
    print(f"自定义模板数量: {len(all_templates['custom'])}")
