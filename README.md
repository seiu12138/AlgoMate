# 🤖 AlgoMate - 智能算法辅导系统

> 前后端分离架构 | React + FastAPI | 会话持久化 | RAG增强

AlgoMate 是一个基于 **LangGraph + ReAct 架构** 的智能算法辅导系统，能够自动分析算法题目、编写代码、执行测试并在出错时自主修复。支持**会话持久化**、**顺序检索增强RAG**和**编号引用来源追踪**。

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
│   │   │   ├── enhanced_rag.py     # 增强RAG（顺序检索+引用追踪）
│   │   │   ├── conversation_rag.py # 会话RAG
│   │   │   └── retrievers/         # 检索器
│   │   │       ├── sequential_retriever.py  # 顺序检索器
│   │   │       ├── vector_retriever.py      # 向量检索器
│   │   │       └── web_retriever.py         # 网页检索器
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
│   │   │   │   ├── MessageItem.tsx        # 消息展示（含来源）
│   │   │   │   └── SourceTaggedContent.tsx # 引用渲染组件
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
| 🧠 **ReAct Agent** | 推理-行动循环，自动解题、编码、测试、修复 |
| 📚 **顺序检索 RAG** | RAG → 网页搜索 → 直接LLM，严格优先级控制 |
| 🔢 **编号引用** | 角标格式 `[1][2]` 标注来源，支持点击跳转 |
| 🌐 **网页来源展示** | 消息顶部显示网页来源 URL 列表 |
| 🖥️ **代码沙箱** | Python/C++/Java 安全执行环境 |
| 💾 **会话持久化** | 自动保存对话历史，支持多会话管理 |
| 💬 **流式展示** | 实时展示 Agent 思考过程和生成内容 |

---

## 🛠️ 技术栈

### 后端
- **FastAPI** - Web 框架
- **LangChain / LangGraph** - Agent 框架
- **ChromaDB** - 向量数据库
- **DashScope** - 通义千问模型
- **DuckDuckGo** - 网页搜索

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
| `/api/rag/chat` | POST | RAG 问答 (SSE，带来源追踪) |
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
- 消息历史（角色、内容、元数据、来源信息）
- 可选的Agent结果（代码、执行历史等）

---

## 🔍 RAG 顺序检索流程

```
用户提问
    ↓
[Step 1] 向量数据库检索 (RAG)
    ↓
结果数 >= min_vector_results(默认2)?
    ↓ 是              ↓ 否
返回 RAG结果    [Step 2] 网页搜索
    [1][2]...           ↓
                    有结果?
                        ↓ 是      ↓ 否
                    返回网页结果   直接询问LLM
                    [1][2]...    (无引用)
```

**特点：**
- 严格控制来源，不会混合 RAG 和网页结果
- 使用编号引用 `[1]`, `[2]` 标注来源
- 网页来源在消息顶部显示可点击的 URL 列表

---

## 📄 相关文档

- [API 文档](./API.md) - 详细 API 说明
- [后端文档](./backend/README.md) - 后端启动和开发说明
- [前端文档](./frontend/README.md) - 前端开发说明

---

## 📜 License

MIT License © 2026 AlgoMate

---

> 🌟 **AlgoMate** - 让算法学习更高效！
