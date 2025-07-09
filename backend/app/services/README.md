# 服务目录

此目录包含所有业务逻辑和服务实现。

## 结构

- `ai_service.py`: AI个性化服务
- `repository_service.py`: 零件仓库管理服务
- `packaging_service.py`: 项目打包服务
- `report_service.py`: 报告生成服务

## 用途

服务层实现所有业务逻辑，包括：

1. 处理来自API层的请求
2. 执行业务规则和逻辑
3. 与数据库交互
4. 调用外部服务和API

服务层是应用程序的核心，包含所有业务规则和领域逻辑。 