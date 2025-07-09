#!/usr/bin/env python
"""
简单的WeasyPrint PDF导出测试
"""

from weasyprint import HTML, CSS

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
    </style>
</head>
<body>
    <h1>PDF导出测试文档</h1>
    <p>这是一个测试文档，用于验证WeasyPrint的PDF导出功能。</p>
    <p>如果您能看到这个PDF文件，说明PDF导出功能工作正常！</p>
</body>
</html>
"""

try:
    # 生成PDF
    print("开始生成PDF...")
    HTML(string=html_content).write_pdf("simple_test.pdf")
    print("PDF成功生成: simple_test.pdf")
except Exception as e:
    print(f"PDF生成失败: {str(e)}") 