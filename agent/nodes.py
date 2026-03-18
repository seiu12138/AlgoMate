#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/16
# @File     : nodes.py
# @Project  : AlgoMate
import json
from typing import Dict, Any
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .state import AgentState, ExecutionHistory
from tools.code_executor import CodeExecutor
from utils.prompts_loader import (
    load_analysis_prompt,
    load_test_case_generation_prompt,
    load_test_case_self_validation_prompt,
    load_code_generation_prompt,
    load_test_case_validation_prompt,
    load_code_fix_prompt,
    load_final_answer_prompt,
)
from utils.logger_handler import log_node, log_test, log_code
import logging


# LangGraph节点实现
class AgentNodes:
    """Agent 节点集合"""

    def __init__(self, llm):
        self.llm = llm
        self.code_executor = CodeExecutor(timeout=5)
    
    def analyze_problem(self, state: AgentState) -> Dict[str, Any]:
        """
        分析题目节点

        Args:
            state: 当前Agent状态

        Returns:
            包含problem_analysis、messages和next_step的字典
        """
        log_node("analyze_problem", "开始分析题目")
        
        prompt = ChatPromptTemplate.from_template(load_analysis_prompt())
        chain = prompt | self.llm
        
        response = chain.invoke({
            "problem_description": state["problem_description"]
        })
        
        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            analysis = json.loads(content.strip())
            analysis_str = json.dumps(analysis, ensure_ascii=False, indent=2)
        except:
            analysis_str = response.content
        
        log_node("analyze_problem", "题目分析完成")
        
        return {
            "problem_analysis": analysis_str,
            "messages": [AIMessage(content=f"题目分析:\n{analysis_str}")],
            "next_step": "generate_test_cases"
        }
    
    def generate_test_cases(self, state: AgentState) -> Dict[str, Any]:
        """
        生成测试用例节点

        Args:
            state: 当前Agent状态

        Returns:
            包含test_cases、messages和next_step的字典
        """
        log_node("generate_test_cases", "开始生成测试用例")
        
        prompt = ChatPromptTemplate.from_template(load_test_case_generation_prompt())
        chain = prompt | self.llm
        
        response = chain.invoke({
            "problem_analysis": state["problem_analysis"]
        })
        
        # 解析测试用例
        test_cases = []
        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            data = json.loads(content.strip())
            for tc in data.get("test_cases", []):
                test_cases.append({
                    "input": tc["input"],
                    "expected": tc["expected"],
                    "actual": None,
                    "passed": None,
                    "category": tc.get("category", "general"),
                    "description": tc.get("description", "")
                })
        except Exception as e:
            log_node("generate_test_cases", f"测试用例解析失败: {e}", level=logging.WARNING)
            # 使用默认测试用例
            test_cases = [{"input": "", "expected": "", "actual": None, "passed": None, "category": "general", "description": ""}]
        
        log_test(f"生成 {len(test_cases)} 个测试用例")
        
        return {
            "test_cases": test_cases,
            "messages": [AIMessage(content=f"生成测试用例: {len(test_cases)} 个")],
            "next_step": "validate_test_cases"
        }
    
    def validate_test_cases(self, state: AgentState) -> Dict[str, Any]:
        """
        验证测试用例节点（生成后立即验证）

        Args:
            state: 当前Agent状态

        Returns:
            包含validated_test_cases、messages和next_step的字典
        """
        log_node("validate_test_cases", "开始验证测试用例正确性")
        
        test_cases = state.get("test_cases", [])
        test_cases_str = json.dumps(test_cases, ensure_ascii=False, indent=2)
        
        prompt = ChatPromptTemplate.from_template(load_test_case_self_validation_prompt())
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "problem_analysis": state["problem_analysis"],
                "test_cases": test_cases_str
            })
            
            # 解析验证结果
            content = response.content
            log_test(f"测试用例自验证结果: {content[:200]}...")
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            validation = json.loads(content.strip())
            validated_cases = validation.get("validated_test_cases", [])
            corrections = validation.get("corrections_made", [])
            
            # 转换回标准格式
            final_test_cases = []
            for tc in validated_cases:
                final_test_cases.append({
                    "input": tc["input"],
                    "expected": tc["expected"],
                    "actual": None,
                    "passed": None,
                    "category": tc.get("category", "general"),
                    "description": tc.get("description", "")
                })
            
            if corrections:
                log_test(f"修正了 {len(corrections)} 个测试用例的期望值", level=logging.WARNING)
                for corr in corrections:
                    log_test(f"  用例 {corr['index']}: {corr['reason']}")
            else:
                log_test("所有测试用例验证通过，无需修正")
            
            validation_summary = validation.get("validation_summary", "验证完成")
            
            return {
                "test_cases": final_test_cases,
                "messages": [AIMessage(content=f"测试用例验证: {validation_summary}")],
                "next_step": "generate_code"
            }
            
        except Exception as e:
            log_node("validate_test_cases", f"测试用例验证失败: {e}", level=logging.WARNING)
            # 验证失败也继续，使用原始测试用例
            return {
                "test_cases": test_cases,
                "messages": [AIMessage(content="测试用例验证跳过，使用原始测试用例")],
                "next_step": "generate_code"
            }
    
    def generate_code(self, state: AgentState) -> Dict[str, Any]:
        """
        生成代码节点

        Args:
            state: 当前Agent状态

        Returns:
            包含generated_code、messages和next_step的字典
        """
        log_node("generate_code", "开始生成代码")
        
        prompt = ChatPromptTemplate.from_template(load_code_generation_prompt())
        chain = prompt | self.llm
        
        # 格式化测试用例
        test_cases_str = json.dumps(state.get("test_cases", []), ensure_ascii=False, indent=2)
        
        response = chain.invoke({
            "language": state.get("language", "python"),
            "problem_analysis": state["problem_analysis"],
            "test_cases": test_cases_str
        })
        
        # 提取代码
        code = response.content
        if "```" in code:
            # 提取代码块
            lines = code.split("\n")
            in_code = False
            code_lines = []
            for line in lines:
                if line.strip().startswith("```"):
                    if in_code:
                        break
                    in_code = True
                    continue
                if in_code:
                    code_lines.append(line)
            code = "\n".join(code_lines)
        
        log_code(f"代码生成完成，共 {len(code)} 字符")
        
        return {
            "generated_code": code,
            "messages": [AIMessage(content=f"生成代码:\n```python\n{code}\n```")],
            "next_step": "execute_code"
        }
    
    def execute_code(self, state: AgentState) -> Dict[str, Any]:
        """
        执行代码节点

        Args:
            state: 当前Agent状态

        Returns:
            包含execution_result、messages和next_step的字典
        """
        log_node("execute_code", "开始执行代码")
        
        code = state.get("generated_code", "")
        language = state.get("language", "python")
        test_cases = state.get("test_cases", [])
        
        # 准备测试用例
        exec_test_cases = []
        for tc in test_cases:
            exec_test_cases.append((tc["input"], tc["expected"]))
        
        # 执行代码
        result = self.code_executor.execute(
            code=code,
            language=language,
            test_cases=exec_test_cases if exec_test_cases else None
        )

        result_dict = result.to_dict()
        
        # 更新测试用例结果
        if test_cases and result.success:
            output_lines = result.stdout.strip().split("\n")
            for i, line in enumerate(output_lines):
                if i < len(test_cases) and ":" in line:
                    passed = "[成功]" in line or "成功" in line or "passed" in line.lower()
                    test_cases[i]["passed"] = passed
        
        log_node("execute_code", f"代码执行完成，成功: {result.success}, 错误: {result.error_type or '无'}")
        
        return {
            "execution_result": result_dict,
            "messages": [AIMessage(content=f"执行结果:\n{result}")],
            "next_step": "analyze_result"
        }
    
    def analyze_result(self, state: AgentState) -> Dict[str, Any]:
        """
        分析结果节点

        Args:
            state: 当前Agent状态

        Returns:
            包含is_solved、execution_history、iteration_count、messages和next_step的字典
        """
        log_node("analyze_result", "开始分析执行结果")
        
        result = state.get("execution_result", {})
        iteration = state.get("iteration_count", 0)
        max_iter = state.get("max_iterations", 5)
        history = state.get("execution_history", [])
        
        success = result.get("success", False)
        error_type = result.get("error_type")
        
        # 创建历史记录
        history_entry = ExecutionHistory(
            iteration=iteration + 1,
            code=state.get("generated_code", ""),
            language=state.get("language", "python"),
            result=result,
            analysis="",
            fixes=None,
            potential_test_case_error=False
        )
        
        # 判断是否解决
        if success:
            log_node("analyze_result", "代码执行成功，所有测试用例通过")
            return {
                "is_solved": True,
                "execution_history": [history_entry],
                "iteration_count": iteration + 1,
                "messages": [AIMessage(content="代码执行成功！所有测试用例通过。")],
                "next_step": "finish"
            }
        
        # 如果还有迭代次数，尝试验证测试用例
        if iteration < max_iter:
            # 使用 LLM 验证测试用例是否正确
            log_test("开始验证测试用例正确性")
            
            test_cases_str = json.dumps(
                state.get("test_cases", []),
                ensure_ascii=False,
                indent=2
            )
            
            prompt = ChatPromptTemplate.from_template(load_test_case_validation_prompt())
            chain = prompt | self.llm
            
            try:
                response = chain.invoke({
                    "code": state.get("generated_code", ""),
                    "success": result.get("success", False),
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", ""),
                    "test_cases": test_cases_str,
                    "problem_analysis": state.get("problem_analysis", "")
                })

                # 解析验证结果
                content = response.content
                log_test(f"测试用例验证结果内容: {content}")
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                validation = json.loads(content.strip())
                test_cases_valid = validation.get("test_cases_valid", True)
                issues = validation.get("issues", [])
                assessment = validation.get("overall_assessment", "")
                
                log_test(f"测试用例验证结果: {assessment}")
                
                # 如果测试用例有误，修正它们
                if not test_cases_valid and issues:
                    log_test("检测到测试用例错误，准备修正", level=logging.WARNING)
                    
                    # 修正测试用例
                    test_cases = state.get("test_cases", [])
                    for issue in issues:
                        idx = issue.get("test_index", 0)
                        if 0 <= idx < len(test_cases):
                            old_expected = test_cases[idx].get("expected", "")
                            suggested_fix = issue.get("suggested_fix", old_expected)
                            test_cases[idx]["expected"] = suggested_fix
                            log_test(f"修正用例 {idx}: '{old_expected}' -> '{suggested_fix}'")
                    
                    # 更新历史记录
                    history_entry["potential_test_case_error"] = True
                    
                    return {
                        "test_cases": test_cases,
                        "execution_history": [history_entry],
                        "iteration_count": iteration + 1,
                        "messages": [AIMessage(content=f"检测到测试用例错误，已修正 {len(issues)} 个用例，重新执行...")],
                        "next_step": "execute_code"  # 重新执行测试
                    }
                
                # 测试用例正确，代码需要修复
                log_test("测试用例验证通过，代码需要修复")
                
            except Exception as e:
                log_test(f"测试用例验证失败: {e}，继续正常修复流程", level=logging.WARNING)
        
        # 判断是否还有迭代次数
        if iteration >= max_iter:
            log_node("analyze_result", f"达到最大迭代次数 ({max_iter})，停止尝试", level=logging.WARNING)
            return {
                "execution_history": [history_entry],
                "iteration_count": iteration + 1,
                "messages": [AIMessage(content=f"达到最大迭代次数 ({max_iter})，未能解决问题。")],
                "next_step": "finish"
            }
        
        # 需要修复代码
        log_node("analyze_result", f"执行失败，准备修复代码 (迭代 {iteration + 1}/{max_iter})")
        
        return {
            "execution_history": [history_entry],
            "iteration_count": iteration + 1,
            "messages": [AIMessage(content=f"执行失败: {error_type or '未知错误'}，准备修复代码...")],
            "next_step": "fix_code"
        }
    
    def fix_code(self, state: AgentState) -> Dict[str, Any]:
        """
        修复代码节点

        Args:
            state: 当前Agent状态

        Returns:
            包含generated_code、messages和next_step的字典
        """
        log_node("fix_code", "开始修复代码")
        
        result = state.get("execution_result", {})
        history = state.get("execution_history", [])
        
        # 格式化历史记录
        history_str = "\n".join([
            f"尝试 {h['iteration']}: {h['result'].get('error_type', '成功') if h['result'] else '未知'}"
            for h in history[:-1]  # 排除当前这次
        ]) if len(history) > 1 else "无"
        
        # 格式化测试用例用于诊断
        test_cases_str = json.dumps(
            state.get("test_cases", []), 
            ensure_ascii=False, 
            indent=2
        )
        
        prompt = ChatPromptTemplate.from_template(load_code_fix_prompt())
        chain = prompt | self.llm
        
        response = chain.invoke({
            "code": state.get("generated_code", ""),
            "success": result.get("success", False),
            "exit_code": result.get("exit_code", -1),
            "error_type": result.get("error_type", "未知"),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "test_cases": test_cases_str,
            "history": history_str
        })
        
        # 提取修复后的代码
        fixed_code = response.content
        if "```" in fixed_code:
            lines = fixed_code.split("\n")
            in_code = False
            code_lines = []
            for line in lines:
                if line.strip().startswith("```"):
                    if in_code:
                        break
                    in_code = True
                    continue
                if in_code:
                    code_lines.append(line)
            fixed_code = "\n".join(code_lines)
        
        log_code(f"代码修复完成，共 {len(fixed_code)} 字符")
        
        # 更新历史记录中的修复说明
        if history:
            log_node("fix_code", f"执行结果: {result}")
            error_type = result.get("error_type") or "错误"
            history[-1]["fixes"] = "修复 " + error_type
        
        return {
            "generated_code": fixed_code,
            "messages": [AIMessage(content=f"修复后的代码:\n```python\n{fixed_code}\n```")],
            "next_step": "execute_code"  # 循环回执行
        }
    
    def create_final_answer(self, state: AgentState) -> Dict[str, Any]:
        """
        生成最终答案节点

        Args:
            state: 当前Agent状态

        Returns:
            包含final_answer和messages的字典
        """
        log_node("create_final_answer", "开始生成最终答案")
        
        is_solved = state.get("is_solved", False)
        
        if is_solved:
            # 生成完整报告
            prompt = ChatPromptTemplate.from_template(load_final_answer_prompt())
            chain = prompt | self.llm
            
            history_str = json.dumps(
                state.get("execution_history", []),
                ensure_ascii=False,
                indent=2
            )
            
            response = chain.invoke({
                "problem_description": state["problem_description"],
                "code": state.get("generated_code", ""),
                "execution_history": history_str,
                "final_result": json.dumps(state.get("execution_result", {}), ensure_ascii=False)
            })
            
            final_answer = response.content
        else:
            # 生成失败报告
            final_answer = f"""## 解答报告

很遗憾，经过多次尝试未能成功解决问题。

### 尝试历史
{len(state.get("execution_history", []))} 次尝试均失败。

### 最后错误
```
{state.get("execution_result", {}).get("stderr", "未知错误")}
```

### 最后代码
```python
{state.get("generated_code", "")}
```

**建议**：
1. 检查题目描述是否完整
2. 尝试更换编程语言
3. 手动检查代码逻辑
"""
        
        log_node("create_final_answer", "最终答案生成完成")
        
        return {
            "final_answer": final_answer,
            "messages": [AIMessage(content=final_answer)]
        }
