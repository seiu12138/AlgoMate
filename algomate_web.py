#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/16
# @File     : algomate_web.py
# @Project  : AlgoMate
import streamlit as st

from utils.config_handler import session_conf
from utils.style_loader import load_theme
from rag.rag import RagService
from agent.react_agent import AlgoMateAgent


# 页面配置
st.set_page_config(
    page_title="AlgoMate - 智能算法助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载主题样式
load_theme("algomate_theme")


### streamlit环境初始化
def init_session():
    """初始化 session state"""
    if "message" not in st.session_state:
        st.session_state["message"] = []
    
    if "rag" not in st.session_state:
        st.session_state["rag"] = RagService()
    
    if "agent" not in st.session_state:
        st.session_state["agent"] = None
    
    if "mode" not in st.session_state:
        st.session_state["mode"] = "RAG 问答模式"
    
    if "agent_results" not in st.session_state:
        st.session_state["agent_results"] = {}

init_session()

### streamlit侧边栏实现
with st.sidebar:
    # 标题区域
    st.title("🤖 AlgoMate")
    st.markdown("<span style='color: #4b5563;'>智能算法学习与解题助手</span>", unsafe_allow_html=True)
    
    st.divider()
    
    # ========== 工作模式选择 ==========
    st.markdown("<p class='sidebar-section-title'>📋 工作模式</p>", unsafe_allow_html=True)
    
    mode = st.radio(
        "选择模式",
        ["RAG 问答模式", "Agent 解题模式"],
        label_visibility="collapsed",
        help="RAG 问答模式：基于知识库回答算法相关问题\nAgent 解题模式：AI 自动分析、编写、测试、修复代码"
    )
    st.session_state["mode"] = mode
    
    # Agent 配置
    if mode == "Agent 解题模式":
        st.divider()
        st.markdown("<p class='sidebar-subtitle'>⚙️ Agent 配置</p>", unsafe_allow_html=True)
        language = st.selectbox(
            "编程语言",
            ["python", "cpp", "java"],
            help="选择代码生成和执行的编程语言"
        )
        max_iter = st.slider(
            "最大修复次数",
            1, 10, 5,
            help="代码失败时的最大自动修复尝试次数"
        )
    else:
        language = "python"
        max_iter = 5
    
    # ========== 操作按钮 ==========
    st.divider()
    st.markdown("<p class='sidebar-section-title'>🛠️ 操作</p>", unsafe_allow_html=True)
    
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state["message"] = []
        st.session_state["agent_results"] = {}
        st.rerun()

    # 底部信息
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("<span style='color: #6b7280;'>Powered by LangChain + LangGraph</span>", unsafe_allow_html=True)

### 主界面
st.title("AlgoMate" if st.session_state["mode"] == "RAG 问答模式" else "AlgoMate Agent")
st.caption("📝 知识问答" if st.session_state["mode"] == "RAG 问答模式" else "🤖 自动解题")
st.divider()

# 显示历史消息
for message in st.session_state["message"]:
    with st.chat_message(message["role"]):
        if "content" in message:
            st.markdown(message["content"])
        
        # 显示 Agent 详细结果
        if "agent_result" in message and message["role"] == "assistant":
            result = message["agent_result"]
            
            # 代码展示
            if result.get("generated_code"):
                with st.expander("📝 生成的代码", expanded=False):
                    st.code(result["generated_code"], language=language)
            
            # 执行结果
            if result.get("execution_result"):
                exec_result = result["execution_result"]
                with st.expander("▶️ 执行结果", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        success = exec_result.get("success", False)
                        st.metric("执行状态", "✅ 成功" if success else "❌ 失败")
                    with col2:
                        st.metric("执行时间", f"{exec_result.get('execution_time', 0):.2f}ms")
                    with col3:
                        st.metric("退出码", exec_result.get("exit_code", -1))
                    
                    if exec_result.get("stdout"):
                        st.text("标准输出:")
                        st.code(exec_result["stdout"])
                    
                    if exec_result.get("stderr"):
                        st.text("错误输出:")
                        st.error(exec_result["stderr"])
            
            # 执行历史
            if result.get("execution_history"):
                history = result["execution_history"]
                with st.expander(f"📊 执行历史 ({len(history)} 次尝试)", expanded=False):
                    for h in history:
                        iter_num = h.get("iteration", 0)
                        error_type = h.get("result", {}).get("error_type", "成功")
                        
                        if error_type is None:
                            st.success(f"尝试 {iter_num}: ✅ 成功")
                        else:
                            st.error(f"尝试 {iter_num}: ❌ {error_type}")
                        
                        if h.get("fixes"):
                            st.caption(f"修复: {h['fixes']}")


# 输入栏Placeholder
prompt = st.chat_input("输入你的问题..." if st.session_state["mode"] == "RAG 问答模式" else "描述你的算法题目...")

if prompt:
    # 用户消息
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})
    
    # Assistant 回复
    with st.chat_message("assistant"):
        if st.session_state["mode"] == "RAG 问答模式":
            # ============ RAG 模式 ============
            with st.spinner("💭 思考中..."):
                rag = st.session_state["rag"]
                
                # 流式输出
                res_stream = rag.chain.stream(
                    {"input": prompt}, 
                    session_conf.get("session_config", {})
                )
                
                res_container = st.empty()
                res_list = []
                
                for chunk in res_stream:
                    res_list.append(chunk)
                    res_container.markdown("".join(res_list))
                
                final_response = "".join(res_list)
                st.session_state["message"].append({
                    "role": "assistant", 
                    "content": final_response
                })
        
        else:
            # ============ Agent 模式 ============
            # 初始化 Agent
            if st.session_state["agent"] is None:
                with st.spinner("🚀 初始化 Agent..."):
                    st.session_state["agent"] = AlgoMateAgent(max_iterations=max_iter)
            
            agent = st.session_state["agent"]
            
            # 创建进度展示区域
            progress_container = st.container()
            status_area = st.empty()
            result_area = st.empty()
            
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            # 收集完整结果
            final_result = {}
            messages = []
            
            try:
                # 流式执行
                step_count = 0
                total_steps = 7  # 预估步骤数
                
                for event in agent.solve_stream(prompt, language=language):
                    for node_name, output in event.items():
                        if node_name == "__end__":
                            continue
                        
                        # 更新进度
                        step_count += 1
                        progress = min(step_count / total_steps, 0.95)
                        progress_bar.progress(progress)
                        
                        # 更新状态
                        status_map = {
                            "analyze": "🔍 分析题目...",
                            "generate_test_cases": "📝 生成测试用例...",
                            "validate_test_cases": "✅ 验证测试用例...",
                            "generate_code": "💻 编写代码...",
                            "execute_code": "▶️ 执行代码...",
                            "analyze_result": "📊 分析结果...",
                            "fix_code": "🔧 修复代码...",
                            "finish": "✨ 生成最终答案..."
                        }
                        status_text.info(status_map.get(node_name, f"执行: {node_name}"))
                        
                        # 收集消息
                        if "messages" in output:
                            messages.extend(output["messages"])
                        
                        # 收集结果
                        final_result.update(output)
                
                # 完成
                progress_bar.progress(1.0)
                status_text.success("✅ 完成！")
                
                # 展示最终答案
                final_answer = final_result.get("final_answer", "未能生成答案")
                result_area.markdown(final_answer)
                
                # 保存到消息历史
                st.session_state["message"].append({
                    "role": "assistant",
                    "content": final_answer,
                    "agent_result": {
                        "generated_code": final_result.get("generated_code"),
                        "execution_result": final_result.get("execution_result"),
                        "execution_history": final_result.get("execution_history"),
                        "is_solved": final_result.get("is_solved", False)
                    }
                })
                
                # 保存到结果字典（用于详细展示）
                st.session_state["agent_results"][len(st.session_state["message"]) - 1] = final_result
                
                # 重新运行以展示详细信息
                st.rerun()
                
            except Exception as e:
                status_text.error(f"❌ 执行出错: {str(e)}")
                st.error("详细错误信息:")
                import traceback
                st.code(traceback.format_exc())

### 底部栏
st.divider()
if st.session_state["mode"] == "RAG 问答模式":
    st.caption("💡 提示：在知识库上传算法相关文档，我可以基于这些知识回答问题")
else:
    st.caption("💡 提示：Agent 模式会自动分析问题、编写代码、执行测试并在出错时自动修复")
