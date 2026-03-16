#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/16
# @File     : test_agent.py
# @Project  : AlgoMate
"""
Agent 功能测试脚本

运行方式：
    python test_agent.py

测试内容：
1. 代码执行器功能
2. ReAct Agent 基本流程
"""

import sys
import os


def test_code_executor():
    """测试代码执行器"""
    print("\n" + "="*60)
    print("测试 1: 代码执行器")
    print("="*60)
    
    from tools.code_executor import CodeExecutor, execute_code
    
    executor = CodeExecutor(timeout=5)
    print(f"执行器后端: {executor.backend_type}")
    
    # 测试 1.1: Python 执行
    print("\n--- 测试 Python 执行 ---")
    python_code = '''
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# 读取输入
import ast
nums = ast.literal_eval(input())
target = int(input())
result = two_sum(nums, target)
print(result)
'''
    
    test_cases = [
        ("[2, 7, 11, 15]\n9\n", "[0, 1]"),
        ("[3, 2, 4]\n6\n", "[1, 2]"),
    ]
    
    result = executor.execute(python_code, "python", test_cases=test_cases)
    print(f"成功: {result.success}")
    print(f"输出:\n{result.stdout}")
    if result.stderr:
        print(f"错误: {result.stderr}")
    
    # 测试 1.2: 错误检测
    print("\n--- 测试编译错误检测 ---")
    error_code = '''
def broken(
    print("syntax error"
'''
    
    result = executor.execute(error_code, "python")
    print(f"成功: {result.success}")
    print(f"错误类型: {result.error_type}")
    
    # 测试 1.3: 超时检测
    print("\n--- 测试超时检测 ---")
    timeout_code = '''
while True:
    pass
'''
    
    result = execute_code(timeout_code, "python", timeout=2)
    print(f"成功: {result.success}")
    print(f"错误类型: {result.error_type}")
    
    print("\n✅ 代码执行器测试完成")


def test_react_agent():
    """测试 ReAct Agent"""
    print("\n" + "="*60)
    print("测试 2: ReAct Agent")
    print("="*60)
    
    try:
        from agent.react_agent import AlgoMateAgent
        
        # 简单测试题目
        test_problem = """
实现一个函数，计算两个整数的和。

输入：两个整数 a 和 b
输出：它们的和

示例：
输入：3 5
输出：8
"""
        
        print("\n题目:")
        print(test_problem)
        
        agent = AlgoMateAgent(max_iterations=3)
        result = agent.solve(test_problem, language="python")
        
        print("\n--- 执行历史 ---")
        history = result.get("execution_history", [])
        for h in history:
            print(f"尝试 {h['iteration']}: {h['result'].get('error_type', '成功')}")
        
        print("\n--- 生成的代码 ---")
        print(result.get("generated_code", "无"))
        
        print("\n--- 是否解决 ---")
        print(f"is_solved: {result.get('is_solved', False)}")
        
        print("\n✅ ReAct Agent 测试完成")
        
    except Exception as e:
        print(f"❌ Agent 测试失败: {e}")
        import traceback
        traceback.print_exc()


def check_dependencies():
    """检查依赖"""
    print("\n" + "="*60)
    print("依赖检查")
    print("="*60)
    
    dependencies = {
        "langchain": False,
        "langchain-core": False,
        "langgraph": False,
        "streamlit": False,
        "chromadb": False,
    }
    
    try:
        import langchain
        dependencies["langchain"] = True
        print("✅ langchain")
    except:
        print("❌ langchain - pip install langchain")
    
    try:
        import langchain_core
        dependencies["langchain-core"] = True
        print("✅ langchain-core")
    except:
        print("❌ langchain-core - pip install langchain-core")
    
    try:
        import langgraph
        dependencies["langgraph"] = True
        print("✅ langgraph")
    except:
        print("❌ langgraph - pip install langgraph")
    
    try:
        import streamlit
        dependencies["streamlit"] = True
        print("✅ streamlit")
    except:
        print("❌ streamlit - pip install streamlit")
    
    try:
        import chromadb
        dependencies["chromadb"] = True
        print("✅ chromadb")
    except:
        print("❌ chromadb - pip install chromadb")
    
    # 可选依赖
    try:
        import docker
        print("✅ docker (可选)")
    except:
        print("⚠️ docker (可选) - pip install docker，用于更安全的代码执行")
    
    return all(dependencies.values())


def main():
    """主函数"""
    print("\n" + "="*60)
    print("AlgoMate Agent 测试")
    print("="*60)
    
    # 检查依赖
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\n⚠️ 部分依赖缺失，请安装:")
        print("pip install langchain langchain-core langgraph streamlit chromadb")
        return
    
    # 测试代码执行器
    try:
        test_code_executor()
    except Exception as e:
        print(f"\n❌ 代码执行器测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试 ReAct Agent
    try:
        test_react_agent()
    except Exception as e:
        print(f"\n❌ ReAct Agent 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    main()
