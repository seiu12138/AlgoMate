# AlgoMate - 智能算法辅导 AI Agent 🤖

AlgoMate 是一个基于 **LangGraph + ReAct 架构** 的智能算法辅导系统，能够自动分析算法题目、编写代码、执行测试并在出错时自主修复。

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🧠 **ReAct Agent** | 基于推理-行动的自主循环，自动解决问题 |
| 📝 **代码沙箱** | 支持 Python/C++/Java 的安全代码执行环境 |
| 🔄 **自动修复** | 代码失败后自动分析错误并修复（最多5次迭代） |
| 🧪 **测试生成** | 自动生成边界测试用例 |
| 📚 **知识增强** | 基于 RAG 的算法知识检索 |
| 🎨 **流式展示** | Web 界面实时展示 Agent 思考过程 |

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                     AlgoMate AI Agent                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ 题目分析Agent │───▶│ 代码生成Agent │───▶│ 测试验证Agent │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                    │                    │             │
│         └────────────────────┼────────────────────┘             │
│                              ▼                                  │
│                     ┌─────────────────┐                        │
│                     │  ReAct 循环器   │ ◀── 失败时自动修复     │
│                     └────────┬────────┘                        │
│                              │                                  │
│         ┌────────────────────┼────────────────────┐            │
│         ▼                    ▼                    ▼            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ 知识检索Agent │    │ 复杂度分析   │    │ 解答生成     │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
├─────────────────────────────────────────────────────────────────┤
│  工具层：代码沙箱(Docker/Subprocess) | Chroma向量库 | LLM API   │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

依赖包括：
- `langchain` + `langgraph`: Agent 框架
- `streamlit`: Web 界面
- `chromadb`: 向量数据库
- `dashscope`: 通义千问模型（或使用 OpenAI API）

### 2. 配置模型

编辑 `config/config_data.py`:

```python
# 使用 DashScope (通义千问)
embedding_model_name = "text-embedding-v4"
chat_model_name = "qwen3-max"

# 或使用 OpenAI
# chat_model_name = "gpt-4"
```

设置 API Key:
```bash
export DASHSCOPE_API_KEY="your-api-key"
# 或
export OPENAI_API_KEY="your-api-key"
```

### 3. 运行 Web 界面

```bash
streamlit run algomate_web.py
```

访问 `http://localhost:8501`

## 📖 使用指南

### 模式一：RAG 问答模式

适合算法概念学习、知识点查询。

1. 先上传算法知识文档（TXT 格式）
2. 在 Web 界面选择 "RAG 问答模式"
3. 输入问题，如：
   - "解释一下动态规划的核心思想"
   - "二分查找的时间复杂度是多少？"

### 模式二：Agent 解题模式

适合实际编程练习。

1. 在 Web 界面选择 "Agent 解题模式"
2. 选择编程语言（Python/C++/Java）
3. 输入题目描述，如：

```
题目：两数之和

给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。

示例：
输入：nums = [2,7,11,15], target = 9
输出：[0,1]
```

4. Agent 会自动：
   - 🔍 分析题目
   - 📝 生成测试用例
   - 💻 编写代码
   - ▶️ 执行测试
   - 🔧 如有错误自动修复（最多5次）
   - ✨ 生成完整解答报告

## 📁 项目结构

```
algomate/
├── agent/                  # ReAct Agent 核心
│   ├── __init__.py
│   ├── react_agent.py      # 主 Agent 类
│   ├── state.py            # Agent 状态定义
│   └── nodes.py            # ReAct 节点实现
├── tools/                  # 工具集
│   ├── __init__.py
│   └── code_executor.py    # 代码执行沙箱
├── rag/                    # RAG 功能
│   ├── rag.py
│   ├── vector_stores.py
│   └── file_history_store.py
├── db/                     # 知识库管理
│   ├── knowledge_base.py
│   └── file_uploader.py
├── config/
│   └── config_data.py      # 配置
├── algomate_web.py         # Web 界面
├── test_agent.py           # 测试脚本
└── requirements.txt        # 依赖
```

## 🔧 代码执行沙箱

项目实现了两层代码执行安全机制：

### 1. Docker 沙箱（推荐生产环境）

- 完全容器隔离
- 资源限制（CPU、内存、时间）
- 无网络访问
- 文件系统隔离

需要安装 Docker：
```bash
pip install docker
```

### 2. Subprocess 沙箱（本地演示）

- 超时控制
- 内存限制
- 临时目录执行
- 进程树清理

适合本地快速测试。

## 🔄 ReAct 循环流程

```
用户输入题目
    │
    ▼
┌─────────────┐
│ 1. 分析题目 │ ──▶ 提取类型、约束、边界
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 2. 生成测试 │ ──▶ 自动生成测试用例
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 3. 编写代码 │ ──▶ 生成初始代码
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 4. 执行测试 │ ──▶ 运行代码，检查输出
└──────┬──────┘
       │
       ├──▶ 成功 ──▶ 生成解答报告 ──▶ 结束
       │
       └──▶ 失败 ──▶ 分析错误 ──▶ 修复代码
                              │
                              └──▶ 回到步骤 4
                              （最多 5 次）
```

## 📝 简历项目描述

### 项目名称
**AlgoMate - 智能算法辅导 AI Agent 系统**

### 项目概述
设计并实现基于 **LangGraph + ReAct 架构** 的多 Agent 协作系统，集成代码沙箱、自主推理循环、知识增强 RAG 等核心技术，为算法学习者提供从题目理解到代码优化的全流程智能辅导。

### 核心职责与亮点

| 模块 | 技术栈 | 项目亮点 |
|------|--------|----------|
| **ReAct Agent 架构** | LangGraph + Pydantic | 实现推理-行动循环，支持多轮代码生成-测试-修复，平均 2.3 轮迭代达到正确解 |
| **代码沙箱系统** | Docker SDK + subprocess | 构建双层安全执行环境，支持 Python/C++/Java，资源限制 + 超时控制 |
| **智能测试生成** | LLM + 边界分析 | 自动生成覆盖正常/边界/对抗性的测试用例，提升代码健壮性 |
| **知识增强 RAG** | Chroma + LangChain | 向量检索相似算法题目，辅助 Agent 生成更优解 |
| **流式交互界面** | Streamlit + Callback | 实时展示 Agent 思考过程，提升用户体验 |

### 技术关键词
`LangGraph` `ReAct` `Multi-Agent` `Docker Sandbox` `RAG` `Streamlit` `Code Generation`

## 🧪 运行测试

```bash
# 运行全部测试
python test_agent.py

# 单独测试代码执行器
python -c "from tools.code_executor import execute_code; print(execute_code('print(1+1)', 'python'))"

# 单独测试 Agent（需要配置 API Key）
python -c "from agent.react_agent import solve_problem; print(solve_problem('计算1+1'))"
```

## 🛣️ 未来扩展

- [ ] **算法复杂度分析**：AST 静态分析自动推导时间/空间复杂度
- [ ] **知识图谱**：Neo4j 构建算法知识图谱，GraphRAG 增强检索
- [ ] **学习路径规划**：基于用户历史的个性化刷题推荐
- [ ] **代码可视化**：递归执行过程、变量状态追踪
- [ ] **多语言支持**：Go、Rust、JavaScript 等更多语言

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 PR！
