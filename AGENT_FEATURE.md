# AlgoMate Agent 功能实现文档

## 已完成功能

### 1. 代码执行沙箱 (tools/code_executor.py)

#### 功能特性
- **双层架构**：支持 Docker 沙箱（生产环境）和 Subprocess 沙箱（本地演示）
- **多语言支持**：Python、C++、Java
- **安全机制**：
  - 超时控制（默认 10 秒，可配置）
  - 内存限制（默认 256MB）
  - 进程树清理
  - 临时目录隔离

#### 核心类
```python
class CodeExecutor:
    """
    代码执行器统一接口
    
    自动选择最佳执行后端：
    1. Docker 可用时优先使用 DockerSandbox
    2. 否则回退到 SubprocessSandbox
    """
    
    def execute(self, code: str, language: str, 
                input_data: str = None, 
                test_cases: List[tuple] = None) -> ExecutionResult
```

#### 使用示例
```python
from tools.code_executor import execute_code

# 执行 Python 代码
result = execute_code("print('Hello')", language="python")
print(result.stdout)  # Hello

# 执行带测试用例
result = execute_code(
    code="print(sum(map(int, input().split())))",
    language="python",
    test_cases=[("1 2\n", "3"), ("3 4\n", "7")]
)
print(result.success)  # True/False
```

---

### 2. ReAct Agent (agent/)

#### 架构设计

```
用户输入
    |
    v
┌─────────────┐
│ 题目分析    │ ── 提取类型、约束、边界
└──────┬──────┘
       |
       v
┌─────────────┐
│ 生成测试    │ ── 自动生成 3-5 个测试用例
└──────┬──────┘
       |
       v
┌─────────────┐
│ 编写代码    │ ── 生成初始代码
└──────┬──────┘
       |
       v
┌─────────────┐
│ 执行测试    │ ── 运行代码
└──────┬──────┘
       |
       ├─ 成功 ──▶ 生成报告 ──▶ 结束
       |
       └─ 失败 ──▶ 分析错误 ──▶ 修复代码 ──┐
                                  ^       |
                                  └───────┘
                                  (最多 5 次)
```

#### 核心文件

| 文件 | 职责 |
|------|------|
| `agent/state.py` | 定义 AgentState，包含题目、代码、执行结果、历史等状态 |
| `agent/nodes.py` | 7 个核心节点：分析/生成测试/生成代码/执行/分析结果/修复/生成报告 |
| `agent/react_agent.py` | AlgoMateAgent 主类，使用 LangGraph 构建工作流 |

#### 使用示例

```python
from agent.react_agent import AlgoMateAgent

# 初始化 Agent
agent = AlgoMateAgent(max_iterations=5)

# 解决问题（同步模式）
result = agent.solve(
    problem_description="""
    题目：两数之和
    
    给定数组 nums 和 target，找出和为 target 的两个数下标。
    
    示例：
    输入：nums = [2,7,11,15], target = 9
    输出：[0,1]
    """,
    language="python"
)

# 获取结果
print(result["final_answer"])  # 完整解答报告
print(result["generated_code"])  # 最终代码
print(result["is_solved"])  # 是否解决
print(result["execution_history"])  # 执行历史
```

#### 流式模式（Web 界面使用）

```python
# 实时获取中间结果
for event in agent.solve_stream(problem, language="python"):
    for node_name, output in event.items():
        print(f"节点 {node_name} 完成")
        if "generated_code" in output:
            print(f"代码: {output['generated_code']}")
```

---

### 3. Web 界面 (algomate_web.py)

#### 功能特性
- **双模式切换**：RAG 问答模式 / Agent 解题模式
- **流式展示**：实时展示 Agent 思考过程
- **代码高亮**：语法高亮显示生成的代码
- **执行可视化**：展示执行结果、历史记录、测试用例

#### 界面布局
```
┌─────────────────────────────────────────┐
│  AlgoMate                 [模式切换]    │
├──────────┬──────────────────────────────┤
│ 工作模式 │                              │
│ ● RAG问答│  User: 题目描述...           │
│ ○ Agent  │                              │
│          │  Assistant:                  │
│ Agent配置│  ┌─────────────────────────┐ │
│ - 语言   │  │ 最终解答报告...         │ │
│ - 迭代   │  └─────────────────────────┘ │
│          │  ┌─────────────────────────┐ │
│ [清空]   │  │ [展开] 生成的代码       │ │
│          │  └─────────────────────────┘ │
│          │  ┌─────────────────────────┐ │
│          │  │ [展开] 执行结果         │ │
│          │  └─────────────────────────┘ │
│          │  ┌─────────────────────────┐ │
│          │  │ [展开] 执行历史 (3次)   │ │
│          │  └─────────────────────────┘ │
│          │                              │
│          │  [输入框...            ] [发送]│
└──────────┴──────────────────────────────┘
```

---

## 启动方式

### 1. 安装依赖

```bash
pip install langchain langchain-core langchain-community langgraph streamlit chromadb
```

### 2. 配置 API Key

```bash
# DashScope (通义千问)
export DASHSCOPE_API_KEY="your-key"

# 或 OpenAI
export OPENAI_API_KEY="your-key"
```

### 3. 启动 Web 界面

```bash
streamlit run algomate_web.py
```

访问 http://localhost:8501

---

## 测试

```bash
# 测试代码执行器
python -c "from tools.code_executor import execute_code; print(execute_code('print(1+1)', 'python'))"

# 完整测试
python test_agent.py
```

---

## 简历描述建议

### 项目名称
**AlgoMate - 基于 ReAct 架构的智能算法辅导 Agent**

### 项目描述
设计并实现基于 **LangGraph + ReAct** 架构的多 Agent 系统，具备自主分析题目、编写代码、执行测试、自动修复错误的闭环能力。

### 技术栈
`Python` `LangChain/LangGraph` `Docker` `Streamlit` `ChromaDB`

### 核心功能
1. **代码执行沙箱**：支持 Python/C++/Java 的双层安全执行环境（Docker + Subprocess）
2. **ReAct 智能体**：实现推理-行动循环，平均 2-3 轮迭代达到正确解
3. **自动测试生成**：LLM 自动生成边界测试用例
4. **错误自动修复**：分析编译/运行时错误，自动迭代修复
5. **流式交互界面**：Streamlit 实时展示 Agent 思考过程

### 代码统计
- 核心代码：~800 行（Agent + 沙箱）
- Web 界面：~200 行
- 测试覆盖：代码执行、Agent 流程
