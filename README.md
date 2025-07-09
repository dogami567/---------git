# 大学生竞赛信息聚合与订阅平台

本项目旨在为大学生提供竞赛信息聚合与订阅服务，帮助学生更便捷地获取、管理和参与各类竞赛活动。

## 功能特性

- 竞赛信息浏览与搜索
- 个性化竞赛推荐
- 竞赛订阅与提醒
- 团队协作功能
- 竞赛资源共享
- 项目报告生成

## 技术栈

- **前端**：React, TypeScript, Ant Design
- **后端**：Python, FastAPI, SQLAlchemy
- **数据库**：PostgreSQL
- **部署**：Docker, Nginx
- **其他工具**：Git, GitHub Actions

## 项目结构

```
.
├── backend/                # 后端代码
│   ├── app/                # 应用代码
│   │   ├── api/            # API端点
│   │   ├── core/           # 核心功能
│   │   ├── db/             # 数据库相关
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模式
│   │   └── services/       # 业务服务
│   ├── scripts/            # 脚本工具
│   └── tests/              # 测试代码
├── frontend/               # 前端代码
├── docs/                   # 文档
└── reports/                # 生成的报告
```

## 安装与运行

### 后端

1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

2. 运行开发服务器

```bash
uvicorn app.main:app --reload
```

### 前端

1. 安装依赖

```bash
cd frontend
npm install
```

2. 运行开发服务器

```bash
npm run dev
```

## 报告生成功能

本平台提供强大的报告生成功能，支持以下特性：

- 多种报告模板（项目报告、竞赛分析报告等）
- 支持Markdown和DOCX格式输出
- 自定义变量替换
- 图表和表格支持
- API接口支持

### 使用示例

```python
from backend.app.services.report_service import ReportService, ReportTemplate, ReportFormat

# 创建报告服务
report_service = ReportService()

# 获取项目报告模板
template = report_service.create_project_report_template()

# 准备报告数据
data = {
    "project_name": "大学生竞赛信息聚合与订阅平台",
    "author": "开发团队",
    # 其他数据...
}

# 生成报告
output_path = report_service.generate_report(
    template=template,
    data=data,
    format=ReportFormat.MARKDOWN,
    include_toc=True
)

print(f"报告已生成：{output_path}")
```

### API端点

- `POST /api/v1/reports/generate` - 生成自定义报告
- `POST /api/v1/reports/project` - 生成项目报告
- `GET /api/v1/reports/templates/default` - 获取默认模板

## 贡献指南

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的改动 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件 