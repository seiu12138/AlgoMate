# AlgoMate - AI Coding Agent Guide

## 项目概述

**AlgoMate** 是一个基于 **LangGraph + ReAct 架构** 的智能算法辅导系统，采用前后端分离架构。系统能够自动分析算法题目、编写代码、执行测试并在出错时自主修复。支持**会话持久化**和**RAG知识增强**。

### 核心功能
- **RAG 问答模式**: 基于向量检索的算法知识问答
- **Agent 解题模式**: ReAct 架构的智能算法解题（自动分析、编码、测试、修复）
- **会话管理**: 多会话隔离、历史记录持久化、自动标题生成
- **代码执行沙箱**: 支持 Python/C++/Java 的安全执行环境

---

## 技术架构

### 技术栈

#### 后端 (Backend)
| 技术 | 用途 |
|------|------|
| **FastAPI** | Web 框架 |
| **LangChain / LangGraph** | Agent 框架 |
| **ChromaDB** | 向量数据库 |
| **DashScope** | 通义千问模型 (qwen3-max) |
| **SSE (Server-Sent Events)** | 流式响应 |
| **Pydantic** | 数据验证 |

#### 前端 (Frontend)
| 技术 | 用途 |
|------|------|
| **React 19 + TypeScript** | UI 框架 |
| **Vite** | 构建工具 |
| **Tailwind CSS 4** | 样式框架 |
| **Zustand** | 状态管理 |
| **Axios** | HTTP 客户端 |

---

## 项目结构

```
AlgoMate/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── api/
│   │   │   ├── routes.py    # API 路由定义
│   │   │   └── schemas.py   # Pydantic 数据模型
│   │   ├── agent/           # ReAct Agent 核心
│   │   │   ├── react_agent.py      # Agent 主类
│   │   │   ├── nodes.py            # 工作流节点
│   │   │   └── state.py            # Agent 状态定义
│   │   ├── rag/             # RAG 知识库
│   │   │   ├── rag.py              # RAG 服务
│   │   │   ├── vector_stores.py    # 向量存储
│   │   │   └── conversation_rag.py # 会话 RAG
│   │   ├── core/            # 核心模块
│   │   │   ├── session.py          # 会话管理（FastAPI依赖）
│   │   │   └── session_manager.py  # 会话管理器
│   │   ├── tools/           # 代码执行工具
│   │   │   └── code_executor.py    # 代码执行沙箱
│   │   ├── utils/           # 工具模块
│   │   │   ├── config_handler.py   # 配置处理
│   │   │   ├── prompts_loader.py   # Prompt 加载
│   │   │   └── logger_handler.py   # 日志处理
│   │   ├── config/          # YAML 配置文件
│   │   │   ├── model.yaml          # 模型配置
│   │   │   ├── agent.yaml          # Agent 配置
│   │   │   ├── chroma.yaml         # ChromaDB 配置
│   │   │   └── prompts.yaml        # Prompt 路径配置
│   │   ├── prompts/         # Prompt 模板文件 (.txt)
│   │   └── data/            # 数据存储目录
│   ├── requirements.txt     # Python 依赖
│   ├── requirements-py38.txt # Python 3.8 兼容版
│   ├── .env.example         # 环境变量示例
│   └── start.py             # 启动脚本
│
├── frontend/                # React + TypeScript 前端
│   ├── src/
│   │   ├── components/      # React 组件
│   │   │   ├── Sidebar/     # 侧边栏（会话列表、模式切换）
│   │   │   ├── Chat/        # 聊天组件
│   │   │   ├── Input/       # 输入组件
│   │   │   └── common/      # 通用组件
│   │   ├── stores/          # Zustand 状态管理
│   │   │   ├── chatStore.ts       # 聊天状态
│   │   │   └── configStore.ts     # 配置状态
│   │   ├── api/             # API 封装
│   │   │   ├── client.ts          # Axios 客户端
│   │   │   ├── rag.ts             # RAG API
│   │   │   └── agent.ts           # Agent API
│   │   ├── services/        # 会话服务
│   │   │   └── sessionAPI.ts      # 会话 API
│   │   ├── types/           # TypeScript 类型定义
│   │   │   └── index.ts
│   │   ├── styles/          # 全局样式
│   │   └── App.tsx          # 应用入口
│   ├── package.json
│   ├── tsconfig.json        # TypeScript 配置
│   ├── vite.config.ts       # Vite 配置
│   └── eslint.config.js     # ESLint 配置
│
├── data/                    # 会话数据持久化
│   └── chat_history/
│       ├── sessions.json           # 会话索引
│       ├── rag/                    # RAG 会话数据
│       └── agent/                  # Agent 会话数据
│
└── README.md / API.md / AGENT_FEATURE.md
```

---

## 开发环境配置

### 环境变量

#### 必需
```powershell
# DashScope API Key (通义千问)
$env:DASHSCOPE_API_KEY="your-api-key"
```

#### 可选
```powershell
# 服务器配置
$env:HOST="0.0.0.0"
$env:PORT="8000"
$env:RELOAD="true"
```

### 配置文件 (backend/app/config/)

#### model.yaml
```yaml
embedding_model_name: "text-embedding-v1"
chat_model_name: "qwen3-max"
```

#### agent.yaml
```yaml
max_iterations: 5
code_execution_timeout: 10
```

#### chroma.yaml
```yaml
collection_name: "algomate"
persist_directory: "./data/chromd_db"
md5_hex_store: "./data/md5.text"
data_path: "./data/knowledge_base"
allow_knowledge_file_type: [".txt", ".pdf"]
```

---

## 构建和运行命令

### 后端

```powershell
# 进入后端目录
cd backend

# 安装依赖 (Python 3.9+ 推荐)
pip install -r requirements.txt

# Python 3.8 用户
pip install -r requirements-py38.txt

# 设置 API Key
$env:DASHSCOPE_API_KEY="your-api-key"

# 启动服务 (使用启动脚本)
python start.py

# 或使用 uvicorn 直接启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务地址：
- API: http://localhost:8000
- 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/health

### 前端

```powershell
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint
```

前端地址：http://localhost:5173

---

## 代码风格指南

### Python (后端)

#### 编码规范
- 遵循 **PEP 8** 规范
- 文件头使用统一的编码声明：`# -*- coding: utf-8 -*-`
- 使用类型注解（Type Hints）
- 文档字符串使用 Google 风格或 reStructuredText 风格

#### 模块导入顺序
1. 标准库导入
2. 第三方库导入
3. 本地模块导入

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/16
# @File     : example.py
# @Project  : AlgoMate

import os
import sys
from typing import Dict, Any

from fastapi import FastAPI
from langchain_core.messages import HumanMessage

from app.config import settings
from app.utils.logger import log_agent
```

#### 命名规范
- 类名：PascalCase (e.g., `AlgoMateAgent`, `SessionManager`)
- 函数/变量：snake_case (e.g., `create_session`, `problem_description`)
- 常量：UPPER_CASE (e.g., `DEFAULT_TIMEOUT`)
- 私有函数/变量：_leading_underscore (e.g., `_build_graph`)

### TypeScript/React (前端)

#### 编码规范
- ESLint 配置使用 `@eslint/js` + `typescript-eslint` + `react-hooks` + `react-refresh`
- 使用函数组件 + Hooks
- 类型定义统一放在 `src/types/index.ts`

#### 命名规范
- 组件名：PascalCase (e.g., `ChatInput`, `MessageList`)
- 函数/变量：camelCase (e.g., `useChatStore`, `currentSessionId`)
- 类型/接口：PascalCase (e.g., `AgentResult`, `ConversationSession`)
- Hook：以 `use` 开头 (e.g., `useChatStore`)

#### 组件结构
```typescript
// 导入顺序：React -> 第三方 -> 本地
import { useState, useCallback } from 'react';
import axios from 'axios';

import { useChatStore } from '../stores/chatStore';
import type { Message } from '../types';

// 组件定义
interface Props {
    sessionId: string;
}

export function MyComponent({ sessionId }: Props) {
    // hooks
    const { messages, addMessage } = useChatStore();
    
    // state
    const [isLoading, setIsLoading] = useState(false);
    
    // handlers
    const handleClick = useCallback(() => {
        // ...
    }, []);
    
    // render
    return (
        <div className="...">
            {/* ... */}
        </div>
    );
}
```

---

## 测试说明

### 后端测试

```powershell
# 测试代码执行器
cd backend
python -c "from tools.code_executor import execute_code; print(execute_code('print(1+1)', 'python'))"

# 运行 pytest (如果有测试文件)
pytest
```

### 前端测试

```powershell
cd frontend

# 代码检查
npm run lint

# TypeScript 类型检查
npx tsc --noEmit
```

---

## API 架构

### 端点概览

| 端点 | 方法 | 描述 | 模式 |
|------|------|------|------|
| `/api/health` | GET | 健康检查 | - |
| `/api/config` | GET | 获取配置 | - |
| `/api/sessions` | GET | 获取会话列表 | 会话管理 |
| `/api/sessions` | POST | 创建新会话 | 会话管理 |
| `/api/sessions/{id}` | GET | 获取会话详情 | 会话管理 |
| `/api/sessions/{id}` | PATCH | 更新会话标题 | 会话管理 |
| `/api/sessions/{id}` | DELETE | 删除会话 | 会话管理 |
| `/api/sessions/{id}/summarize` | POST | 生成会话摘要 | 会话管理 |
| `/api/rag/chat` | POST | RAG 问答 (SSE) | RAG |
| `/api/agent/solve` | POST | Agent 解题 (SSE) | Agent |

### SSE 流式响应

#### RAG 事件类型
- `token`: 生成的文本片段
- `title_update`: 自动生成的会话标题
- `done`: 完成标记
- `error`: 错误信息

#### Agent 事件类型
- `node_start`: 节点开始执行
- `progress`: 进度更新 (0-100)
- `node_complete`: 节点完成
- `title_update`: 自动生成的会话标题
- `complete`: 最终结果

---

## Agent 工作流架构

```
用户输入
    |
    v
┌─────────────┐
│  analyze    │ ── 分析题目（输入、输出、约束）
└──────┬──────┘
       |
       v
┌─────────────┐
│ generate_   │ ── 生成测试用例
│ test_cases  │
└──────┬──────┘
       |
       v
┌─────────────┐
│  validate_  │ ── 验证测试用例
│ test_cases  │
└──────┬──────┘
       |
       v
┌─────────────┐
│  generate_  │ ── 生成代码
│    code     │
└──────┬──────┘
       |
       v
┌─────────────┐
│   execute_  │ ── 执行代码
│    code     │
└──────┬──────┘
       |
       v
┌─────────────┐
│   analyze_  │ ── 分析结果
│   result    │
└──────┬──────┘
       |
       ├── 成功 ──> finish ──> 生成最终答案
       |
       └─ 失败 ──> fix_code ──┐
                         ^    |
                         └────┘
                      (最多 5 次迭代)
```

### 状态定义 (AgentState)
- `problem_description`: 题目描述
- `problem_analysis`: AI 分析结果
- `generated_code`: 生成的代码
- `language`: 编程语言
- `test_cases`: 测试用例列表
- `execution_result`: 执行结果
- `execution_history`: 执行历史
- `iteration_count`: 当前迭代次数
- `is_solved`: 是否已解决

---

## 数据存储

### 会话持久化

会话数据存储在 `data/chat_history/` 目录：

```
data/chat_history/
├── sessions.json              # 会话索引
├── rag/
│   └── session_{uuid}.json    # RAG 会话数据
└── agent/
    └── session_{uuid}.json    # Agent 会话数据
```

### 会话索引格式
```json
[
  {
    "id": "uuid",
    "type": "rag|agent",
    "title": "会话标题",
    "createdAt": "2024-01-01T00:00:00",
    "updatedAt": "2024-01-01T00:00:00",
    "messageCount": 10,
    "lastMessagePreview": "最后消息预览..."
  }
]
```

### 消息格式
```json
{
  "id": "uuid",
  "role": "user|assistant|system",
  "content": "消息内容",
  "timestamp": "2024-01-01T00:00:00",
  "metadata": {}
}
```

---

## 安全注意事项

### 代码执行安全
- 使用 `SubprocessSandbox` 进行代码隔离
- 默认超时 10 秒，防止无限循环
- 内存限制 256MB
- 临时目录隔离，执行后清理
- **注意**: 生产环境建议使用 Docker 沙箱

### API Key 管理
- 通过环境变量传递，不硬编码
- `.env` 文件已加入 `.gitignore`

### CORS 配置
后端配置了允许的源：
- http://localhost:5173 (Vite 开发)
- http://localhost:4173 (Vite Preview)
- http://localhost:3000 (React 开发)
- http://localhost:8080

---

## 开发注意事项

### 添加新 API 端点

1. 在 `backend/app/api/schemas.py` 中添加 Pydantic 模型
2. 在 `backend/app/api/routes.py` 中添加路由处理函数
3. 路由已通过 `router` 在 `main.py` 中注册

### 添加前端组件

1. 在 `frontend/src/components/` 下创建组件目录
2. 在 `frontend/src/types/index.ts` 中添加类型定义（如需要）
3. 在 `frontend/src/api/` 中添加 API 调用（如需要）

### 修改 Agent 行为

- 修改工作流: `backend/app/agent/react_agent.py`
- 修改节点逻辑: `backend/app/agent/nodes.py`
- 修改 Prompt: `backend/app/prompts/*.txt`
- 修改配置: `backend/app/config/agent.yaml`

### 调试技巧

```powershell
# 后端详细日志
uvicorn app.main:app --reload --log-level debug

# 查看日志文件
backend/app/logs/
├── agent_YYYYMMDD.log
├── agent.nodes_YYYYMMDD.log
└── agent.react_YYYYMMDD.log
```

---

## 部署说明

### 后端部署

```powershell
# 生产模式启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 前端部署

```powershell
# 构建生产版本
cd frontend
npm run build

# 部署 dist/ 目录到静态服务器
```

---

## 相关文档

- [API 文档](./API.md) - 详细 API 参考
- [Agent 功能文档](./AGENT_FEATURE.md) - Agent 功能实现细节
- [后端文档](./backend/README.md) - 后端启动和 API 说明
- [前端文档](./frontend/README.md) - 前端开发说明

---

*AlgoMate - 让算法学习更高效！*
