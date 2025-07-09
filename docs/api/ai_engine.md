# AI个性化引擎 API文档

## 概述

AI个性化引擎是一个用于代码优化和个性化的服务，它通过集成AI模型提供代码注释、重命名变量、代码优化、重构和语言转换等功能。

## 基础URL

所有API端点都以 `/api/ai` 为前缀。

## 认证

所有API请求都需要JWT令牌认证，通过HTTP头部的`Authorization`字段传递：

```
Authorization: Bearer <your_token>
```

## 数据模型

### AIModel

表示一个AI模型的配置。

| 字段 | 类型 | 描述 |
|------|------|------|
| id | integer | 模型ID |
| name | string | 模型名称 |
| provider | string | 提供商（如"OpenAI"） |
| model_id | string | 提供商内部的模型ID（如"gpt-3.5-turbo"） |
| api_key_name | string | 环境变量中API密钥的名称 |
| max_tokens | integer | 最大令牌数 |
| temperature | float | 温度参数 |
| is_active | boolean | 是否激活 |
| config | object | 额外配置 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### PersonalizationTemplate

表示一个代码个性化模板。

| 字段 | 类型 | 描述 |
|------|------|------|
| id | integer | 模板ID |
| name | string | 模板名称 |
| description | string | 模板描述 |
| prompt_template | string | 提示模板（含占位符） |
| task_type | string | 任务类型 |
| example_input | string | 示例输入代码 |
| example_output | string | 示例输出代码 |
| parameters | object | 模板参数 |
| is_active | boolean | 是否激活 |
| ai_model_id | integer | 关联的AI模型ID |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### PersonalizationLog

表示一次代码个性化的日志记录。

| 字段 | 类型 | 描述 |
|------|------|------|
| id | integer | 日志ID |
| user_id | integer | 用户ID |
| template_id | integer | 使用的模板ID |
| input_code | string | 输入代码 |
| output_code | string | 输出代码 |
| prompt_used | string | 使用的提示 |
| success | boolean | 是否成功 |
| processing_time | float | 处理时间（秒） |
| tokens_used | integer | 使用的令牌数 |
| error_message | string | 错误信息 |
| metadata | object | 元数据 |
| created_at | datetime | 创建时间 |

## API端点

### 模型管理

#### 获取模型列表

```
GET /api/ai/models
```

**查询参数：**

- `skip` (integer, 可选): 跳过的记录数，默认为0
- `limit` (integer, 可选): 返回的记录数，默认为100

**响应：**

```json
{
  "items": [
    {
      "id": 1,
      "name": "GPT-3.5",
      "provider": "OpenAI",
      "model_id": "gpt-3.5-turbo",
      "api_key_name": "OPENAI_API_KEY",
      "max_tokens": 4096,
      "temperature": 0.7,
      "is_active": true,
      "config": {},
      "created_at": "2023-09-01T12:00:00",
      "updated_at": "2023-09-01T12:00:00"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

#### 获取特定模型

```
GET /api/ai/models/{model_id}
```

**响应：**

```json
{
  "id": 1,
  "name": "GPT-3.5",
  "provider": "OpenAI",
  "model_id": "gpt-3.5-turbo",
  "api_key_name": "OPENAI_API_KEY",
  "max_tokens": 4096,
  "temperature": 0.7,
  "is_active": true,
  "config": {},
  "created_at": "2023-09-01T12:00:00",
  "updated_at": "2023-09-01T12:00:00"
}
```

#### 创建模型

```
POST /api/ai/models
```

**请求体：**

```json
{
  "name": "GPT-4",
  "provider": "OpenAI",
  "model_id": "gpt-4",
  "api_key_name": "OPENAI_API_KEY",
  "max_tokens": 8192,
  "temperature": 0.7,
  "is_active": true,
  "config": {}
}
```

**响应：**

```json
{
  "id": 2,
  "name": "GPT-4",
  "provider": "OpenAI",
  "model_id": "gpt-4",
  "api_key_name": "OPENAI_API_KEY",
  "max_tokens": 8192,
  "temperature": 0.7,
  "is_active": true,
  "config": {},
  "created_at": "2023-09-01T12:00:00",
  "updated_at": "2023-09-01T12:00:00"
}
```

#### 更新模型

```
PUT /api/ai/models/{model_id}
```

**请求体：**

```json
{
  "temperature": 0.5,
  "is_active": false
}
```

**响应：**

```json
{
  "id": 1,
  "name": "GPT-3.5",
  "provider": "OpenAI",
  "model_id": "gpt-3.5-turbo",
  "api_key_name": "OPENAI_API_KEY",
  "max_tokens": 4096,
  "temperature": 0.5,
  "is_active": false,
  "config": {},
  "created_at": "2023-09-01T12:00:00",
  "updated_at": "2023-09-01T13:00:00"
}
```

#### 删除模型

```
DELETE /api/ai/models/{model_id}
```

**响应：**

- 204 No Content：删除成功
- 404 Not Found：模型不存在
- 400 Bad Request：模型有关联的模板，无法删除

### 模板管理

#### 获取模板列表

```
GET /api/ai/templates
```

**查询参数：**

- `skip` (integer, 可选): 跳过的记录数，默认为0
- `limit` (integer, 可选): 返回的记录数，默认为100
- `task_type` (string, 可选): 按任务类型筛选

**响应：**

```json
{
  "items": [
    {
      "id": 1,
      "name": "Python注释模板",
      "description": "为Python代码添加注释",
      "prompt_template": "请为以下Python代码添加注释：\n{code}",
      "task_type": "add_comments",
      "example_input": "def hello(): pass",
      "example_output": "def hello():\n    \"\"\"Say hello\"\"\"\n    pass",
      "parameters": {"style": "docstring"},
      "is_active": true,
      "ai_model_id": 1,
      "created_at": "2023-09-01T12:00:00",
      "updated_at": "2023-09-01T12:00:00"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

#### 获取特定模板

```
GET /api/ai/templates/{template_id}
```

**响应：**

```json
{
  "id": 1,
  "name": "Python注释模板",
  "description": "为Python代码添加注释",
  "prompt_template": "请为以下Python代码添加注释：\n{code}",
  "task_type": "add_comments",
  "example_input": "def hello(): pass",
  "example_output": "def hello():\n    \"\"\"Say hello\"\"\"\n    pass",
  "parameters": {"style": "docstring"},
  "is_active": true,
  "ai_model_id": 1,
  "created_at": "2023-09-01T12:00:00",
  "updated_at": "2023-09-01T12:00:00"
}
```

#### 创建模板

```
POST /api/ai/templates
```

**请求体：**

```json
{
  "name": "JavaScript注释模板",
  "description": "为JavaScript代码添加注释",
  "prompt_template": "请为以下JavaScript代码添加注释：\n{code}",
  "task_type": "add_comments",
  "example_input": "function hello() { return true; }",
  "example_output": "/**\n * Says hello\n * @returns {boolean} Always true\n */\nfunction hello() { return true; }",
  "parameters": {"style": "jsdoc"},
  "is_active": true,
  "ai_model_id": 1
}
```

**响应：**

```json
{
  "id": 2,
  "name": "JavaScript注释模板",
  "description": "为JavaScript代码添加注释",
  "prompt_template": "请为以下JavaScript代码添加注释：\n{code}",
  "task_type": "add_comments",
  "example_input": "function hello() { return true; }",
  "example_output": "/**\n * Says hello\n * @returns {boolean} Always true\n */\nfunction hello() { return true; }",
  "parameters": {"style": "jsdoc"},
  "is_active": true,
  "ai_model_id": 1,
  "created_at": "2023-09-01T13:00:00",
  "updated_at": "2023-09-01T13:00:00"
}
```

#### 更新模板

```
PUT /api/ai/templates/{template_id}
```

**请求体：**

```json
{
  "description": "更新的描述",
  "is_active": false
}
```

**响应：**

```json
{
  "id": 1,
  "name": "Python注释模板",
  "description": "更新的描述",
  "prompt_template": "请为以下Python代码添加注释：\n{code}",
  "task_type": "add_comments",
  "example_input": "def hello(): pass",
  "example_output": "def hello():\n    \"\"\"Say hello\"\"\"\n    pass",
  "parameters": {"style": "docstring"},
  "is_active": false,
  "ai_model_id": 1,
  "created_at": "2023-09-01T12:00:00",
  "updated_at": "2023-09-01T14:00:00"
}
```

#### 删除模板

```
DELETE /api/ai/templates/{template_id}
```

**响应：**

- 204 No Content：删除成功
- 404 Not Found：模板不存在

### 代码个性化

#### 使用特定模板个性化代码

```
POST /api/ai/personalize
```

**请求体：**

```json
{
  "template_id": 1,
  "input_code": "def calculate(a, b):\n    return a + b",
  "parameters": {
    "language": "python",
    "style": "google"
  }
}
```

**响应：**

```json
{
  "output_code": "def calculate(a, b):\n    \"\"\"Calculates the sum of two numbers.\n    \n    Args:\n        a: First number to add.\n        b: Second number to add.\n        \n    Returns:\n        The sum of a and b.\n    \"\"\"\n    return a + b",
  "template_id": 1,
  "log_id": 1,
  "processing_time": 1.2,
  "tokens_used": 150
}
```

#### 为代码添加注释

```
POST /api/ai/code/add-comments
```

**请求体：**

```json
{
  "code": "def calculate(a, b):\n    return a + b",
  "language": "python",
  "style": "google"
}
```

**响应：**

```json
{
  "output_code": "def calculate(a, b):\n    \"\"\"Calculates the sum of two numbers.\n    \n    Args:\n        a: First number to add.\n        b: Second number to add.\n        \n    Returns:\n        The sum of a and b.\n    \"\"\"\n    return a + b"
}
```

#### 重命名变量

```
POST /api/ai/code/rename-variables
```

**请求体：**

```json
{
  "code": "def calc(x, y):\n    z = x + y\n    return z",
  "language": "python",
  "style": "descriptive"
}
```

**响应：**

```json
{
  "output_code": "def calculate(first_number, second_number):\n    result = first_number + second_number\n    return result"
}
```

#### 优化代码

```
POST /api/ai/code/optimize
```

**请求体：**

```json
{
  "code": "result = []\nfor i in range(10):\n    if i % 2 == 0:\n        result.append(i * 2)",
  "language": "python",
  "focus": "performance"
}
```

**响应：**

```json
{
  "output_code": "result = [i * 2 for i in range(0, 10, 2)]"
}
```

#### 重构代码

```
POST /api/ai/code/refactor
```

**请求体：**

```json
{
  "code": "class User:\n    def __init__(self, name):\n        self.name = name\n    \n    def get_name(self):\n        return self.name\n    \n    def set_name(self, name):\n        self.name = name",
  "language": "python",
  "refactor_type": "property",
  "instructions": "使用Python属性装饰器替换getter和setter"
}
```

**响应：**

```json
{
  "output_code": "class User:\n    def __init__(self, name):\n        self._name = name\n    \n    @property\n    def name(self):\n        return self._name\n    \n    @name.setter\n    def name(self, value):\n        self._name = value"
}
```

#### 转换代码语言

```
POST /api/ai/code/convert
```

**请求体：**

```json
{
  "code": "function add(a, b) {\n  return a + b;\n}",
  "source_language": "javascript",
  "target_language": "python"
}
```

**响应：**

```json
{
  "output_code": "def add(a, b):\n    return a + b"
}
```

#### 获取支持的任务类型

```
GET /api/ai/code/task-types
```

**响应：**

```json
{
  "task_types": {
    "add_comments": "添加注释",
    "rename_variables": "重命名变量",
    "optimize_code": "优化代码",
    "refactor_code": "重构代码",
    "convert_language": "转换语言"
  }
}
```

### 其他端点

#### 获取个性化设置

```
GET /api/ai/settings
```

**响应：**

```json
{
  "models": [
    {
      "id": 1,
      "name": "GPT-3.5",
      "provider": "OpenAI",
      "model_id": "gpt-3.5-turbo"
    }
  ],
  "task_types": {
    "add_comments": [
      {
        "id": 1,
        "name": "Python注释模板",
        "description": "为Python代码添加注释"
      }
    ],
    "rename_variables": [
      {
        "id": 3,
        "name": "变量重命名模板",
        "description": "重命名变量使其更具描述性"
      }
    ]
  }
}
```

#### 初始化默认设置

```
POST /api/ai/initialize
```

**响应：**

```json
{
  "models_created": 1,
  "templates_created": 5,
  "success": true
}
```

#### 获取用户历史记录

```
GET /api/ai/user/history
```

**查询参数：**

- `limit` (integer, 可选): 返回的记录数，默认为10
- `offset` (integer, 可选): 偏移量，默认为0

**响应：**

```json
{
  "total": 1,
  "logs": [
    {
      "id": 1,
      "template_name": "Python注释模板",
      "task_type": "add_comments",
      "success": true,
      "created_at": "2023-09-01T12:00:00",
      "processing_time": 1.2,
      "tokens_used": 150
    }
  ],
  "offset": 0,
  "limit": 10
}
```

#### 保存用户偏好设置

```
POST /api/ai/user/preferences
```

**请求体：**

```json
{
  "preference_type": "model",
  "preference_value": {
    "default_model_id": 1,
    "default_language": "python"
  }
}
```

**响应：**

```json
{
  "success": true,
  "user_id": 1,
  "preference_type": "model",
  "message": "用户偏好设置已保存"
}
```

## 错误处理

当发生错误时，API将返回适当的HTTP状态代码和JSON错误响应：

```json
{
  "detail": "错误信息"
}
```

### 常见错误代码

- `400 Bad Request`: 请求参数无效
- `401 Unauthorized`: 认证失败
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 参数验证失败
- `429 Too Many Requests`: 请求过于频繁
- `500 Internal Server Error`: 服务器内部错误
- `502 Bad Gateway`: AI提供商服务不可用
- `503 Service Unavailable`: 服务暂时不可用
- `504 Gateway Timeout`: 请求超时

## 使用示例

### Python客户端示例

```python
import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/ai"

# 认证令牌
TOKEN = "your_jwt_token"

# 请求头
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def add_comments(code, language="python", style="google"):
    """为代码添加注释"""
    url = f"{BASE_URL}/code/add-comments"
    data = {
        "code": code,
        "language": language,
        "style": style
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()["output_code"]
    else:
        print(f"错误: {response.status_code} - {response.text}")
        return None

# 使用示例
code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

commented_code = add_comments(code)
print(commented_code)
``` 