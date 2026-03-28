# AlgoMate Backend

AlgoMate 后端 API 服务 - 基于 FastAPI + LangGraph + ReAct 架构的智能算法辅导系统。

## 功能特性

- **RAG 问答**: 基于向量检索的算法知识问答（流式 SSE 响应）
- **Agent 解题**: ReAct 架构的智能算法解题（流式节点状态推送）
- **会话管理**: 支持多会话隔离和历史记录
- **CORS 支持**: 允许前端跨域访问

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py        # API 路由
│   │   └── schemas.py       # Pydantic 模型
│   ├── core/
│   │   ├── __init__.py
│   │   └── session.py       # 会话管理
│   ├── agent/               # ReAct Agent 实现
│   ├── rag/                 # RAG 服务
│   ├── tools/               # 代码执行工具
│   ├── utils/               # 工具函数
│   ├── config/              # 配置文件
│   ├── prompts/             # Prompt 模板
│   └── data/                # 数据目录
├── requirements.txt         # 依赖列表
└── README.md                # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

确保已设置 DashScope API Key（用于通义千问模型）：

```bash
# Linux/macOS
export DASHSCOPE_API_KEY=your_api_key_here

# Windows PowerShell
$env:DASHSCOPE_API_KEY="your_api_key_here"

# Windows CMD
set DASHSCOPE_API_KEY=your_api_key_here
```

### 3. 启动服务

```bash
# 开发模式（热重载）
python -m app.main

# 或使用 uvicorn 直接启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

服务启动后访问：
- API 文档: http://localhost:8000/docs
- API 根路径: http://localhost:8000/api
- 健康检查: http://localhost:8000/api/health

## API 端点

### 健康检查
```http
GET /api/health
```

### 获取配置
```http
GET /api/config
```

Response:
```json
{
  "languages": ["python", "cpp", "java"],
  "max_iterations_range": [1, 10]
}
```

### RAG 问答（流式 SSE）
```http
POST /api/rag/chat
Content-Type: application/json

{
  "message": "什么是动态规划？",
  "session_id": "user-123"
}
```

Response (SSE):
```
data: {"type": "token", "content": "动态规划"}
data: {"type": "token", "content": "是一种"}
data: {"type": "done"}
```

### Agent 解题（流式 SSE）
```http
POST /api/agent/solve
Content-Type: application/json

{
  "problem": "两数之和：给定数组 nums 和 target...",
  "language": "python",
  "max_iterations": 5,
  "session_id": "user-123"
}
```

Response (SSE):
```
data: {"type": "node_start", "node": "analyze", "status": "🔍 分析题目..."}
data: {"type": "progress", "value": 10}
data: {"type": "node_complete", "node": "analyze", "output": {...}}
data: {"type": "complete", "result": {...}}
```

### 清空会话
```http
POST /api/session/clear
Content-Type: application/json

{
  "session_id": "user-123"
}
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `HOST` | 服务器绑定地址 | `0.0.0.0` |
| `PORT` | 服务器端口 | `8000` |
| `RELOAD` | 开发模式热重载 | `true` |
| `DASHSCOPE_API_KEY` | DashScope API Key | - |

## 前端集成示例

### RAG 聊天
```javascript
const eventSource = new EventSource('/api/rag/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: '什么是动态规划？', session_id: 'user-1' })
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'token') {
    console.log(data.content);
  } else if (data.type === 'done') {
    eventSource.close();
  }
};
```

### Agent 解题
```javascript
const eventSource = new EventSource('/api/agent/solve', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    problem: '两数之和...',
    language: 'python',
    max_iterations: 5,
    session_id: 'user-1'
  })
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch (data.type) {
    case 'node_start':
      console.log('节点开始:', data.node, data.status);
      break;
    case 'progress':
      console.log('进度:', data.value);
      break;
    case 'complete':
      console.log('结果:', data.result);
      eventSource.close();
      break;
  }
};
```

## 注意事项

1. **API Key**: 需要设置 `DASHSCOPE_API_KEY` 环境变量才能正常使用 AI 功能
2. **会话隔离**: 不同 `session_id` 的会话相互独立
3. **流式响应**: RAG 和 Agent 接口使用 SSE 流式响应，前端需要正确处理
4. **超时设置**: Agent 解题可能需要较长时间，建议前端设置合适的超时时间

## 开发说明

### 添加新接口

1. 在 `app/api/schemas.py` 中添加请求/响应模型
2. 在 `app/api/routes.py` 中添加路由处理函数
3. 在 `app/main.py` 中确保路由已注册（通常在 `routes.py` 中已完成）

### 调试

```bash
# 启用详细日志
uvicorn app.main:app --reload --log-level debug
```
