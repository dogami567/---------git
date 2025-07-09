import pytest
import os
from sqlalchemy.orm import Session
from backend.app.services.report_service import ReportService, ReportTemplate, ReportSection, ReportFormat
from backend.app.db.database import SessionLocal

# 定义测试输出目录
TEST_OUTPUT_DIR = "reports/test_artifacts"


@pytest.fixture(scope="module")
def db() -> Session:
    """
    提供一个数据库会话的pytest fixture
    """
    # 确保测试输出目录存在
    if not os.path.exists(TEST_OUTPUT_DIR):
        os.makedirs(TEST_OUTPUT_DIR)
        
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@pytest.fixture(scope="module")
def report_service(db: Session) -> ReportService:
    """
    提供ReportService实例的pytest fixture
    """
    return ReportService(db)


def create_sample_report_template() -> ReportTemplate:
    """
    创建一个用于测试的简单报告模板
    """
    template = ReportTemplate(title="验证测试报告", description="这是一个用于验证报告生成流程的自动化测试报告。")
    
    # 添加一个简单的文本部分
    template.add_section(
        ReportSection(
            title="第一章：简介",
            content="本部分测试基本的文本段落生成。",
            level=1
        )
    )
    
    # 添加一个包含代码块的部分
    code_content = """
def hello_world():
    print("Hello, world!")
"""
    code_section = ReportSection(
        title="第二章：代码示例",
        content="本部分测试代码块的格式化与高亮。",
        level=1
    )
    code_section.add_subsection(
        ReportSection(
            title="Python示例",
            content=f"```python\n{code_content}\n```",
            level=2
        )
    )
    template.add_section(code_section)
    
    return template


def test_generate_all_report_formats(report_service: ReportService):
    """
    测试：验证所有支持的报告格式（Markdown, DOCX, PDF）是否都能成功生成。
    """
    # 1. 准备数据
    template = create_sample_report_template()
    sample_data = {
        "project_name": "测试项目",
        "author": "自动化测试脚本"
    }

    # 2. 遍历所有格式进行测试
    for report_format in ReportFormat:
        output_filename = f"verification_report.{report_format.value}"
        output_path = os.path.join(TEST_OUTPUT_DIR, output_filename)
        
        # 3. 调用报告生成函数
        try:
            generated_path = report_service.generate_report(
                template=template,
                data=sample_data,
                format=report_format,
                output_path=output_path,
                use_cache=False  # 测试时禁用缓存
            )

            # 4. 断言检查
            assert generated_path is not None, f"生成路径不应为None ({report_format.value})"
            assert os.path.exists(generated_path), f"报告文件未被创建于: {generated_path} ({report_format.value})"
            assert os.path.getsize(generated_path) > 0, f"报告文件为空: {generated_path} ({report_format.value})"
            
            print(f"✅ {report_format.value.upper()} 报告已成功生成于: {generated_path}")

        except Exception as e:
            pytest.fail(f"生成 {report_format.value.upper()} 报告时发生意外错误: {e}") 