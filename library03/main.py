# main.py - 论文智能排版AI Agent（完整版）
from module_a.ui_doc_handler import read_and_clean_doc
from module_b.ai_processor import process_text
from module_c.formatter_exporter import generate_final_doc
from module_d.template_manager import TemplateManager
from module_e.format_parser import FormatParser
from module_f.academic_corrector import AcademicCorrector
from module_g.auto_fixer import AutoFixer

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("论文智能排版AI Agent - 完整版")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)

        self.template_manager = TemplateManager()
        self.format_parser = FormatParser()
        self.corrector = AcademicCorrector()
        self.fixer = AutoFixer()

        self.style_params = {
            "font_main": "宋体",
            "font_title": "黑体",
            "size_main": 12,
            "size_author": 14,
            "size_title1": 18,
            "size_title2": 15,
            "line_spacing": 1.5,
            "indent_char": 2
        }

        self.current_errors = []
        self.current_b_result = None
        self.current_fix_result = None

        self.create_widgets()
        self.load_builtin_templates()

    def create_widgets(self):
        main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
        main_container.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_container, width=700)
        right_frame = tk.Frame(main_container, width=280)
        main_container.add(left_frame, width=700)
        main_container.add(right_frame, width=280)

        self.create_left_panel(left_frame)
        self.create_right_panel(right_frame)

    def create_left_panel(self, parent):
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        content_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(content_frame, text="论文智能排版AI Agent", font=("黑体", 20, "bold"), pady=15)
        title_label.pack()

        self.create_module_ab_section(content_frame)
        self.create_module_d_section(content_frame)
        self.create_module_e_section(content_frame)
        self.create_module_fg_section(content_frame)
        self.create_params_section(content_frame)

    def create_right_panel(self, parent):
        right_title = tk.Label(parent, text="错误清单", font=("黑体", 14, "bold"), pady=10)
        right_title.pack(fill=tk.X)

        self.error_listbox = tk.Listbox(parent, font=("宋体", 10))
        self.error_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(self.error_listbox, orient="vertical", command=self.error_listbox.yview)
        self.error_listbox.configure(yscrollcommand=scrollbar.set)

        self.error_detail = tk.Text(parent, height=8, font=("宋体", 9), wrap=tk.WORD)
        self.error_detail.pack(fill=tk.X, padx=5, pady=5)

        btn_clear_errors = tk.Button(parent, text="清除错误记录", command=self.clear_errors,
                                     font=("宋体", 10), bg="#FFEBEE")
        btn_clear_errors.pack(fill=tk.X, padx=5, pady=5)

        status_frame = tk.Frame(parent)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        self.status_label = tk.Label(status_frame, text="就绪", font=("宋体", 10), fg="#666", anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=5)

    def create_module_ab_section(self, parent):
        """模块A/B：基础功能区"""
        frame = tk.LabelFrame(parent, text="基础功能", font=("黑体", 12), padx=10, pady=10)
        frame.pack(fill=tk.X, pady=10)

        btn_frame = tk.Frame(frame)
        btn_frame.pack()

        btn_clean = tk.Button(btn_frame, text="文本清洗", command=self.do_clean_only,
                              font=("宋体", 11), width=12, bg="#E8F5E9", fg="#2E7D32")
        btn_clean.pack(side=tk.LEFT, padx=5)

        btn_identify = tk.Button(btn_frame, text="AI信息识别", command=self.do_identify_only,
                                  font=("宋体", 11), width=12, bg="#E3F2FD", fg="#1565C0")
        btn_identify.pack(side=tk.LEFT, padx=5)

        btn_format = tk.Button(btn_frame, text="完整排版", command=self.do_full_format,
                                font=("宋体", 11), width=12, bg="#FFF3E0", fg="#E65100")
        btn_format.pack(side=tk.LEFT, padx=5)

        tk.Label(frame, text="A:文本清洗 | A+B:AI识别 | A+B+C:完整排版", font=("宋体", 9), fg="#666").pack()

    def create_module_d_section(self, parent):
        """模块D：模板管理"""
        frame = tk.LabelFrame(parent, text="模板管理（D模块）", font=("黑体", 12), padx=10, pady=10)
        frame.pack(fill=tk.X, pady=10)

        top_frame = tk.Frame(frame)
        top_frame.pack(fill=tk.X)

        self.template_notebook = ttk.Notebook(top_frame)
        self.template_notebook.pack(fill=tk.X)

        self.builtin_tab = tk.Frame(self.template_notebook)
        self.custom_tab = tk.Frame(self.template_notebook)
        self.template_notebook.add(self.builtin_tab, text="官方模板库")
        self.template_notebook.add(self.custom_tab, text="我的自定义模板")

        self.builtin_listbox = tk.Listbox(self.builtin_tab, font=("宋体", 10), height=5)
        self.builtin_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.builtin_listbox.bind("<Double-Button-1>", lambda e: self.load_selected_template())

        self.custom_listbox = tk.Listbox(self.custom_tab, font=("宋体", 10), height=5)
        self.custom_listbox.pack(fill=tk.X, padx=5, pady=5)

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(btn_frame, text="加载模板", command=self.load_selected_template,
                  font=("宋体", 10), width=10).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="保存当前为模板", command=self.save_current_template,
                  font=("宋体", 10), width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="删除", command=self.delete_custom_template,
                  font=("宋体", 10), width=8, bg="#FFCDD2").pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="导入", command=self.import_template,
                  font=("宋体", 10), width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="导出", command=self.export_selected_template,
                  font=("宋体", 10), width=8).pack(side=tk.LEFT, padx=2)

    def create_module_e_section(self, parent):
        """模块E：智能格式解析"""
        frame = tk.LabelFrame(parent, text="智能格式解析（E模块）", font=("黑体", 12), padx=10, pady=10)
        frame.pack(fill=tk.X, pady=10)

        btn_frame = tk.Frame(frame)
        btn_frame.pack()

        tk.Button(btn_frame, text="粘贴格式要求文字", command=self.show_text_parser,
                  font=("宋体", 11), width=18, bg="#F3E5F5", fg="#7B1FA2").pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="上传格式规范文档", command=self.show_doc_parser,
                  font=("宋体", 11), width=18, bg="#F3E5F5", fg="#7B1FA2").pack(side=tk.LEFT, padx=5)

        tk.Label(frame, text="AI自动解析格式要求，填充排版参数", font=("宋体", 9), fg="#666").pack()

    def create_module_fg_section(self, parent):
        """模块F/G：学术纠错"""
        frame = tk.LabelFrame(parent, text="学术AI纠错（F/G模块）", font=("黑体", 12), padx=10, pady=10)
        frame.pack(fill=tk.X, pady=10)

        check_frame = tk.Frame(frame)
        check_frame.pack()

        tk.Label(check_frame, text="检测层次：", font=("宋体", 10)).pack(side=tk.LEFT)

        self.check_basic = tk.BooleanVar(value=True)
        tk.Checkbutton(check_frame, text="基础层", variable=self.check_basic,
                        font=("宋体", 9)).pack(side=tk.LEFT, padx=5)

        self.check_academic = tk.BooleanVar(value=True)
        tk.Checkbutton(check_frame, text="学术层", variable=self.check_academic,
                        font=("宋体", 9)).pack(side=tk.LEFT, padx=5)

        self.check_deep = tk.BooleanVar(value=True)
        tk.Checkbutton(check_frame, text="深度层", variable=self.check_deep,
                        font=("宋体", 9)).pack(side=tk.LEFT, padx=5)

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="学术纠错分析", command=self.do_academic_check,
                  font=("宋体", 11), width=15, bg="#E8EAF6", fg="#3949AB").pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="AI一键修正全文", command=self.do_auto_fix,
                  font=("宋体", 11), width=15, bg="#E8F5E9", fg="#43A047").pack(side=tk.LEFT, padx=5)

    def create_params_section(self, parent):
        """排版参数设置"""
        frame = tk.LabelFrame(parent, text="排版参数设置", font=("黑体", 12), padx=10, pady=10)
        frame.pack(fill=tk.X, pady=10)

        grid_frame = tk.Frame(frame)
        grid_frame.pack()

        row = 0

        tk.Label(grid_frame, text="正文字体:", font=("宋体", 11)).grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.font_main_var = tk.StringVar(value="宋体")
        ttk.Combobox(grid_frame, textvariable=self.font_main_var,
                     values=["宋体", "黑体", "仿宋", "楷体", "微软雅黑"], width=15).grid(row=row, column=1, padx=10)

        tk.Label(grid_frame, text="标题字体:", font=("宋体", 11)).grid(row=row, column=2, sticky=tk.W, padx=10)
        self.font_title_var = tk.StringVar(value="黑体")
        ttk.Combobox(grid_frame, textvariable=self.font_title_var,
                     values=["黑体", "宋体", "楷体", "微软雅黑"], width=15).grid(row=row, column=3, padx=10)

        row += 1
        tk.Label(grid_frame, text="正文字号(pt):", font=("宋体", 11)).grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.size_main_var = tk.StringVar(value="12")
        ttk.Combobox(grid_frame, textvariable=self.size_main_var,
                     values=["10.5", "11", "12", "14", "15", "16"], width=15).grid(row=row, column=1, padx=10)

        tk.Label(grid_frame, text="作者字号(pt):", font=("宋体", 11)).grid(row=row, column=2, sticky=tk.W, padx=10)
        self.size_author_var = tk.StringVar(value="14")
        ttk.Combobox(grid_frame, textvariable=self.size_author_var,
                     values=["12", "14", "15", "16"], width=15).grid(row=row, column=3, padx=10)

        row += 1
        tk.Label(grid_frame, text="一级标题(pt):", font=("宋体", 11)).grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.size_title1_var = tk.StringVar(value="18")
        ttk.Combobox(grid_frame, textvariable=self.size_title1_var,
                     values=["16", "18", "20"], width=15).grid(row=row, column=1, padx=10)

        tk.Label(grid_frame, text="二级标题(pt):", font=("宋体", 11)).grid(row=row, column=2, sticky=tk.W, padx=10)
        self.size_title2_var = tk.StringVar(value="15")
        ttk.Combobox(grid_frame, textvariable=self.size_title2_var,
                     values=["14", "15", "16"], width=15).grid(row=row, column=3, padx=10)

        row += 1
        tk.Label(grid_frame, text="行距:", font=("宋体", 11)).grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.line_spacing_var = tk.StringVar(value="1.5")
        ttk.Combobox(grid_frame, textvariable=self.line_spacing_var,
                     values=["1", "1.25", "1.5", "2"], width=15).grid(row=row, column=1, padx=10)

        tk.Label(grid_frame, text="首行缩进(字符):", font=("宋体", 11)).grid(row=row, column=2, sticky=tk.W, padx=10)
        self.indent_char_var = tk.StringVar(value="2")
        ttk.Combobox(grid_frame, textvariable=self.indent_char_var,
                     values=["0", "1", "2", "3"], width=15).grid(row=row, column=3, padx=10)

        btn_reset = tk.Button(frame, text="恢复默认参数", command=self.reset_params,
                              font=("宋体", 10), bg="#ECEFF1")
        btn_reset.pack(pady=5)

    def load_builtin_templates(self):
        """加载内置模板列表"""
        all_templates = self.template_manager.get_all_templates()
        self.builtin_listbox.delete(0, tk.END)
        for t in all_templates["built_in"]:
            self.builtin_listbox.insert(tk.END, f"{t['name']} [{t['category']}]")

        self.custom_listbox.delete(0, tk.END)
        for t in all_templates["custom"]:
            self.custom_listbox.insert(tk.END, t['name'])

    def load_selected_template(self):
        """加载选中的模板"""
        try:
            idx = self.builtin_listbox.curselection()
            if idx:
                all_templates = self.template_manager.get_all_templates()
                template = all_templates["built_in"][idx[0]]
            else:
                idx = self.custom_listbox.curselection()
                if not idx:
                    messagebox.showwarning("提示", "请先选择一个模板")
                    return
                all_templates = self.template_manager.get_all_templates()
                template = all_templates["custom"][idx[0]]

            params = template["params"]
            self.font_main_var.set(params.get("font_main", "宋体"))
            self.font_title_var.set(params.get("font_title", "黑体"))
            self.size_main_var.set(str(params.get("size_main", 12)))
            self.size_author_var.set(str(params.get("size_author", 14)))
            self.size_title1_var.set(str(params.get("size_title1", 18)))
            self.size_title2_var.set(str(params.get("size_title2", 15)))
            self.line_spacing_var.set(str(params.get("line_spacing", 1.5)))
            self.indent_char_var.set(str(params.get("indent_char", 2)))

            messagebox.showinfo("成功", f"已加载模板：{template['name']}")
        except Exception as e:
            messagebox.showerror("错误", f"加载模板失败：{str(e)}")

    def save_current_template(self):
        """保存当前参数为模板"""
        dialog = tk.Toplevel(self.root)
        dialog.title("保存模板")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="模板名称:", font=("宋体", 11)).pack(pady=5)
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var, width=40).pack(pady=5)

        tk.Label(dialog, text="标签（用逗号分隔）:", font=("宋体", 11)).pack(pady=5)
        tags_var = tk.StringVar()
        tk.Entry(dialog, textvariable=tags_var, width=40).pack(pady=5)

        def do_save():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("提示", "请输入模板名称")
                return
            tags = [t.strip() for t in tags_var.get().split(",") if t.strip()]
            params = self.get_style_params()
            if params:
                success = self.template_manager.save_template(name, params, tags)
                if success:
                    messagebox.showinfo("成功", "模板保存成功！")
                    self.load_builtin_templates()
                    dialog.destroy()
                else:
                    messagebox.showerror("错误", "模板保存失败")

        tk.Button(dialog, text="保存", command=do_save, font=("宋体", 11), width=10).pack(pady=10)

    def delete_custom_template(self):
        """删除自定义模板"""
        idx = self.custom_listbox.curselection()
        if not idx:
            messagebox.showwarning("提示", "请先选择一个自定义模板")
            return
        if messagebox.askyesno("确认", "确定要删除选中的模板吗？"):
            all_templates = self.template_manager.get_all_templates()
            template = all_templates["custom"][idx[0]]
            if self.template_manager.delete_template(template["id"]):
                messagebox.showinfo("成功", "模板已删除")
                self.load_builtin_templates()

    def import_template(self):
        """导入模板"""
        path = filedialog.askopenfilename(filetypes=[("模板文件", "*.json")])
        if path:
            if self.template_manager.import_template(path):
                messagebox.showinfo("成功", "模板导入成功！")
                self.load_builtin_templates()
            else:
                messagebox.showerror("错误", "模板导入失败")

    def export_selected_template(self):
        """导出选中的模板"""
        idx = self.builtin_listbox.curselection()
        if idx:
            all_templates = self.template_manager.get_all_templates()
            template = all_templates["built_in"][idx[0]]
        else:
            idx = self.custom_listbox.curselection()
            if not idx:
                messagebox.showwarning("提示", "请先选择一个模板")
                return
            all_templates = self.template_manager.get_all_templates()
            template = all_templates["custom"][idx[0]]

        path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("模板文件", "*.json")])
        if path:
            if self.template_manager.export_template(template["id"], path):
                messagebox.showinfo("成功", f"模板已导出到：{path}")
            else:
                messagebox.showerror("错误", "模板导出失败")

    def show_text_parser(self):
        """显示文字格式解析弹窗"""
        dialog = tk.Toplevel(self.root)
        dialog.title("智能格式解析 - 粘贴文字")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="请粘贴论文格式要求文字：", font=("宋体", 11)).pack(pady=5)

        text_widget = tk.Text(dialog, font=("宋体", 10), wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        def do_parse():
            text = text_widget.get("1.0", tk.END).strip()
            if not text:
                messagebox.showwarning("提示", "请输入格式要求文字")
                return
            self.update_status("正在AI解析格式要求...")
            try:
                params = self.format_parser.parse_format_text(text)
                self.apply_format_params(params)
                messagebox.showinfo("成功", "格式解析完成！参数已填充")
                self.update_status("就绪")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"解析失败：{str(e)}")
                self.update_status("就绪")

        tk.Button(btn_frame, text="AI解析格式", command=do_parse,
                  font=("宋体", 11), bg="#F3E5F5", width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消", command=dialog.destroy,
                  font=("宋体", 11), width=10).pack(side=tk.LEFT, padx=5)

    def show_doc_parser(self):
        """显示文档格式解析弹窗"""
        path = filedialog.askopenfilename(filetypes=[("Word文档", "*.docx")])
        if not path:
            return

        self.update_status("正在解析格式文档...")
        try:
            params = self.format_parser.parse_format_doc(path)
            self.apply_format_params(params)
            messagebox.showinfo("成功", "格式解析完成！参数已填充")
            self.update_status("就绪")
        except Exception as e:
            messagebox.showerror("错误", f"解析失败：{str(e)}")
            self.update_status("就绪")

    def apply_format_params(self, params: dict):
        """应用格式参数到界面"""
        style_params = self.format_parser.params_to_style(params)
        self.font_main_var.set(style_params.get("font_main", "宋体"))
        self.font_title_var.set(style_params.get("font_title", "黑体"))
        self.size_main_var.set(str(style_params.get("size_main", 12)))
        self.size_author_var.set(str(style_params.get("size_author", 14)))
        self.size_title1_var.set(str(style_params.get("size_title1", 18)))
        self.size_title2_var.set(str(style_params.get("size_title2", 15)))
        self.line_spacing_var.set(str(style_params.get("line_spacing", 1.5)))
        self.indent_char_var.set(str(style_params.get("indent_char", 2)))

    def reset_params(self):
        """恢复默认参数"""
        self.font_main_var.set("宋体")
        self.font_title_var.set("黑体")
        self.size_main_var.set("12")
        self.size_author_var.set("14")
        self.size_title1_var.set("18")
        self.size_title2_var.set("15")
        self.line_spacing_var.set("1.5")
        self.indent_char_var.set("2")

    def do_academic_check(self):
        """执行学术纠错分析"""
        if not self.current_b_result:
            file_path = filedialog.askopenfilename(filetypes=[("Word文档", "*.docx")])
            if not file_path:
                return

            self.update_status("正在清洗文本...")
            try:
                a_result = read_and_clean_doc(file_path)
                self.update_status("正在AI识别信息...")
                self.current_b_result = process_text(a_result)
            except Exception as e:
                messagebox.showerror("错误", f"处理失败：{str(e)}")
                self.update_status("就绪")
                return

        self.update_status("正在进行学术纠错分析...")
        try:
            check_levels = {
                "basic": self.check_basic.get(),
                "academic": self.check_academic.get(),
                "deep": self.check_deep.get()
            }
            self.current_errors = self.corrector.correct_structured_data(self.current_b_result, check_levels)

            flat_errors = self.corrector.get_flat_errors(self.current_errors)
            self.error_listbox.delete(0, tk.END)
            for i, err in enumerate(flat_errors, 1):
                self.error_listbox.insert(tk.END, f"{i}. [{err['error_type']}] {err['raw_text'][:30]}...")

            summary = self.corrector.get_error_summary(self.current_errors)
            messagebox.showinfo("纠错完成", f"检测到 {summary['总错误数']} 处错误\n按错误类型统计：{summary['按类型统计']}")

            self.update_status("就绪")
        except Exception as e:
            messagebox.showerror("错误", f"纠错失败：{str(e)}")
            self.update_status("就绪")

    def do_auto_fix(self):
        """执行AI自动修正"""
        if not self.current_errors:
            messagebox.showwarning("提示", "请先执行学术纠错分析")
            return

        self.update_status("正在进行AI自动修正...")
        try:
            self.current_fix_result = self.fixer.fix_all(self.current_errors, self.current_b_result.get("content_flow"))

            log = self.fixer.generate_fix_log(self.current_fix_result)
            save_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                      filetypes=[("文本文件", "*.txt")],
                                                      initialfile="AI修正日志")
            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(log)

            messagebox.showinfo("修正完成", f"已修正 {self.current_fix_result.get('total_fixed', 0)} 处内容\n修正日志已保存")

            self.update_status("正在重新排版...")
            new_struct = self.fixer.rebuild_struct_data(self.current_fix_result, self.current_b_result)

            save_path = filedialog.asksaveasfilename(defaultextension=".docx",
                                                      filetypes=[("Word文档", "*.docx")],
                                                      initialfile="修正后论文")
            if save_path:
                style_params = self.get_style_params()
                if style_params and generate_final_doc(new_struct, save_path, style_params):
                    messagebox.showinfo("成功", "修正后论文已生成！")

            self.update_status("就绪")
        except Exception as e:
            messagebox.showerror("错误", f"修正失败：{str(e)}")
            self.update_status("就绪")

    def clear_errors(self):
        """清除错误记录"""
        self.current_errors = []
        self.current_b_result = None
        self.current_fix_result = None
        self.error_listbox.delete(0, tk.END)
        self.error_detail.delete("1.0", tk.END)

    def update_status(self, text):
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def get_style_params(self):
        try:
            return {
                "font_main": self.font_main_var.get(),
                "font_title": self.font_title_var.get(),
                "size_main": int(float(self.size_main_var.get())),
                "size_author": int(float(self.size_author_var.get())),
                "size_title1": int(float(self.size_title1_var.get())),
                "size_title2": int(float(self.size_title2_var.get())),
                "line_spacing": float(self.line_spacing_var.get()),
                "indent_char": int(self.indent_char_var.get())
            }
        except ValueError:
            messagebox.showerror("错误", "排版参数输入格式不正确")
            return None

    def do_clean_only(self):
        file_path = filedialog.askopenfilename(filetypes=[("Word文档", "*.docx")])
        if not file_path:
            return

        self.update_status("正在清洗文本...")
        try:
            result = read_and_clean_doc(file_path)
            save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本文件", "*.txt")])
            if not save_path:
                self.update_status("就绪")
                return

            with open(save_path, "w", encoding="utf-8") as f:
                f.write(result["clean_text"])

            messagebox.showinfo("成功", "文本清洗完成！")
            self.update_status("就绪")
        except Exception as e:
            messagebox.showerror("错误", f"文本清洗失败：{str(e)}")
            self.update_status("就绪")

    def do_identify_only(self):
        file_path = filedialog.askopenfilename(filetypes=[("Word文档", "*.docx")])
        if not file_path:
            return

        self.update_status("正在清洗文本...")
        try:
            a_result = read_and_clean_doc(file_path)

            self.update_status("正在AI识别信息...")
            b_result = process_text(a_result)
            self.current_b_result = b_result

            save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON文件", "*.json")])
            if not save_path:
                self.update_status("就绪")
                return

            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(b_result, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("成功", "AI信息识别完成！")
            self.update_status("就绪")
        except Exception as e:
            messagebox.showerror("错误", f"AI识别失败：{str(e)}")
            self.update_status("就绪")

    def do_full_format(self):
        file_path = filedialog.askopenfilename(filetypes=[("Word文档", "*.docx")])
        if not file_path:
            return

        style_params = self.get_style_params()
        if style_params is None:
            return

        self.update_status("正在清洗文本...")
        try:
            a_result = read_and_clean_doc(file_path)

            self.update_status("正在AI识别信息...")
            b_result = process_text(a_result)
            self.current_b_result = b_result

            save_path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word文档", "*.docx")])
            if not save_path:
                self.update_status("就绪")
                return

            self.update_status("正在排版导出...")
            flag = generate_final_doc(b_result, save_path, style_params)
            if flag:
                messagebox.showinfo("成功", "文档排版完成！")
            else:
                messagebox.showerror("失败", "文档生成失败")
            self.update_status("就绪")
        except Exception as e:
            messagebox.showerror("错误", f"排版失败：{str(e)}")
            self.update_status("就绪")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
