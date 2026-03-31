# 🤖 AlgoMate - 智能算法辅导系统

> 前后端分离架构 | React + FastAPI | 会话持久化 | RAG增强

AlgoMate 是一个基于 **LangGraph + ReAct 架构** 的智能算法辅导系统，能够自动分析算法题目、编写代码、执行测试并在出错时自主修复。支持**会话持久化**和**RAG知识增强**。

---

## 📁 项目结构

```
algomate/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── api/             # API 路由
│   │   ├── agent/           # ReAct Agent 核心
│   │   │   ├── react_agent.py      # ReAct Agent核心
│   │   │   ├── nodes.py            # 工作流节点
│   │   │   └── state.py            # Agent状态定义
│   │   ├── rag/             # RAG 知识库
│   │   │   ├── rag.py              # 基础RAG
│   │   │   └── conversation_rag.py # 会话RAG
│   │   ├── core/            # 核心模块
│   │   │   └── session_manager.py  # 会话管理
│   │   ├── tools/           # 代码执行沙箱
│   │   ├── utils/           # 工具模块
│   │   └── config/          # YAML 配置
│   └── requirements.txt
│
├── frontend/                # React + TypeScript 前端
│   ├── src/
│   │   ├── components/      # React 组件
│   │   │   ├── Sidebar/     # 侧边栏(含会话列表)
│   │   │   ├── Chat/        # 聊天组件
│   │   │   └── Input/       # 输入组件
│   │   ├── stores/          # Zustand 状态管理
│   │   ├── api/             # API 封装
│   │   └── services/        # 会话API服务
│   └── package.json
│
├── data/                    # 数据目录
│   └── chat_history/        # 会话持久化数据
├── logs/                    # 日志目录
└── README.md                # 本文档
```

---

## 🚀 快速开始

### 1. 启动后端

```powershell
cd backend

# 安装依赖 (Python 3.9+)
pip install -r requirements.txt

# 设置 API Key
$env:DASHSCOPE_API_KEY="your-api-key"

# 启动服务
python start.py
```

后端服务: http://localhost:8000  
API 文档: http://localhost:8000/docs

### 2. 启动前端

```powershell
cd frontend

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

前端地址: http://localhost:5173

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 💾 **会话持久化** | 自动保存对话历史，支持多会话管理 |
| 🧠 **ReAct Agent** | 推理-行动循环，自动解决问题 |
| 📚 **RAG 知识增强** | 向量检索 + 会话历史双重增强 |
| 🎯 **智能存储** | 助手回复分块存入ChromaDB，支持检索 |
| 🧠 **向量检索** | Agent分析题目时检索历史相关问答 |
| 🖥️ **代码沙箱** | Python/C++/Java 安全执行环境 |
| 🔄 **自动修复** | 代码失败自动分析修复 |
| 🧪 **智能测试** | 自动生成边界测试用例 |
| 💬 **流式展示** | 实时展示 Agent 思考过程 |
| 📝 **自动标题** | 基于首条消息自动生成会话标题 |

---

## 🛠️ 技术栈

### 后端
- **FastAPI** - Web 框架
- **LangChain / LangGraph** - Agent 框架
- **ChromaDB** - 向量数据库
- **DashScope** - 通义千问模型
- **ChromaDB** - 向量数据库存储问答知识
- **文件存储** - JSON 文件会话持久化

### 前端
- **React 18 + TypeScript**
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **Zustand** - 状态管理
- **SSE** - 服务器发送事件

---

## 📡 API 端点

### 会话管理
| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/sessions` | GET | 获取会话列表 |
| `/api/sessions` | POST | 创建新会话 |
| `/api/sessions/{id}` | GET | 获取会话详情 |
| `/api/sessions/{id}` | PATCH | 更新会话标题 |
| `/api/sessions/{id}` | DELETE | 删除会话 |
| `/api/sessions/{id}/summarize` | POST | 生成会话摘要 |

### 核心功能
| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/config` | GET | 获取配置 |
| `/api/rag/chat` | POST | RAG 问答 (SSE) |
| `/api/agent/solve` | POST | Agent 解题 (SSE) |
| `/api/session/clear` | POST | 清空会话 |

---

## 🔧 环境变量

```powershell
# 必需的 API Key
$env:DASHSCOPE_API_KEY="your-dashscope-api-key"

# 可选配置
$env:HOST="0.0.0.0"
$env:PORT="8000"
```

---

## 🗄️ 会话持久化

AlgoMate 使用文件系统存储会话数据：

```
data/chat_history/
├── sessions.json              # 会话索引
├── rag/
│   └── session_{uuid}.json    # RAG 会话数据
└── agent/
    └── session_{uuid}.json    # Agent 会话数据
```

每个会话包含：
- 会话元数据（ID、类型、标题、时间戳）
- 消息历史（角色、内容、元数据）
- 可选的Agent结果（代码、执行历史等）

---

## 📄 相关文档

- [会话持久化规范](./CONVERSATION_PERSISTENCE_SPEC.md) - 会话系统详细设计
- [后端文档](./backend/README.md) - 后端启动和 API 说明
- [前端文档](./frontend/README.md) - 前端开发说明

---

## 📜 License

MIT License © 2026 AlgoMate

---

> 🌟 **AlgoMate** - 让算法学习更高效！
