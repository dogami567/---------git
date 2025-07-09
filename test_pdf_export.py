#!/usr/bin/env python
"""
测试PDF导出功能
用于测试WeasyPrint库的PDF导出功能
"""

import os
from pathlib import Path
from weasyprint import HTML, CSS

def test_simple_pdf_export():
    """测试简单的PDF导出功能"""
    print("开始测试简单的PDF导出功能...")
    
    # 创建一个简单的HTML内容
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>PDF导出测试</title>
        <style>
            body { font-family: sans-serif; margin: 2cm; }
            h1 { color: #005599; text-align: center; }
            .content { border: 1px solid #cccccc; padding: 1em; }
            .footer { text-align: center; margin-top: 2em; font-size: 0.8em; color: #666666; }
        </style>
    </head>
    <body>
        <h1>PDF导出测试文档</h1>
        <div class="content">
            <p>这是一个测试文档，用于验证WeasyPrint的PDF导出功能。</p>
            <p>如果您能看到这个PDF文件，说明PDF导出功能工作正常！</p>
            <ul>
                <li>支持完整的HTML和CSS</li>
                <li>支持UTF-8字符: 你好，世界！</li>
                <li>支持表格和其他复杂布局</li>
            </ul>
        </div>
        <div class="footer">
            生成时间: 2025年7月7日
        </div>
    </body>
    </html>
    """
    
    # 输出文件路径
    output_path = Path("test_output.pdf")
    
    try:
        # 生成PDF
        HTML(string=html_content).write_pdf(output_path)
        print(f"PDF成功生成: {output_path.absolute()}")
        return True
    except Exception as e:
        print(f"PDF生成失败: {str(e)}")
        return False

def test_report_pdf_export():
    """测试从Markdown生成PDF的功能"""
    print("\n开始测试从Markdown生成PDF的功能...")
    
    # 创建一个Markdown内容
    markdown_content = """
    # 测试报告
    
    ## 摘要
    
    这是一个从Markdown生成的测试报告。
    
    ## 测试结果
    
    | 测试项 | 状态 | 备注 |
    |-------|------|------|
    | 功能测试 | 通过 | 所有功能正常 |
    | 性能测试 | 通过 | 响应时间在预期范围内 |
    | 安全测试 | 通过 | 未发现安全漏洞 |
    
    ## 结论
    
    测试通过，可以进行部署。
    """
    
    # 将Markdown转换为HTML
    try:
        import markdown
        html_content = markdown.markdown(markdown_content, extensions=['tables'])
        
        # 添加样式
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Markdown测试报告</title>
            <style>
                body {{ font-family: sans-serif; margin: 2cm; }}
                h1 {{ color: #005599; text-align: center; }}
                h2 {{ color: #0077bb; margin-top: 1.5em; }}
                table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # 输出文件路径
        output_path = Path("test_report.pdf")
        
        # 生成PDF
        HTML(string=styled_html).write_pdf(output_path)
        print(f"Markdown报告PDF成功生成: {output_path.absolute()}")
        return True
    except ImportError:
        print("未安装markdown库，无法进行Markdown测试")
        return False
    except Exception as e:
        print(f"Markdown报告PDF生成失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== PDF导出功能测试 ===")
    
    simple_result = test_simple_pdf_export()
    report_result = test_report_pdf_export()
    
    print("\n=== 测试结果汇总 ===")
    print(f"简单PDF导出: {'成功' if simple_result else '失败'}")
    print(f"Markdown报告导出: {'成功' if report_result else '失败'}")
    
    if simple_result and report_result:
        print("\n所有测试通过！PDF导出功能正常工作。")
    else:
        print("\n部分测试失败，请检查错误信息。") 