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



# 整体系统提示词
ANALYSIS_PROMPT = """你是一位专业的算法竞赛教练。请仔细分析用户提供的编程题目，提取以下信息：

1. **题目类型**：数据结构 / 算法 / 数学 / 字符串 / 图论 / 动态规划 等
2. **输入描述**：输入格式、数据范围、约束条件
3. **输出描述**：输出格式、精度要求
4. **关键约束**：时间限制、空间限制、边界情况
5. **解题思路**：简要描述解题的核心思想
6. **边界情况**：需要特别注意的测试点

请用以下 JSON 格式返回分析结果：
```json
{{
    "problem_type": "题目类型",
    "input_description": "输入描述",
    "output_description": "输出描述",
    "constraints": "关键约束",
    "solution_approach": "解题思路",
    "edge_cases": ["边界情况1", "边界情况2"],
    "suggested_language": "建议的编程语言"
}}
```

题目描述：
{problem_description}
"""


TEST_CASE_GENERATION_PROMPT = """基于以下题目分析，生成 3-5 个测试用例。

要求：
1. **正常情况**：符合题目描述的常规输入
2. **边界情况**：最大值、最小值、空输入等极端情况  
3. **特殊情况**：可能让程序出错的情况

**重要提示**：
- 计算期望值时请仔细验证，确保输出格式完全正确
- 注意数值计算的精度问题（如浮点数保留位数）
- 数组/列表输出注意格式：[1, 2, 3] 还是 1 2 3
- 字符串输出注意是否包含换行或空格
- 建议先用简单的暴力方法手动验证期望值的正确性

题目分析：
{problem_analysis}

请用以下 JSON 格式返回测试用例：
```json
{{
    "test_cases": [
        {{
            "input": "测试输入1",
            "expected": "期望输出1",
            "description": "测试描述，说明为什么选这个用例"
        }},
        ...
    ]
}}
```
"""


CODE_GENERATION_PROMPT = """根据题目分析和测试用例，编写 {language} 代码解决问题。

要求：
1. 代码必须完整可直接运行
2. 包含必要的输入处理
3. 添加关键步骤的注释
4. 时间/空间复杂度要满足约束

题目分析：
{problem_analysis}

测试用例：
{test_cases}

请只返回代码，不要返回其他说明。代码格式示例：

```python
def solution():
    # 读取输入
    n = int(input())
    ...
    
if __name__ == "__main__":
    solution()
```
"""


TEST_CASE_VALIDATION_PROMPT = """验证测试用例的正确性。

当前代码：
```python
{code}
```

执行结果：
- 成功: {success}
- 标准输出: {stdout}
- 错误输出: {stderr}

测试用例：
{test_cases}

题目分析：
{problem_analysis}

请分析以下问题：
1. 测试用例的期望值是否正确？（请根据题目要求重新计算验证）
2. 代码的输出格式是否符合题目要求？
3. 如果测试用例期望值有误，请提供正确的期望值

请以 JSON 格式返回：
```json
{{
    "test_cases_valid": true/false,
    "issues": [
        {{
            "test_index": 0,
            "issue_type": "wrong_expected/format_error/other",
            "description": "问题描述",
            "suggested_fix": "建议的修正值"
        }}
    ],
    "overall_assessment": "总体评估：测试用例正确/测试用例有误但代码正确/代码需要修复"
}}
```
"""


CODE_FIX_PROMPT = """代码执行出错，请分析错误并修复。

当前代码：
```python
{code}
```

执行结果：
- 成功: {success}
- 退出码: {exit_code}
- 错误类型: {error_type}
- 标准输出: {stdout}
- 错误输出: {stderr}

测试用例（用于判断是否是期望值错误）：
{test_cases}

执行历史（之前尝试过的修复）：
{history}

请分析错误原因，并返回修复后的完整代码。修复要点：
1. 如果编译错误，检查语法和头文件/导入
2. 如果运行时错误，检查数组越界、空指针、除零等
3. 如果超时，优化算法复杂度
4. 如果答案错误：
   - 首先检查测试用例的期望值是否合理
   - 如果多个测试用例都因同一原因失败，可能是期望值有误
   - 如果代码逻辑明显正确但输出不匹配，可能是输出格式问题
   - 检查边界情况处理

**重要**：如果怀疑是测试用例期望值错误（例如，简单题目的输出明显符合逻辑但与预期不符），请在代码注释中说明，但仍返回你认为正确的代码。

只返回修复后的代码，不要返回其他说明。
"""


FINAL_ANSWER_PROMPT = """基于所有执行结果，生成完整的解答报告。

题目：
{problem_description}

代码：
```python
{code}
```

执行历史：
{execution_history}

最终执行结果：
{final_result}

请生成以下内容的完整报告：
1. **题目理解**：简要概括题目要求
2. **解题思路**：详细说明算法思想和步骤
3. **代码实现**：代码说明（已提供，简要说明关键点）
4. **复杂度分析**：时间复杂度和空间复杂度
5. **执行结果**：是否通过所有测试用例
6. **总结**：关键点和易错点
"""


# LangGraph节点实现
class AgentNodes:
    """Agent 节点集合"""

    def __init__(self, llm):
        self.llm = llm
        self.code_executor = CodeExecutor(timeout=5)
    
    def analyze_problem(self, state: AgentState) -> Dict[str, Any]:
        """
        分析题目节点
        """
        print("\n🔍 [Node] 分析题目...")
        
        prompt = ChatPromptTemplate.from_template(ANALYSIS_PROMPT)
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
        
        print(f"✅ 题目分析完成")
        
        return {
            "problem_analysis": analysis_str,
            "messages": [AIMessage(content=f"题目分析:\n{analysis_str}")],
            "next_step": "generate_test_cases"
        }
    
    def generate_test_cases(self, state: AgentState) -> Dict[str, Any]:
        """
        生成测试用例节点。自动生成覆盖正常和边界情况的测试用例。
        """
        print("\n📝 [Node] 生成测试用例...")
        
        prompt = ChatPromptTemplate.from_template(TEST_CASE_GENERATION_PROMPT)
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
                    "passed": None
                })
        except Exception as e:
            print(f"⚠️ 测试用例解析失败: {e}")
            # 使用默认测试用例
            test_cases = [{"input": "", "expected": "", "actual": None, "passed": None}]
        
        print(f"✅ 生成 {len(test_cases)} 个测试用例")
        
        return {
            "test_cases": test_cases,
            "messages": [AIMessage(content=f"生成测试用例: {len(test_cases)} 个")],
            "next_step": "generate_code"
        }
    
    def generate_code(self, state: AgentState) -> Dict[str, Any]:
        """
        生成代码节点。基于题目分析和测试用例生成初始代码。
        """
        print("\n💻 [Node] 生成代码...")
        
        prompt = ChatPromptTemplate.from_template(CODE_GENERATION_PROMPT)
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
        
        print(f"✅ 代码生成完成 ({len(code)} 字符)")
        
        return {
            "generated_code": code,
            "messages": [AIMessage(content=f"生成代码:\n```python\n{code}\n```")],
            "next_step": "execute_code"
        }
    
    def execute_code(self, state: AgentState) -> Dict[str, Any]:
        """
        执行代码节点。使用代码执行器运行生成的代码，并收集结果。
        """
        print("\n▶️  [Node] 执行代码...")
        
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
                    passed = "✅" in line or "成功" in line or "passed" in line.lower()
                    test_cases[i]["passed"] = passed
        
        print(f"✅ 执行完成 - 成功: {result.success}, 错误: {result.error_type or '无'}")
        
        return {
            "execution_result": result_dict,
            "messages": [AIMessage(content=f"执行结果:\n{result}")],
            "next_step": "analyze_result"
        }
    
    def analyze_result(self, state: AgentState) -> Dict[str, Any]:
        """
        分析结果节点。判断执行是否成功，决定下一步行动。
        包含测试用例验证和可信度评估机制。
        """
        print("\n📊 [Node] 分析结果...")
        
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
            print("✅ 代码执行成功！")
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
            print("🔍 验证测试用例正确性...")
            
            test_cases_str = json.dumps(
                state.get("test_cases", []),
                ensure_ascii=False,
                indent=2
            )
            
            prompt = ChatPromptTemplate.from_template(TEST_CASE_VALIDATION_PROMPT)
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
                print(f"测试用例验证: {content}")
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                validation = json.loads(content.strip())
                test_cases_valid = validation.get("test_cases_valid", True)
                issues = validation.get("issues", [])
                assessment = validation.get("overall_assessment", "")
                
                print(f"测试用例验证结果: {assessment}")
                
                # 如果测试用例有误，修正它们
                if not test_cases_valid and issues:
                    print("⚠️ 检测到测试用例错误，准备修正...")
                    
                    # 修正测试用例
                    test_cases = state.get("test_cases", [])
                    for issue in issues:
                        idx = issue.get("test_index", 0)
                        if 0 <= idx < len(test_cases):
                            old_expected = test_cases[idx].get("expected", "")
                            suggested_fix = issue.get("suggested_fix", old_expected)
                            test_cases[idx]["expected"] = suggested_fix
                            print(f"  修正用例 {idx}: '{old_expected}' -> '{suggested_fix}'")
                    
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
                print(f"✅ 测试用例验证通过，代码需要修复")
                
            except Exception as e:
                print(f"⚠️ 测试用例验证失败: {e}，继续正常修复流程")
        
        # 判断是否还有迭代次数
        if iteration >= max_iter:
            print(f"⚠️ 达到最大迭代次数 ({max_iter})，停止尝试")
            return {
                "execution_history": [history_entry],
                "iteration_count": iteration + 1,
                "messages": [AIMessage(content=f"达到最大迭代次数 ({max_iter})，未能解决问题。")],
                "next_step": "finish"
            }
        
        # 需要修复代码
        print(f"⚠️ 执行失败，准备修复代码 (迭代 {iteration + 1}/{max_iter})")
        
        return {
            "execution_history": [history_entry],
            "iteration_count": iteration + 1,
            "messages": [AIMessage(content=f"执行失败: {error_type or '未知错误'}，准备修复代码...")],
            "next_step": "fix_code"
        }
    
    def fix_code(self, state: AgentState) -> Dict[str, Any]:
        """
        修复代码节点。分析错误原因，生成修复后的代码。
        """
        print("\n🔧 [Node] 修复代码...")
        
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
        
        prompt = ChatPromptTemplate.from_template(CODE_FIX_PROMPT)
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
        
        print(f"✅ 代码修复完成 ({len(fixed_code)} 字符)")
        
        # 更新历史记录中的修复说明
        if history:
            print(result)
            error_type = result.get("error_type") or "错误"
            history[-1]["fixes"] = "修复 " + error_type
        
        return {
            "generated_code": fixed_code,
            "messages": [AIMessage(content=f"修复后的代码:\n```python\n{fixed_code}\n```")],
            "next_step": "execute_code"  # 循环回执行
        }
    
    def create_final_answer(self, state: AgentState) -> Dict[str, Any]:
        """
        生成最终答案节点。整合所有信息，生成完整的解答报告。
        """
        print("\n✨ [Node] 生成最终答案...")
        
        is_solved = state.get("is_solved", False)
        
        if is_solved:
            # 生成完整报告
            prompt = ChatPromptTemplate.from_template(FINAL_ANSWER_PROMPT)
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
        
        print("✅ 最终答案生成完成")
        
        return {
            "final_answer": final_answer,
            "messages": [AIMessage(content=final_answer)]
        }
