# 项目根目录 test_c.py （修改为B模块真实输出格式）
from module_c.formatter_exporter import generate_final_doc

# 完全复刻终端里B模块输出的数据结构
mock_b_data = {
    "task_id": "test_001",
    "正文": "人工智能在教育领域的应用越来越广泛。李华等人对此展开研究[1]。",
    "作者": "李华",
    "参考文献": [
        "李华. 智能教育研究[J]. 计算机应用,2024,10(2):20-28."
    ]
}

# 调用函数
save_file_path = "./test_file/result_test.docx"
result = generate_final_doc(mock_b_data, save_file_path)

# 输出测试信息
if result:
    print("✅ 测试成功！文档已生成：", save_file_path)
else:
    print("❌ 测试失败！查看控制台异常信息")