import re
import json
from typing import Dict, List, Any, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

class Tool:
    """工具基类"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, input_text: str) -> str:
        raise NotImplementedError

class Calculator(Tool):
    """计算器工具"""
    def __init__(self):
        super().__init__(
            name="calculator",
            description="执行数学计算，输入数学表达式如: 2+3*4"
        )
    
    def execute(self, input_text: str) -> str:
        try:
            # 模拟计算延迟
            time.sleep(0.5)
            allowed_chars = set('0123456789+-*/().')
            if not all(c in allowed_chars or c.isspace() for c in input_text):
                return "错误：包含不允许的字符"
            
            result = eval(input_text)
            return str(result)
        except Exception as e:
            return f"计算错误: {str(e)}"

class Search(Tool):
    """模拟搜索工具"""
    def __init__(self):
        super().__init__(
            name="search",
            description="搜索信息，输入搜索关键词"
        )
        self.knowledge = {
            "北京": "北京是中国的首都，人口约2100万",
            "上海": "上海是中国最大的城市，人口约2400万",
            "python": "Python是一种高级编程语言，广泛用于数据科学和AI",
            "天气": "今天北京天气晴朗，温度25度",
            "股票": "今日股市上涨2.5%，科技股表现强劲",
            "新闻": "最新科技新闻：AI技术在各行业应用加速",
            "react": "ReAct是一个结合推理和行动的AI框架",
            "价格": "当前商品平均价格为100元",
            "销量": "本月销量达到1000件"
        }
    
    def execute(self, input_text: str) -> str:
        try:
            # 模拟搜索延迟
            time.sleep(1.0)
            query = input_text.lower().strip()
            for key, value in self.knowledge.items():
                if key in query:
                    return value
            return f"未找到关于'{input_text}'的信息"
        except Exception as e:
            return f"搜索错误: {str(e)}"

class FileWriter(Tool):
    """文件写入工具"""
    def __init__(self):
        super().__init__(
            name="file_writer",
            description="将内容写入文件，格式: filename|content"
        )
    
    def execute(self, input_text: str) -> str:
        try:
            # 模拟写入延迟
            time.sleep(0.3)
            if '|' not in input_text:
                return "错误：格式应为 filename|content"
            
            filename, content = input_text.split('|', 1)
            filename = filename.strip()
            content = content.strip()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"成功写入文件: {filename}"
        except Exception as e:
            return f"文件写入错误: {str(e)}"

class Task:
    """任务节点"""
    def __init__(self, task_id: str, tool_name: str, tool_input: str, dependencies: List[str] = None):
        self.task_id = task_id
        self.tool_name = tool_name
        self.tool_input = tool_input
        self.dependencies = dependencies or []
        self.result = None
        self.status = "pending"  # pending, running, completed, failed
        self.start_time = None
        self.end_time = None
    
    def __str__(self):
        status_symbol = {
            "pending": "○",
            "running": "⟳",
            "completed": "✓",
            "failed": "✗"
        }
        return f"{status_symbol.get(self.status, '?')} {self.task_id}: {self.tool_name}[{self.tool_input}]"

class DAGExecutor:
    """DAG执行器"""
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.tasks = {}
        self.results = {}
        self.lock = threading.Lock()
    
    def add_task(self, task: Task):
        """添加任务到DAG"""
        self.tasks[task.task_id] = task
    
    def get_ready_tasks(self) -> List[Task]:
        """获取可以执行的任务（依赖已完成）"""
        ready_tasks = []
        for task in self.tasks.values():
            if task.status == "pending":
                # 检查所有依赖是否已完成
                dependencies_completed = all(
                    self.tasks[dep_id].status == "completed" 
                    for dep_id in task.dependencies
                    if dep_id in self.tasks
                )
                if dependencies_completed:
                    ready_tasks.append(task)
        return ready_tasks
    
    def resolve_dependencies(self, task: Task) -> str:
        """解析任务输入中的依赖引用"""
        input_text = task.tool_input
        
        # 查找 $task_id 格式的依赖引用
        pattern = r'\$(\w+)'
        matches = re.findall(pattern, input_text)
        
        for match in matches:
            if match in self.results:
                # 替换依赖引用为实际结果
                input_text = input_text.replace(f'${match}', str(self.results[match]))
        
        return input_text
    
    def execute_task(self, task: Task, tools: Dict[str, Tool]) -> str:
        """执行单个任务"""
        with self.lock:
            task.status = "running"
            task.start_time = time.time()
        
        try:
            # 解析依赖
            resolved_input = self.resolve_dependencies(task)
            
            # 执行工具
            if task.tool_name in tools:
                result = tools[task.tool_name].execute(resolved_input)
                
                with self.lock:
                    task.result = result
                    task.status = "completed"
                    task.end_time = time.time()
                    self.results[task.task_id] = result
                
                return result
            else:
                error_msg = f"未知工具: {task.tool_name}"
                with self.lock:
                    task.result = error_msg
                    task.status = "failed"
                    task.end_time = time.time()
                return error_msg
                
        except Exception as e:
            error_msg = f"执行错误: {str(e)}"
            with self.lock:
                task.result = error_msg
                task.status = "failed"
                task.end_time = time.time()
            return error_msg
    
    def execute_dag(self, tools: Dict[str, Tool]) -> Dict[str, str]:
        """并行执行DAG"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {}
            
            while True:
                # 获取可执行的任务
                ready_tasks = self.get_ready_tasks()
                
                if not ready_tasks:
                    # 检查是否还有未完成的任务
                    pending_tasks = [t for t in self.tasks.values() if t.status in ["pending", "running"]]
                    if not pending_tasks:
                        break  # 所有任务完成
                    
                    # 等待正在运行的任务完成
                    if future_to_task:
                        completed_futures = as_completed(future_to_task.keys(), timeout=1.0)
                        for future in completed_futures:
                            task = future_to_task[future]
                            try:
                                future.result()  # 获取结果，触发异常处理
                            except Exception as e:
                                print(f"任务 {task.task_id} 执行失败: {e}")
                            finally:
                                del future_to_task[future]
                    continue
                
                # 提交可执行的任务
                for task in ready_tasks:
                    future = executor.submit(self.execute_task, task, tools)
                    future_to_task[future] = task
                
                # 等待至少一个任务完成
                if future_to_task:
                    completed_futures = as_completed(future_to_task.keys(), timeout=1.0)
                    for future in completed_futures:
                        task = future_to_task[future]
                        try:
                            future.result()
                        except Exception as e:
                            print(f"任务 {task.task_id} 执行失败: {e}")
                        finally:
                            del future_to_task[future]
                        break  # 只处理一个完成的任务，然后重新评估
        
        return self.results

class LLMCompilerAgent:
    """LLM Compiler Agent - 将任务编译为DAG并并行执行"""
    
    def __init__(self, tools: List[Tool], max_workers: int = 3):
        self.tools = {tool.name: tool for tool in tools}
        self.max_workers = max_workers
        self.dag_executor = None
    
    def _get_tool_descriptions(self) -> str:
        """获取工具描述"""
        descriptions = []
        for tool in self.tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)
    
    def _compile_to_dag(self, question: str) -> DAGExecutor:
        """将问题编译为DAG（简化版规则）"""
        executor = DAGExecutor(self.max_workers)
        question_lower = question.lower()
        
        if "计算" in question_lower and "搜索" in question_lower:
            # 复合任务：搜索后计算
            executor.add_task(Task("search1", "search", "价格"))
            executor.add_task(Task("search2", "search", "销量"))
            executor.add_task(Task("calc1", "calculator", "$search1 * $search2", ["search1", "search2"]))
            
        elif "报告" in question_lower or "总结" in question_lower:
            # 并行搜索多个信息源
            executor.add_task(Task("weather", "search", "天气"))
            executor.add_task(Task("stock", "search", "股票"))
            executor.add_task(Task("news", "search", "新闻"))
            executor.add_task(Task("report", "file_writer", "report.txt|天气: $weather\n股票: $stock\n新闻: $news", 
                             ["weather", "stock", "news"]))
            
        elif "比较" in question_lower:
            # 并行搜索进行比较
            keywords = self._extract_keywords(question)
            if len(keywords) >= 2:
                executor.add_task(Task("info1", "search", keywords[0]))
                executor.add_task(Task("info2", "search", keywords[1]))
                executor.add_task(Task("compare", "file_writer", f"comparison.txt|{keywords[0]}: $info1\n{keywords[1]}: $info2", 
                                 ["info1", "info2"]))
        
        elif "计算" in question_lower:
            # 简单计算任务
            math_expr = self._extract_math_expression(question)
            if math_expr:
                executor.add_task(Task("calc", "calculator", math_expr))
        
        elif "搜索" in question_lower:
            # 搜索任务
            keywords = self._extract_keywords(question)
            for i, keyword in enumerate(keywords):
                executor.add_task(Task(f"search{i+1}", "search", keyword))
        
        else:
            # 默认搜索
            executor.add_task(Task("default", "search", question[:20]))
        
        return executor
    
    def _extract_math_expression(self, text: str) -> str:
        """提取数学表达式"""
        pattern = r'[\d+\-*/().\s]+'
        matches = re.findall(pattern, text)
        if matches:
            return max(matches, key=len).strip()
        return ""
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = ["北京", "上海", "python", "天气", "股票", "新闻", "react", "价格", "销量"]
        found_keywords = []
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        return found_keywords if found_keywords else ["信息"]
    
    def run(self, question: str) -> str:
        """运行LLM Compiler流程"""
        print(f"问题: {question}\n")
        
        # 阶段1: 编译为DAG
        print("=== 编译阶段 ===")
        self.dag_executor = self._compile_to_dag(question)
        
        if not self.dag_executor.tasks:
            return "无法为此问题生成执行计划"
        
        print("生成的DAG任务:")
        for task in self.dag_executor.tasks.values():
            deps = f" (依赖: {', '.join(task.dependencies)})" if task.dependencies else ""
            print(f"  {task}{deps}")
        print()
        
        # 阶段2: 并行执行DAG
        print("=== 执行阶段 ===")
        start_time = time.time()
        
        # 实时显示执行状态
        def print_status():
            while True:
                with self.dag_executor.lock:
                    all_completed = all(task.status in ["completed", "failed"] for task in self.dag_executor.tasks.values())
                    
                    print("\r执行状态: ", end="")
                    for task in self.dag_executor.tasks.values():
                        print(f"{task.task_id}({task.status[:1]}) ", end="")
                    print("", end="", flush=True)
                    
                    if all_completed:
                        break
                
                time.sleep(0.5)
        
        # 启动状态显示线程
        import threading
        status_thread = threading.Thread(target=print_status, daemon=True)
        status_thread.start()
        
        # 执行DAG
        results = self.dag_executor.execute_dag(self.tools)
        
        end_time = time.time()
        print(f"\n执行完成，总耗时: {end_time - start_time:.2f}秒\n")
        
        # 阶段3: 生成结果
        print("=== 结果阶段 ===")
        self._print_execution_summary()
        
        final_result = self._generate_final_answer(question, results)
        print(f"最终答案: {final_result}")
        return final_result
    
    def _print_execution_summary(self):
        """打印执行摘要"""
        print("执行摘要:")
        for task in self.dag_executor.tasks.values():
            duration = ""
            if task.start_time and task.end_time:
                duration = f" ({task.end_time - task.start_time:.2f}s)"
            print(f"  {task}{duration}")
            if task.result:
                print(f"    结果: {task.result}")
        print()
    
    def _generate_final_answer(self, question: str, results: Dict[str, str]) -> str:
        """生成最终答案"""
        if not results:
            return "执行完成，但没有结果"
        
        question_lower = question.lower()
        
        if "报告" in question_lower:
            return "已生成综合报告文件"
        elif "比较" in question_lower:
            return "已生成比较分析文件"
        elif "计算" in question_lower:
            calc_results = [v for k, v in results.items() if k.startswith("calc")]
            if calc_results:
                return f"计算结果: {calc_results[0]}"
        
        # 返回所有结果的摘要
        if len(results) == 1:
            return list(results.values())[0]
        else:
            return f"完成 {len(results)} 个任务: " + "; ".join(f"{k}={v}" for k, v in results.items())

def main():
    """演示用法"""
    # 创建工具
    tools = [
        Calculator(),
        Search(),
        FileWriter()
    ]
    
    # 创建Agent
    agent = LLMCompilerAgent(tools, max_workers=3)
    
    # 测试问题
    questions = [
        "搜索价格和销量信息，然后计算总收入",
        "生成包含天气、股票和新闻的综合报告",
        "比较北京和上海的信息",
        "计算 (25 + 15) * 3 的结果"
    ]
    
    for question in questions:
        print("=" * 70)
        result = agent.run(question)
        print("=" * 70)
        print()

if __name__ == "__main__":
    main()
