# API目录

此目录包含所有API路由和端点定义。

## 结构

- `routes/`: API路由模块
- `endpoints/`: API端点实现
- `schemas/`: 请求和响应模式定义

## 用途

API层负责处理HTTP请求和响应，包括：

1. 路由定义
2. 输入验证
3. 响应格式化
4. 错误处理

API层不应包含业务逻辑，而应调用服务层来处理业务逻辑。 