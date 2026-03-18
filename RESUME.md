# AlgoMate - 简历项目描述

## 项目概述

**AlgoMate - 从 RAG 到 ReAct：智能算法辅导系统的技术演进**

本项目是一个渐进式学习 AI Agent 技术的完整实践：从基础的 RAG（检索增强生成）知识问答系统，逐步演进为具备自主推理和行动能力的 ReAct Agent 系统。通过这个项目，系统性地掌握了从简单信息检索到复杂任务规划的技术栈。

---

## 技术演进路线

```
阶段一：RAG 知识检索（基础）
    │
    ├── 向量数据库：Chroma + 文本嵌入
    ├── 检索增强：相似度搜索 + Prompt 增强
    └── 对话历史：文件持久化存储
    │
    ▼
阶段二：代码执行工具（能力扩展）
    │
    ├── 代码沙箱：Docker/Subprocess 双层架构
    ├── 多语言支持：Python/C++/Java
    └── 安全机制：超时/内存/进程隔离
    │
    ▼
阶段三：ReAct Agent（自主决策）
    │
    ├── 架构设计：LangGraph 状态机编排
    ├── 推理循环：分析→生成→执行→修复
    └── 自纠错机制：测试用例自验证
```

---

## 技术栈

`LangChain` `LangGraph` `ReAct` `RAG` `ChromaDB` `Docker` `Streamlit` `Multi-Agent System`

---

## 阶段一：RAG 知识问答系统（基础阶段）

### 核心功能
基于向量数据库的算法知识检索问答系统，支持上传算法文档，通过语义检索回答概念性问题。

### 技术实现
- **向量存储**：ChromaDB + DashScope 文本嵌入模型，实现文档向量化存储
- **文本分割**：RecursiveCharacterTextSplitter 处理长文档，避免上下文溢出
- **检索增强**：相似度 Top-K 检索，将检索结果注入 System Prompt 增强生成质量
- **对话记忆**：FileChatMessageHistory 实现多轮对话历史持久化

### 关键代码
```python
# RAG 链构建
retriever = vector_store.as_retriever(search_kwargs={"k": 2})
chain = (
    {"context": retriever | format_docs, "input": RunnablePassthrough()}
    | prompt_template
    | chat_model
    | StrOutputParser()
)
```

---

## 阶段二：代码执行沙箱（能力扩展）

### 核心功能
为系统增加代码执行能力，使 Agent 不仅能"说"还能"做"，支持验证生成代码的正确性。

### 技术实现
- **双层沙箱架构**：
  - Docker 沙箱：生产环境，完整容器隔离，资源限制严格
  - Subprocess 沙箱：开发环境，超时控制 + 信号处理 + 临时目录
- **多语言支持**：Python/C++/Java，自动语言检测
- **安全机制**：
  - 超时控制：`subprocess.communicate(timeout=10)` 防止死循环
  - 进程清理：`os.killpg()` 终止整个进程树
  - 资源隔离：内存限制、无网络访问、只读文件系统

### 关键代码
```python
class CodeExecutor:
    """统一接口，自动选择 Docker/Subprocess 后端"""
    def execute(self, code, language, test_cases) -> ExecutionResult:
        # 自动检测语言、执行代码、返回结果
```

---

## 阶段三：ReAct Agent（自主决策系统）

### 核心功能
构建具备自主推理和行动能力的 Agent，实现完整的算法题求解闭环：分析题目 → 生成测试 → 编写代码 → 执行验证 → 自动修复。

### 技术实现
- **LangGraph 状态机**：7 个节点、条件边、循环跳转，可视化工作流
- **ReAct 循环**：推理(Reasoning) → 行动(Action) → 观察(Observation) → 反思(Reflection)
- **自纠错机制**：
  - 测试用例自验证：失败时先验证测试用例正确性，避免修复正确代码
  - 错误模式检测：连续同类错误触发可信度评估
  - 优雅降级：达到迭代上限或测试用例可疑时，标记部分成功并结束

### 关键代码
```python
# ReAct 工作流定义
workflow.add_node("analyze", analyze_problem)
workflow.add_node("generate_code", generate_code)
workflow.add_node("execute", execute_code)
workflow.add_node("fix", fix_code)

# 条件边：根据执行结果动态路由
workflow.add_conditional_edges(
    "analyze_result",
    should_continue,
    {"fix": "fix_code", "reexecute": "execute_code", "finish": END}
)
```

---

## 项目难点与解决方案

### 难点一：从 RAG 到 Agent 的架构演进

**问题描述**：
RAG 是单向流程（检索→生成），而 Agent 需要多轮循环（生成→执行→观察→修复）。如何复用 RAG 的基础设施（LLM、向量库）同时支持 Agent 的复杂状态管理？

**解决方案**：
1. **分层架构**：将 RAG 封装为知识检索工具，供 Agent 节点调用
2. **状态隔离**：RAG 使用简单对话历史，Agent 使用 TypedDict 管理复杂状态
3. **模式切换**：Web 界面支持 RAG/Agent 双模式，独立 Session 避免状态冲突

**技术收获**：
理解了 RAG 是"知识外挂"，Agent 是"决策大脑"，两者可以互补：RAG 为 Agent 提供领域知识，Agent 为 RAG 增加行动能力。

---

### 难点二：测试用例期望值错误导致的无效修复

**问题描述**：
LLM 生成的测试用例可能出现期望值计算错误，导致 Agent 不断"修复"实际上正确的代码，浪费迭代次数。

**解决方案**：
1. **测试用例自验证机制**：测试失败时，调用 LLM 验证测试用例正确性
2. **双向判断**：LLM 同时评估代码逻辑和期望值合理性
3. **自动修正**：检测到测试用例错误时，修正期望值并重新执行，不消耗修复次数

**关键逻辑**：
```python
# 测试失败时先验证测试用例
validation = llm.validate_test_cases(code, result, test_cases)
if not validation["test_cases_valid"]:
    test_cases = fix_test_cases(test_cases, validation["issues"])
    return {"next_step": "execute_code"}  # 重新执行，不消耗迭代
else:
    return {"next_step": "fix_code"}  # 修复代码
```

---

### 难点三：代码执行的安全性与隔离性

**问题描述**：
Agent 需要执行生成的代码，如何防止恶意代码（无限循环、资源耗尽）？如何在无 Docker 环境下保证安全？

**解决方案**：
1. **分层沙箱**：Docker（生产）+ Subprocess（开发）两种后端
2. **Subprocess 安全措施**：
   - 超时控制 + 信号处理清理进程树
   - 临时目录执行，自动清理
3. **资源限制**：内存限制、CPU 时间片控制

---

### 难点四：ReAct 循环中的状态管理

**问题描述**：
Agent 需要维护复杂上下文（题目、代码、执行历史、测试用例），多轮迭代中如何确保状态一致性？

**解决方案**：
1. **集中式状态**：TypedDict 定义 `AgentState`，包含所有字段
2. **不可变更新**：每个节点返回状态片段，LangGraph 自动合并
3. **检查点机制**：MemorySaver 支持中断恢复

---

## 学习收获与技术反思

### 阶段收获

| 阶段 | 核心技术 | 关键收获 |
|------|----------|----------|
| RAG | 向量检索、Prompt 工程 | 理解嵌入模型和相似度检索原理，掌握检索增强生成范式 |
| 工具 | 代码沙箱、安全隔离 | 理解 LLM 从"说"到"做"需要可靠的工具层支撑 |
| Agent | ReAct、LangGraph | 掌握推理-行动循环，理解状态机在复杂任务中的应用 |

### 技术反思

1. **递进式学习路径**：
   - RAG → Tool → Agent 是自然的演进路线
   - 先掌握简单的链式调用，再理解复杂的状态管理
   - 每个阶段都建立在前一阶段的基础上

2. **Agent 设计原则**：
   - 工具层必须可靠，否则 Agent 无法获得准确观察
   - 自纠错机制很重要，LLM 会犯错，需要验证和兜底
   - 迭代控制必不可少，防止无限循环

3. **可改进方向**：
   - 引入代码复杂度分析节点（AST 静态分析）
   - 使用更轻量的模型进行测试验证，降低成本
   - 构建知识图谱，GraphRAG 增强检索

---

## 一句话总结

从 RAG 知识检索到 ReAct 自主决策，渐进式构建了具备自纠错能力的智能算法辅导 Agent，掌握了 LangChain 生态从简单链到复杂状态机的完整技术栈。

---

## 面试高频问题准备

### 技术演进相关

**Q: 为什么选择从 RAG 开始，而不是直接做 Agent？**
> RAG 是 LLM 应用的基础模式，帮助我理解向量检索、Prompt 工程、链式调用等核心概念。直接做 Agent 会同时面临状态管理、工具调用、循环控制等多个复杂问题，学习曲线过陡。从 RAG 开始，每增加一个能力（代码执行、循环修复）都有明确的技术目标，递进式掌握。

**Q: RAG 和 Agent 的关系是什么？**
> RAG 是 Agent 的一个工具。在这个项目中，RAG 为 Agent 提供算法知识检索能力，Agent 的「知识检索节点」可以调用 RAG 查询相似题目。RAG 负责"知道"，Agent 负责"做到"。

**Q: LangChain 的 Chain 和 LangGraph 的 Graph 有什么区别？**
> Chain 是线性流程，适合 RAG 这种单向任务；Graph 支持分支、循环、条件跳转，适合 ReAct 这种需要反复试错的多轮任务。LangGraph 还提供了状态管理和检查点机制，适合复杂 Agent。

### 技术细节相关

**Q: 测试用例自验证是如何实现的？**
> 测试失败时，不直接修复代码，而是先调用 LLM 验证测试用例。Prompt 包含代码、执行结果、测试用例，让 LLM 判断期望值是否正确。输出 JSON 包含 `test_cases_valid` 和 `suggested_fix`，如果是测试用例错误，自动修正后重新执行。

**Q: 如何防止 Agent 无限循环？**
> 三层防护：1) `max_iterations` 硬上限 2) 连续同类错误触发测试用例可信度评估 3) 达到上限后强制结束并标记部分成功。
