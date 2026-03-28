# AlgoMate API 文档

## 概述

AlgoMate API 是基于 FastAPI 构建的 RESTful API，提供智能算法辅导服务。

**基础 URL**: `http://localhost:8000`

**API 文档访问**:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI Schema: `http://localhost:8000/openapi.json`

---

## 功能模块

| 模块 | 描述 |
|------|------|
| **Health** | 健康检查和系统状态 |
| **Sessions** | 会话管理 - 创建、查询、更新、删除 |
| **RAG** | 知识库问答 (检索增强生成) |
| **Agent** | 智能 Agent - 自动解题、编码、测试、修复 |
| **System** | 系统配置和工具 |

---

## 健康检查

### GET `/api/health`

检查 API 服务运行状态。

**响应**:
```json
{
  "status": "ok",
  "service": "AlgoMate API"
}
```

---

## 会话管理

### GET `/api/sessions`

获取所有会话列表。

**查询参数**:
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| type | string | 否 | 过滤类型: "rag" 或 "agent" |

**响应**:
```json
{
  "sessions": [
    {
      "id": "uuid",
      "type": "rag",
      "title": "会话标题",
      "createdAt": "2024-01-01T00:00:00",
      "updatedAt": "2024-01-01T00:00:00",
      "messageCount": 10,
      "lastMessagePreview": "最后消息预览..."
    }
  ]
}
```

---

### POST `/api/sessions`

创建新会话。

**请求体**:
```json
{
  "type": "rag",
  "title": "可选标题"
}
```

**响应**:
```json
{
  "session": {
    "id": "uuid",
    "type": "rag",
    "title": "New Conversation",
    "createdAt": "...",
    "updatedAt": "...",
    "messageCount": 0,
    "lastMessagePreview": ""
  }
}
```

---

### GET `/api/sessions/{session_id}`

获取会话详情（包含消息）。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| session_id | string | 会话ID |

**响应**:
```json
{
  "session": { ... },
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "消息内容",
      "timestamp": "...",
      "metadata": {}
    }
  ]
}
```

**错误**:
- `404` - 会话不存在

---

### PATCH `/api/sessions/{session_id}`

更新会话标题。

**请求体**:
```json
{
  "title": "新标题"
}
```

**响应**:
```json
{
  "success": true,
  "message": "Session 'xxx' title updated"
}
```

---

### DELETE `/api/sessions/{session_id}`

删除会话。

**响应**:
```json
{
  "success": true,
  "message": "Session 'xxx' deleted"
}
```

---

### POST `/api/sessions/{session_id}/summarize`

生成会话摘要标题。

**响应**:
```json
{
  "title": "生成的标题"
}
```

---

## RAG 问答

### POST `/api/rag/chat`

RAG 知识问答（流式 SSE）。

**请求体**:
```json
{
  "message": "什么是动态规划？",
  "session_id": "uuid"
}
```

**响应** (SSE 流):
```
data: {"type": "token", "content": "动态规划是一种..."}

data: {"type": "title_update", "title": "动态规划简介"}

data: {"type": "done"}
```

**事件类型**:
| 类型 | 描述 |
|------|------|
| token | 生成的文本片段 |
| title_update | 首次对话时发送的标题 |
| done | 完成标记 |
| error | 错误信息 |

---

## Agent 解题

### POST `/api/agent/solve`

Agent 智能解题（流式 SSE）。

**请求体**:
```json
{
  "problem": "两数之和：给定数组 nums 和 target...",
  "language": "python",
  "max_iterations": 5,
  "session_id": "uuid"
}
```

**参数说明**:
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| problem | string | 是 | 题目描述 |
| language | string | 否 | 编程语言: python/cpp/java，默认 python |
| max_iterations | int | 否 | 最大迭代次数 1-10，默认 5 |
| session_id | string | 是 | 会话ID |

**响应** (SSE 流):
```
data: {"type": "node_start", "node": "analyze", "status": "🔍 分析题目..."}

data: {"type": "progress", "value": 15}

data: {"type": "node_complete", "node": "analyze", "output": {...}}

data: {"type": "title_update", "title": "两数之和"}

data: {"type": "complete", "result": {...}}
```

**执行节点**:
1. `analyze` - 分析题目
2. `generate_test_cases` - 生成测试用例
3. `validate_test_cases` - 验证测试用例
4. `generate_code` - 生成代码
5. `execute_code` - 执行代码
6. `analyze_result` - 分析结果
7. `fix_code` - 修复代码（如需要）
8. `finish` - 生成最终答案

**最终结果**:
```json
{
  "type": "complete",
  "result": {
    "final_answer": "解答内容...",
    "generated_code": "代码...",
    "is_solved": true,
    "iteration_count": 3,
    "execution_history": [...]
  }
}
```

---

## 系统配置

### GET `/api/config`

获取系统配置信息。

**响应**:
```json
{
  "languages": ["python", "cpp", "java"],
  "max_iterations_range": [1, 10]
}
```

---

## 代码示例

### Python 调用示例

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 创建会话
response = requests.post(
    f"{BASE_URL}/api/sessions",
    json={"type": "rag"}
)
session_id = response.json()["session"]["id"]

# RAG 问答
response = requests.post(
    f"{BASE_URL}/api/rag/chat",
    json={
        "message": "什么是动态规划？",
        "session_id": session_id
    },
    stream=True
)

for line in response.iter_lines():
    if line.startswith(b"data: "):
        data = json.loads(line[6:])
        print(data)
```

### cURL 示例

```bash
# 健康检查
curl http://localhost:8000/api/health

# 创建会话
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"type": "agent"}'

# Agent 解题
curl -X POST http://localhost:8000/api/agent/solve \
  -H "Content-Type: application/json" \
  -d '{
    "problem": "两数之和",
    "language": "python",
    "session_id": "your-session-id"
  }'
```

---

## 错误处理

**HTTP 状态码**:
| 状态码 | 描述 |
|--------|------|
| 200 | 成功 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

**错误响应格式**:
```json
{
  "detail": "错误描述信息"
}
```

---

## 数据模型

### Session
```json
{
  "id": "string (uuid)",
  "type": "rag | agent",
  "title": "string",
  "createdAt": "string (ISO datetime)",
  "updatedAt": "string (ISO datetime)",
  "messageCount": "integer",
  "lastMessagePreview": "string"
}
```

### Message
```json
{
  "id": "string (uuid)",
  "role": "user | assistant | system",
  "content": "string",
  "timestamp": "string (ISO datetime)",
  "metadata": "object (optional)"
}
```

---

## 版本信息

- **当前版本**: 0.1.0
- **最后更新**: 2024
- **仓库**: https://github.com/seiu12138/AlgoMate
