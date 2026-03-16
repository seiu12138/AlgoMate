#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/16
# @File     : code_executor.py
# @Project  : AlgoMate
import os
import re
import signal
import subprocess
import tempfile
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List


class Language(Enum):
    PYTHON = "python"
    CPP = "cpp"
    JAVA = "java"


@dataclass
class ExecutionResult:
    """代码执行结果"""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float  # 毫秒
    memory_usage: int  # KB
    error_type: Optional[str] = None  # 'compile_error', 'runtime_error', 'timeout', 'memory_limit', None
    
    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "execution_time": self.execution_time,
            "memory_usage": self.memory_usage,
            "error_type": self.error_type
        }
    
    def __str__(self) -> str:
        status = "✅ 成功" if self.success else "❌ 失败"
        return f"""
        执行结果: {status}
        退出码: {self.exit_code}
        错误类型: {self.error_type or '无'}
        执行时间: {self.execution_time:.2f}ms
        内存使用: {self.memory_usage}KB
        
        --- 标准输出 ---
        {self.stdout}
        
        --- 错误输出 ---
        {self.stderr}
        """


class SubprocessSandbox:
    """
    基于子进程的受限执行环境
    """
    
    DEFAULT_TIMEOUT = 10  # 秒
    DEFAULT_MEMORY_LIMIT = 256 * 1024 * 1024  # 256MB
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, memory_limit: int = DEFAULT_MEMORY_LIMIT):
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.temp_dir = tempfile.mkdtemp(prefix="algomate_sandbox_")
    
    def _kill_process_tree(self, pid: int):
        """递归终止进程树"""
        try:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)],
                             capture_output=True)
            else:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
        except:
            pass
    
    def _run_with_timeout(self, cmd: List[str], cwd: str, 
                         input_data: Optional[str] = None) -> tuple:
        """带超时控制的命令执行"""
        process = None
        try:
            if os.name != 'nt':
                # Unix 系统：使用进程组以便终止整个进程树
                process = subprocess.Popen(
                    cmd,
                    cwd=cwd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    preexec_fn=os.setsid
                )
            else:
                # Windows
                process = subprocess.Popen(
                    cmd,
                    cwd=cwd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            
            stdout, stderr = process.communicate(input=input_data, timeout=self.timeout)
            return process.returncode, stdout, stderr, False
            
        except subprocess.TimeoutExpired:
            if process:
                self._kill_process_tree(process.pid)
                process.wait()
            return -1, "", "执行超时", True
        except Exception as e:
            if process:
                process.kill()
            return -1, "", f"执行异常: {str(e)}", False
    
    def _detect_language(self, code: str) -> Language:
        """根据代码特征检测语言"""
        code = code.strip()
        
        # C++ 特征
        if any(keyword in code for keyword in ['#include', 'using namespace', 'std::', 'cout <<']):
            return Language.CPP
        
        # Java 特征
        if 'public class' in code or 'public static void main' in code:
            return Language.JAVA
        
        # 默认 Python
        return Language.PYTHON
    
    def _extract_python_function(self, code: str, function_name: str = "solution") -> Optional[str]:
        """从代码中提取指定函数"""
        # 匹配函数定义
        pattern = rf'def\s+{function_name}\s*\([^)]*\)(?:\s*->\s*\w+)?\s*:'
        if re.search(pattern, code):
            return function_name
        return None
    
    def execute(self, code: str, language: Optional[Language] = None,
                input_data: Optional[str] = None, 
                test_cases: Optional[List[tuple]] = None) -> ExecutionResult:
        """
        进程受限环境执行代码
        
        :param code: 源代码字符串
        :param language: 编程语言 ('python', 'cpp', 'java'，自动检测)
        :param input_data: 标准输入数据
        :param test_cases: 测试用例列表 [(input, expected_output), ...]
        :return: ExecutionResult
        """
        import time
        
        if language is None:
            language = self._detect_language(code)
        
        start_time = time.time()
        
        try:
            if language == Language.PYTHON:
                result = self._execute_python(code, input_data, test_cases)
            elif language == Language.CPP:
                result = self._execute_cpp(code, input_data, test_cases)
            elif language == Language.JAVA:
                result = self._execute_java(code, input_data, test_cases)
            else:
                result = ExecutionResult(
                    success=False,
                    stdout="",
                    stderr=f"不支持的语言: {language}",
                    exit_code=-1,
                    execution_time=0,
                    memory_usage=0,
                    error_type="unsupported_language"
                )
        except Exception as e:
            result = ExecutionResult(
                success=False,
                stdout="",
                stderr=f"执行器异常: {str(e)}",
                exit_code=-1,
                execution_time=(time.time() - start_time) * 1000,
                memory_usage=0,
                error_type="executor_error"
            )
        
        return result
    
    def _execute_python(self, code: str, input_data: Optional[str],
                       test_cases: Optional[List[tuple]]) -> ExecutionResult:
        """执行 Python 代码"""
        import time
        
        start_time = time.time()
        
        # 创建临时文件
        temp_file = os.path.join(self.temp_dir, "solution.py")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # 如果有多个测试用例，逐一执行
        if test_cases:
            results = []
            all_passed = True
            
            for i, (test_input, expected) in enumerate(test_cases):
                cmd = ['python', temp_file]
                exit_code, stdout, stderr, timeout = self._run_with_timeout(
                    cmd, self.temp_dir, test_input
                )
                
                if timeout:
                    return ExecutionResult(
                        success=False,
                        stdout="",
                        stderr=f"测试用例 {i+1} 执行超时",
                        exit_code=-1,
                        execution_time=self.timeout * 1000,
                        memory_usage=0,
                        error_type="timeout"
                    )
                
                passed = stdout.strip() == expected.strip() if expected else exit_code == 0
                if not passed:
                    all_passed = False
                    results.append(f"用例 {i+1}: ❌\n输入: {test_input}\n输出: {stdout.strip()}\n期望: {expected}")
                else:
                    results.append(f"用例 {i+1}: ✅")
            
            exec_time = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=all_passed,
                stdout="\n".join(results),
                stderr="",
                exit_code=0 if all_passed else 1,
                execution_time=exec_time,
                memory_usage=0
            )
        
        # 单个执行
        cmd = ['python', temp_file]
        exit_code, stdout, stderr, timeout = self._run_with_timeout(
            cmd, self.temp_dir, input_data
        )
        
        exec_time = (time.time() - start_time) * 1000
        
        if timeout:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="执行超时（可能包含死循环）",
                exit_code=-1,
                execution_time=self.timeout * 1000,
                memory_usage=0,
                error_type="timeout"
            )
        
        return ExecutionResult(
            success=exit_code == 0,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            execution_time=exec_time,
            memory_usage=0,
            error_type="runtime_error" if exit_code != 0 else None
        )
    
    def _execute_cpp(self, code: str, input_data: Optional[str],
                    test_cases: Optional[List[tuple]]) -> ExecutionResult:
        """执行 C++ 代码"""
        import time
        
        start_time = time.time()
        
        # 创建源文件
        source_file = os.path.join(self.temp_dir, "solution.cpp")
        exe_file = os.path.join(self.temp_dir, "solution.exe" if os.name == 'nt' else "solution")
        
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # 编译
        compile_cmd = ['g++', '-std=c++17', '-O2', source_file, '-o', exe_file]
        exit_code, stdout, stderr, timeout = self._run_with_timeout(compile_cmd, self.temp_dir)
        
        if exit_code != 0:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"编译错误:\n{stderr}",
                exit_code=exit_code,
                execution_time=(time.time() - start_time) * 1000,
                memory_usage=0,
                error_type="compile_error"
            )
        
        # 执行
        if test_cases:
            results = []
            all_passed = True
            
            for i, (test_input, expected) in enumerate(test_cases):
                exit_code, stdout, stderr, timeout = self._run_with_timeout(
                    [exe_file], self.temp_dir, test_input
                )
                
                if timeout:
                    return ExecutionResult(
                        success=False,
                        stdout="",
                        stderr=f"测试用例 {i+1} 执行超时",
                        exit_code=-1,
                        execution_time=self.timeout * 1000,
                        memory_usage=0,
                        error_type="timeout"
                    )
                
                passed = stdout.strip() == expected.strip() if expected else exit_code == 0
                if not passed:
                    all_passed = False
                    results.append(f"用例 {i+1}: ❌\n输入: {test_input}\n输出: {stdout.strip()}\n期望: {expected}")
                else:
                    results.append(f"用例 {i+1}: ✅")
            
            exec_time = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=all_passed,
                stdout="\n".join(results),
                stderr="",
                exit_code=0 if all_passed else 1,
                execution_time=exec_time,
                memory_usage=0
            )
        
        exit_code, stdout, stderr, timeout = self._run_with_timeout(
            [exe_file], self.temp_dir, input_data
        )
        
        exec_time = (time.time() - start_time) * 1000
        
        if timeout:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="执行超时（可能包含死循环）",
                exit_code=-1,
                execution_time=self.timeout * 1000,
                memory_usage=0,
                error_type="timeout"
            )
        
        return ExecutionResult(
            success=exit_code == 0,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            execution_time=exec_time,
            memory_usage=0,
            error_type="runtime_error" if exit_code != 0 else None
        )
    
    def _execute_java(self, code: str, input_data: Optional[str],
                     test_cases: Optional[List[tuple]]) -> ExecutionResult:
        """执行 Java 代码"""
        import time
        
        start_time = time.time()
        
        # 提取类名
        match = re.search(r'public\s+class\s+(\w+)', code)
        if not match:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="找不到 public class，请确保代码包含 public class 类名",
                exit_code=-1,
                execution_time=0,
                memory_usage=0,
                error_type="compile_error"
            )
        
        class_name = match.group(1)
        source_file = os.path.join(self.temp_dir, f"{class_name}.java")
        
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # 编译
        compile_cmd = ['javac', source_file]
        exit_code, stdout, stderr, timeout = self._run_with_timeout(compile_cmd, self.temp_dir)
        
        if exit_code != 0:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"编译错误:\n{stderr}",
                exit_code=exit_code,
                execution_time=(time.time() - start_time) * 1000,
                memory_usage=0,
                error_type="compile_error"
            )
        
        # 执行
        if test_cases:
            results = []
            all_passed = True
            
            for i, (test_input, expected) in enumerate(test_cases):
                exit_code, stdout, stderr, timeout = self._run_with_timeout(
                    ['java', '-cp', self.temp_dir, class_name], self.temp_dir, test_input
                )
                
                if timeout:
                    return ExecutionResult(
                        success=False,
                        stdout="",
                        stderr=f"测试用例 {i+1} 执行超时",
                        exit_code=-1,
                        execution_time=self.timeout * 1000,
                        memory_usage=0,
                        error_type="timeout"
                    )
                
                passed = stdout.strip() == expected.strip() if expected else exit_code == 0
                if not passed:
                    all_passed = False
                    results.append(f"用例 {i+1}: ❌\n输入: {test_input}\n输出: {stdout.strip()}\n期望: {expected}")
                else:
                    results.append(f"用例 {i+1}: ✅")
            
            exec_time = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=all_passed,
                stdout="\n".join(results),
                stderr="",
                exit_code=0 if all_passed else 1,
                execution_time=exec_time,
                memory_usage=0
            )
        
        exit_code, stdout, stderr, timeout = self._run_with_timeout(
            ['java', '-cp', self.temp_dir, class_name], self.temp_dir, input_data
        )
        
        exec_time = (time.time() - start_time) * 1000
        
        if timeout:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="执行超时（可能包含死循环）",
                exit_code=-1,
                execution_time=self.timeout * 1000,
                memory_usage=0,
                error_type="timeout"
            )
        
        return ExecutionResult(
            success=exit_code == 0,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            execution_time=exec_time,
            memory_usage=0,
            error_type="runtime_error" if exit_code != 0 else None
        )


class DockerSandbox:
    """
    Docker环境验证
    """
    def __init__(self, timeout: int = 10, memory_limit: str = "512m", cpu_limit: float = 1.0):
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self.available = self._check_docker()
    
    def _check_docker(self) -> bool:
        """检查 Docker 是否可用"""
        try:
            import docker
            client = docker.from_env()
            client.ping()
            return True
        except:
            return False
    
    def execute(self, code: str,
                language: Language,
                input_data: Optional[str] = None,
                test_cases: Optional[List[tuple]] = None) -> ExecutionResult:
        """
        基于Docker环境执行的代码

        :param code: 源代码字符串
        :param language: 编程语言 ('python', 'cpp', 'java'，自动检测)
        :param input_data: 标准输入数据
        :param test_cases: 测试用例列表 [(input, expected_output), ...]
        :return: ExecutionResult
        """
        if not self.available:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="Docker 不可用，请使用 SubprocessSandbox",
                exit_code=-1,
                execution_time=0,
                memory_usage=0,
                error_type="docker_unavailable"
            )

        import docker
        
        client = docker.from_env()
        
        # 根据语言选择镜像
        image_map = {
            Language.PYTHON: "python:3.11-slim",
            Language.CPP: "gcc:latest",
            Language.JAVA: "openjdk:17-slim"
        }
        
        image = image_map.get(language, "python:3.11-slim")
        
        # 构建执行命令(简单调用echo命令执行)
        cmd = f"echo '{code}' | python3"
        
        try:
            container = client.containers.run(
                image,
                cmd,
                detach=True,
                mem_limit=self.memory_limit,
                cpu_period=100000,
                cpu_quota=int(100000 * self.cpu_limit),
                network_mode="none",  # 无网络
                read_only=True,  # 只读文件系统
            )
            
            result = container.wait(timeout=self.timeout)
            logs = container.logs().decode('utf-8')
            container.remove(force=True)
            
            return ExecutionResult(
                success=result['StatusCode'] == 0,
                stdout=logs,
                stderr="",
                exit_code=result['StatusCode'],
                execution_time=0,
                memory_usage=0
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Docker 执行错误: {str(e)}",
                exit_code=-1,
                execution_time=0,
                memory_usage=0,
                error_type="docker_error"
            )


class CodeExecutor:
    def __init__(self, timeout: int = 10, memory_limit: int = 256 * 1024 * 1024,
                 prefer_docker: bool = True):
        self.timeout = timeout
        self.memory_limit = memory_limit
        
        # 优先尝试Docker环境
        if prefer_docker:
            docker_sandbox = DockerSandbox(timeout, f"{memory_limit // 1024 // 1024}m")
            if docker_sandbox.available:
                self.backend = docker_sandbox
                self.backend_type = "docker"
                return
        
        # 回退到 Subprocess
        self.backend = SubprocessSandbox(timeout, memory_limit)
        self.backend_type = "subprocess"
    
    def execute(self, code: str, language: Optional[str] = None,
                input_data: Optional[str] = None,
                test_cases: Optional[List[tuple]] = None) -> ExecutionResult:
        """
        代码执行

        :param code: 源代码字符串
        :param language: 编程语言 ('python', 'cpp', 'java'，自动检测)
        :param input_data: 标准输入数据
        :param test_cases: 测试用例列表 [(input, expected_output), ...]
        :return:
        """
        lang_enum = None
        if language:
            lang_map = {
                'python': Language.PYTHON,
                'cpp': Language.CPP,
                'c++': Language.CPP,
                'java': Language.JAVA
            }
            lang_enum = lang_map.get(language.lower())
        
        return self.backend.execute(code, lang_enum, input_data, test_cases)
    
    def get_backend_info(self) -> dict:
        """获取执行环境信息"""
        return {
            "type": self.backend_type,
            "timeout": self.timeout,
            "memory_limit": self.memory_limit
        }


def execute_code(code: str,
                 language: Optional[str] = None,
                 input_data: Optional[str] = None,
                 test_cases: Optional[List[tuple]] = None,
                 timeout: int = 10) -> ExecutionResult:
    """
    代码执行函数

    Example:
        >>> result = execute_code("print('Hello')", language="python")
        >>> print(result.stdout)
        Hello

    :param code: 待执行的代码
    :param language: 待执行代码所用编程语言
    :param input_data: 待执行代码所需输入数据
    :param test_cases: 待执行代码的测试用例
    :param timeout: 代码超时时间
    :return:
    """
    executor = CodeExecutor(timeout=timeout)
    return executor.execute(code, language, input_data, test_cases)


if __name__ == "__main__":
    # 测试代码
    
    # 测试 Python
    print("=" * 50)
    print("测试 Python 执行")
    print("=" * 50)
    
    python_code = '''
print("Hello from Python!")
for i in range(5):
    print(f"Number: {i}")
    '''
    
    result = execute_code(python_code, language="python")
    print(result)
    
    # 测试 C++
    print("\n" + "=" * 50)
    print("测试 C++ 执行")
    print("=" * 50)
    
    cpp_code = '''
#include <iostream>
using namespace std;

int main() {
    cout << "Hello from C++!" << endl;
    for (int i = 0; i < 5; i++) {
        cout << "Number: " << i << endl;
    }
    return 0;
}
    '''
    
    result = execute_code(cpp_code, language="cpp")
    print(result)
    
    # 测试超时
    print("\n" + "=" * 50)
    print("测试超时检测")
    print("=" * 50)
    
    infinite_loop = '''
while True:
    pass
'''
    
    result = execute_code(infinite_loop, language="python", timeout=2)
    print(result)
