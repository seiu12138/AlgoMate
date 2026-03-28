# 🤖 AlgoMate - 智能算法辅导系统

> 前后端分离架构 | React + FastAPI

AlgoMate 是一个基于 **LangGraph + ReAct 架构** 的智能算法辅导系统，能够自动分析算法题目、编写代码、执行测试并在出错时自主修复。

---

## 📁 项目结构

```
algomate/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── api/             # API 路由
│   │   ├── agent/           # ReAct Agent 核心
│   │   ├── rag/             # RAG 知识库
│   │   ├── tools/           # 代码执行沙箱
│   │   ├── utils/           # 工具模块
│   │   ├── config/          # YAML 配置
│   │   └── data/            # 数据目录
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                # React + TypeScript 前端
│   ├── src/
│   │   ├── components/      # React 组件
│   │   ├── stores/          # Zustand 状态管理
│   │   ├── api/             # API 封装
│   │   └── App.tsx
│   ├── package.json
│   └── README.md
│
├── logs/                    # 日志目录
├── AGENT_FEATURE.md         # 功能文档
└── README.md                # 本文档
```

---

## 🚀 快速开始

### 1. 启动后端

```powershell
cd backend

# 安装依赖
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
| 🧠 **ReAct Agent** | 推理-行动循环，自动解决问题 |
| 📚 **RAG 知识增强** | 向量检索的算法知识库问答 |
| 🖥️ **代码沙箱** | Python/C++/Java 安全执行环境 |
| 🔄 **自动修复** | 代码失败自动分析修复 |
| 🧪 **智能测试** | 自动生成边界测试用例 |
| 💬 **流式展示** | 实时展示 Agent 思考过程 |

---

## 🛠️ 技术栈

### 后端
- **FastAPI** - Web 框架
- **LangChain / LangGraph** - Agent 框架
- **ChromaDB** - 向量数据库
- **DashScope** - 通义千问模型

### 前端
- **React 18 + TypeScript**
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **Zustand** - 状态管理
- **SSE** - 服务器发送事件

---

## 📡 API 端点

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
$env:DASHSCOPE_API_KEY="your-dashscope-api-key"
```

---

## 📄 相关文档

- [功能文档](./AGENT_FEATURE.md) - Agent 功能详细说明
- [后端文档](./backend/README.md) - 后端启动和 API 说明
- [前端文档](./frontend/README.md) - 前端开发说明

---

## 📜 License

MIT License © 2026 AlgoMate

---

> 🌟 **AlgoMate** - 让算法学习更高效！
