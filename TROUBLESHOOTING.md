# AlgoMate 故障排除指南

## 问题：前端显示"抱歉，发生了错误"

### 原因分析
当前 Python 3.8 环境与 `langgraph>=0.1.0` 不兼容（需要 Python 3.9+）。

### 解决方案

#### 方案 1：使用 Mock 后端（推荐，立即可用）

Mock 后端模拟了真实后端的 API 响应，无需 AI 模型即可测试前端功能。

```powershell
# 1. 停止当前的 start.py（如果有）

# 2. 启动 Mock 后端
cd backend
python mock_main.py

# 3. 在另一个终端启动前端
cd frontend
npm run preview
```

访问 http://localhost:4173 即可使用。

#### 方案 2：修复真实后端（需要降级依赖）

```powershell
# 1. 停止当前后端

# 2. 安装 Python 3.8 兼容的依赖
cd backend
pip install -r requirements-py38.txt

# 3. 启动真实后端
python start.py
```

**注意**：降级后的 langgraph 版本可能部分功能受限。

#### 方案 3：升级 Python 到 3.9+（推荐长期使用）

```powershell
# 安装 Python 3.9 或更高版本
# 然后安装完整依赖
pip install -r requirements.txt
```

---

## 常见问题

### Q: 如何查看后端错误日志？

**A**: 查看启动后端的终端窗口，错误信息会显示在那里。常见错误：

```
ModuleNotFoundError: No module named 'langgraph'
# → 依赖未安装，运行 pip install -r requirements.txt

ImportError: cannot import name '...' from '...'
# → 版本不兼容，使用 requirements-py38.txt
```

### Q: 前端提示 "Failed to fetch"？

**A**: 检查：
1. 后端是否已启动（访问 http://localhost:8000/api/health）
2. 后端 CORS 是否允许前端地址
3. 前后端端口是否正确（后端 8000，前端 5173/4173）

### Q: Mock 后端和真实后端有什么区别？

| 功能 | Mock 后端 | 真实后端 |
|------|-----------|----------|
| RAG 问答 | 返回固定文本 | 调用 AI 模型 |
| Agent 解题 | 模拟执行流程 | 真实代码生成执行 |
| 依赖要求 | 仅需 FastAPI | 需要 LangChain/LangGraph |
| 适用场景 | 前端开发测试 | 生产环境 |

---

## 快速启动检查清单

- [ ] Python 3.8+ 已安装
- [ ] 后端依赖已安装（requirements.txt 或 requirements-py38.txt）
- [ ] DASHSCOPE_API_KEY 已设置（真实后端需要）
- [ ] 后端服务已启动（http://localhost:8000）
- [ ] 前端已构建（npm run build）
- [ ] 前端服务已启动（npm run preview）
- [ ] 浏览器可以访问 http://localhost:4173
