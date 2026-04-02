# AlgoMate - AGENTS.md

> 本文档面向 AI 编码助手，包含项目架构、开发规范和重要实现细节。
> 语言：中文 / Language: Chinese

---

## 项目概述

**AlgoMate** 是一个基于 **LangGraph + ReAct 架构** 的智能算法辅导系统，采用前后端分离架构：

- **后端**: FastAPI + LangChain/LangGraph + ChromaDB
- **前端**: React 18 + TypeScript + Vite + Tailwind CSS

### 核心功能

1. **RAG 模式** (检索增强生成): 基于向量检索的算法知识问答
2. **Agent 模式** (智能解题): ReAct 循环自动分析题目、编码、测试、修复
3. **会话持久化**: JSON 文件存储对话历史，支持多会话管理

---

## 技术栈详情

### 后端 (`backend/`)

| 组件 | 用途 | 版本 |
|------|------|------|
| FastAPI | Web 框架 | >=0.110.0 |
| Uvicorn | ASGI 服务器 | >=0.27.0 |
| LangChain/LangGraph | Agent 框架 | >=0.2.0 / >=0.1.0 |
| ChromaDB | 向量数据库 | >=0.4.0 |
| DashScope | 通义千问模型 API | - |
| sse-starlette | SSE 流式响应 | >=2.0.0 |
| Pydantic | 数据验证 | >=2.0.0 |
| PyYAML | 配置管理 | >=6.0.0 |

### 前端 (`frontend/`)

| 组件 | 用途 | 版本 |
|------|------|------|
| React | UI 框架 | ^19.2.4 |
| TypeScript | 类型系统 | ~5.9.3 |
| Vite | 构建工具 | ^8.0.1 |
| Tailwind CSS | 样式框架 | ^4.2.2 |
| Zustand | 状态管理 | ^5.0.12 |
| Axios | HTTP 客户端 | ^1.14.0 |
| react-markdown | Markdown 渲染 | ^10.1.0 |
| lucide-react | 图标库 | ^1.7.0 |

---

## 项目结构

```
algomate/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py            # FastAPI 入口
│   │   ├── api/
│   │   │   ├── routes.py      # API 路由定义
│   │   │   └── schemas.py     # Pydantic 模型
│   │   ├── agent/             # ReAct Agent 核心
│   │   │   ├── react_agent.py # Agent 主类
│   │   │   ├── nodes.py       # 工作流节点实现
│   │   │   └── state.py       # Agent 状态定义
│   │   ├── rag/               # RAG 服务
│   │   │   ├── rag.py         # 基础 RAG
│   │   │   ├── conversation_rag.py  # 会话增强 RAG
│   │   │   └── vector_stores.py     # 向量存储
│   │   ├── core/
│   │   │   ├── session.py           # 会话管理 (运行时)
│   │   │   └── session_manager.py   # 持久化会话管理
│   │   ├── tools/
│   │   │   └── code_executor.py     # 代码执行沙箱
│   │   ├── utils/
│   │   │   ├── config_handler.py    # 配置加载
│   │   │   ├── file_handler.py      # 文件处理
│   │   │   ├── logger_handler.py    # 日志管理
│   │   │   └── prompts_loader.py    # Prompt 加载
│   │   ├── config/            # YAML 配置文件
│   │   │   ├── agent.yaml     # Agent 配置
│   │   │   ├── model.yaml     # 模型配置
│   │   │   ├── chroma.yaml    # ChromaDB 配置
│   │   │   └── prompts.yaml   # Prompt 路径配置
│   │   ├── prompts/           # Prompt 模板文件 (.txt)
│   │   └── data/              # 数据目录
│   │       ├── knowledge_base/      # 知识库 PDF/TXT
│   │       ├── chromd_db/           # ChromaDB 持久化
│   │       └── logs/                # 日志文件
│   ├── data/chat_history/     # 会话持久化存储
│   ├── requirements.txt       # Python 依赖
│   └── start.py              # 启动脚本
│
├── frontend/                  # React 前端
│   ├── src/
│   │   ├── components/        # React 组件
│   │   │   ├── Sidebar/       # 侧边栏（会话列表）
│   │   │   ├── Chat/          # 聊天组件
│   │   │   ├── Input/         # 输入组件
│   │   │   └── common/        # 通用组件
│   │   ├── stores/
│   │   │   ├── chatStore.ts   # 聊天状态 (Zustand)
│   │   │   └── configStore.ts # 配置状态
│   │   ├── services/
│   │   │   └── sessionAPI.ts  # 会话 API 封装
│   │   ├── api/
│   │   │   ├── client.ts      # HTTP 客户端
│   │   │   ├── rag.ts         # RAG API
│   │   │   └── agent.ts       # Agent API
│   │   ├── types/
│   │   │   └── index.ts       # TypeScript 类型定义
│   │   ├── styles/
│   │   │   └── globals.css    # 全局样式
│   │   ├── App.tsx           # 应用入口
│   │   └── main.tsx          # React 挂载点
│   ├── package.json          # NPM 依赖
│   ├── vite.config.ts        # Vite 配置
│   ├── tsconfig.json         # TypeScript 配置
│   └── eslint.config.js      # ESLint 配置
│
├── data/chat_history/         # 会话数据（运行时生成）
├── API.md                     # API 文档
└── README.md                  # 项目说明
```

---

## 构建和运行命令

### 后端

```powershell
# 进入后端目录
cd backend

# 安装依赖 (Python 3.9+)
pip install -r requirements.txt

# 设置必需的环境变量
$env:DASHSCOPE_API_KEY="your-api-key"

# 启动服务（推荐）
python start.py

# 或使用 uvicorn 直接启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 前端

```powershell
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint
```

### 访问地址

- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/health

---

## 环境变量

### 必需

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `DASHSCOPE_API_KEY` | DashScope API Key (通义千问) | `sk-xxx...` |

### 可选

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `HOST` | 服务器绑定地址 | `0.0.0.0` |
| `PORT` | 服务器端口 | `8000` |
| `RELOAD` | 开发模式热重载 | `true` |

---

## 配置文件说明

### 后端 YAML 配置 (`backend/app/config/`)

| 文件 | 用途 | 关键配置项 |
|------|------|-----------|
| `model.yaml` | AI 模型配置 | `chat_model_name`, `embedding_model_name` |
| `agent.yaml` | Agent 参数 | `max_iterations`, `code_execution_timeout` |
| `chroma.yaml` | 向量数据库 | `collection_name`, `persist_directory` |
| `prompts.yaml` | Prompt 路径 | 各场景 Prompt 文件映射 |
| `session.yaml` | 会话配置 | 存储路径等 |
| `storage.yaml` | 存储配置 | 文件存储参数 |
| `search.yaml` | 检索配置 | 检索参数 |
| `splitter.yaml` | 文本分割 | 分块参数 |

### 前端配置

| 文件 | 用途 |
|------|------|
| `vite.config.ts` | Vite 构建配置 |
| `tsconfig.json` | TypeScript 编译配置 |
| `eslint.config.js` | ESLint 规则 |
| `postcss.config.js` | PostCSS/Tailwind 配置 |

---

## 代码风格指南

### Python (后端)

- **编码**: UTF-8，文件头包含 `#!/usr/bin/env python` 和 `# -*- coding: utf-8 -*-
- **文档字符串**: 使用 Google 风格 docstring
- **类型注解**: 函数参数和返回值必须添加类型注解
- **命名规范**:
  - 类名: `PascalCase`
  - 函数/变量: `snake_case`
  - 常量: `UPPER_SNAKE_CASE`
  - 私有: `_leading_underscore`

示例:
```python
def create_session(self, session_type: str, title: str = None) -> Dict[str, Any]:
    """
    创建新会话

    Args:
        session_type: 会话类型（"rag" 或 "agent"）
        title: 会话标题，默认为 "New Conversation"

    Returns:
        新创建的会话元数据
    """
    ...
```

### TypeScript (前端)

- **类型**: 优先使用 `type` 定义类型，复杂对象使用 `interface`
- **组件**: 函数组件，使用箭头函数
- **命名规范**:
  - 类型/接口: `PascalCase`
  - 函数/变量: `camelCase`
  - 组件: `PascalCase`
  - 常量: `UPPER_SNAKE_CASE`

示例:
```typescript
export interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: number;
}

export const useChatStore = create<ChatState>((set, get) => ({
    // ...
}));
```

---

## 关键架构模式

### 后端架构

1. **ReAct Agent 工作流** (`agent/`):
   ```
   analyze → generate_test_cases → validate_test_cases → generate_code 
   → execute_code → analyze_result → [fix_code → execute_code] → finish
   ```

2. **RAG 流程** (`rag/`):
   - 向量检索 + 会话历史双重增强
   - 助手回复相关性检测后存入向量库

3. **会话管理** (`core/session_manager.py`):
   - 基于文件的 JSON 持久化
   - 路径: `data/chat_history/{rag,agent}/session_{uuid}.json`
   - 索引: `data/chat_history/sessions.json`

### 前端架构

1. **状态管理**: Zustand 存储，按功能拆分 store
2. **API 通信**: 原生 fetch + SSE (Server-Sent Events) 流式响应
3. **组件组织**: 按功能域分组（Sidebar, Chat, Input）

---

## 数据流说明

### Agent 解题流程

1. 前端发送 POST `/api/agent/solve` (SSE)
2. 后端通过 `session_manager` 验证/创建会话
3. `AlgoMateAgent` 执行 LangGraph 工作流
4. 每个节点通过 SSE 发送 `node_start`, `progress`, `node_complete` 事件
5. 最终结果存储到会话，发送 `complete` 事件

### RAG 问答流程

1. 前端发送 POST `/api/rag/chat` (SSE)
2. 用户消息存入会话（不入向量库）
3. `ConversationRAG` 获取增强上下文（向量检索 + 历史）
4. 流式生成响应，通过 SSE 发送 `token` 事件
5. 助手回复异步存入向量库（相关性检测后）

---

## 测试策略

当前项目测试覆盖有限，主要依赖:

1. **手动测试**: 通过 Swagger UI (`/docs`) 测试 API
2. **前端开发服务器**: 热重载实时验证

### 建议添加的测试

```powershell
# 后端 (pytest)
cd backend
pytest tests/

# 前端 (Vitest 或 Jest)
cd frontend
npm test
```

---

## 安全注意事项

1. **API Key 管理**:
   - `DASHSCOPE_API_KEY` 必须设置，否则 AI 功能不可用
   - 永远不要将 API Key 提交到代码仓库

2. **代码执行沙箱** (`tools/code_executor.py`):
   - 当前使用本地进程执行，存在安全风险
   - 建议生产环境使用 Docker 容器隔离

3. **CORS 配置**:
   - 开发环境允许 `localhost:5173` 等前端端口
   - 生产环境应限制为实际域名

4. **输入验证**:
   - 所有 API 输入通过 Pydantic 模型验证
   - 文件上传限制类型（PDF, TXT）

5. **会话数据**:
   - 会话文件存储在本地文件系统
   - 注意文件权限和数据备份

---

## 开发提示

### 添加新 API 端点

1. 在 `app/api/schemas.py` 添加请求/响应模型
2. 在 `app/api/routes.py` 实现路由处理函数
3. 路由自动注册（已通过 `app.include_router`）

### 修改 Agent 行为

1. 节点逻辑在 `agent/nodes.py`
2. 工作流图在 `agent/react_agent.py` 的 `_build_graph()`
3. Prompt 模板在 `app/prompts/` 目录

### 前端添加新组件

1. 组件放入 `src/components/{功能域}/`
2. 类型定义添加到 `src/types/index.ts`
3. 状态管理在对应 store 中添加

---

## 故障排查

### 后端启动失败

```powershell
# 检查 Python 版本 (需要 3.9+)
python --version

# 检查依赖安装
pip list | grep fastapi

# 检查 API Key
$env:DASHSCOPE_API_KEY
```

### 前端连接后端失败

- 确认后端运行在 `localhost:8000`
- 检查浏览器控制台 CORS 错误
- 查看 `sessionAPI.ts` 中的 `API_BASE` 配置

### 向量数据库问题

- 检查 `backend/app/data/chromd_db/` 目录权限
- 删除该目录可重置向量数据库（会丢失知识库数据）

---

## 版本信息

- **当前版本**: 0.1.0
- **最后更新**: 2024
- **仓库**: https://github.com/seiu12138/AlgoMate
