import os
import sys
import platform

# --- Start of Fix ---
# 确保在任何其他导入之前修复 PATH
def fix_windows_gtk_path():
    """
    在Windows上，如果GTK运行时已安装但未在PATH中，则手动添加。
    这对于让 weasyprint 找到其C库依赖项至关重要。
    """
    if platform.system() == "Windows":
        gtk_path = r"C:\Program Files\GTK3-Runtime Win64\bin"
        if os.path.exists(gtk_path) and gtk_path not in os.environ.get('PATH', ''):
            print(f"INFO: 手动将GTK路径添加到环境变量: {gtk_path}")
            os.environ['PATH'] = gtk_path + os.pathsep + os.environ.get('PATH', '')
        else:
            print("INFO: GTK 路径已在环境变量中或不存在，无需添加。")

fix_windows_gtk_path()

# 将项目根目录添加到Python路径中，以解决模块导入问题
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"INFO: 将项目根目录添加到 sys.path: {project_root}")
# --- End of Fix ---

from backend.app.db.database import SessionLocal
from backend.app.services.report_service import ReportService, ReportTemplate, ReportSection, ReportFormat

def create_sample_report_template() -> ReportTemplate:
    """创建一个用于测试的简单报告模板"""
    template = ReportTemplate(
        title="Verification Report Template",
        description="A template for verifying the report generation pipeline."
    )
    
    sections_data = [
        {"title": "# 验证测试报告", "content": "这是一个用于验证报告生成流程的自动化测试报告。"},
        {"title": "# 第一章：简介", "content": "本部分测试基本的文本段落生成。"},
        {"title": "# 第二章：代码示例", "content": "本部分测试代码块的格式化与高亮。\n\n## Python示例\n\n```python\ndef hello_world():\n    print(\"Hello, world!\")\n```"},
    ]
    
    for sec_data in sections_data:
        template.add_section(ReportSection(title=sec_data["title"], content=sec_data["content"]))
        
    return template

def run_test():
    """执行PDF报告生成测试"""
    print("\n--- 开始手动PDF生成测试 ---")
    db = None
    try:
        # 设置数据库会话
        db = SessionLocal()
        report_service = ReportService(db)

        # 准备数据
        template = create_sample_report_template()
        sample_data = {
            "project_name": "手动测试项目",
            "author": "手动测试脚本"
        }
        output_dir = "reports/test_artifacts"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_filename = "manual_verification_report.pdf"
        output_path = os.path.join(output_dir, output_filename)

        print(f"尝试生成PDF报告于: {output_path}")

        # 调用报告生成函数
        generated_path = report_service.generate_report(
            template=template,
            data=sample_data,
            format=ReportFormat.PDF,
            output_path=output_path,
            use_cache=False
        )

        # 检查结果
        if os.path.exists(generated_path) and os.path.getsize(generated_path) > 0:
            print(f"\n✅ ✅ ✅ 成功! ✅ ✅ ✅")
            print(f"PDF报告已成功生成于: {generated_path}")
        else:
            print(f"\n❌ 失败! 报告文件未创建或为空。")

    except Exception as e:
        print(f"\n❌ ❌ ❌ 发生致命错误! ❌ ❌ ❌")
        import traceback
        print("错误类型:", type(e).__name__)
        print("错误信息:", e)
        print("\n--- 堆栈跟踪 ---")
        traceback.print_exc()

    finally:
        if db:
            db.close()
        print("\n--- 测试结束 ---")

if __name__ == "__main__":
    run_test() 