import re
import json
from typing import Dict, List, Any, Optional

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
            "新闻": "最新科技新闻：AI技术在各行业应用加速"
        }
    
    def execute(self, input_text: str) -> str:
        query = input_text.lower().strip()
        for key, value in self.knowledge.items():
            if key in query:
                return value
        return f"未找到关于'{input_text}'的信息"

class FileWriter(Tool):
    """文件写入工具"""
    def __init__(self):
        super().__init__(
            name="file_writer",
            description="将内容写入文件，格式: filename|content"
        )
    
    def execute(self, input_text: str) -> str:
        try:
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

class Step:
    """执行步骤"""
    def __init__(self, step_id: int, description: str, tool_name: str = None, tool_input: str = None):
        self.step_id = step_id
        self.description = description
        self.tool_name = tool_name
        self.tool_input = tool_input
        self.result = None
        self.completed = False
    
    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"{status} Step {self.step_id}: {self.description}"

class PlanAndExecuteAgent:
    """Plan-and-Execute Agent"""
    
    def __init__(self, tools: List[Tool], max_steps: int = 10):
        self.tools = {tool.name: tool for tool in tools}
        self.max_steps = max_steps
        self.plan = []
        self.execution_log = []
    
    def _get_tool_descriptions(self) -> str:
        """获取工具描述"""
        descriptions = []
        for tool in self.tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)
    
    def _create_plan(self, question: str) -> List[Step]:
        """创建执行计划（简化版规则）"""
        plan = []
        step_id = 1
        
        # 分析问题类型并生成计划
        question_lower = question.lower()
        
        if "计算" in question_lower or any(op in question for op in ['+', '-', '*', '/', '=']):
            # 数学计算任务
            math_expr = self._extract_math_expression(question)
            if math_expr:
                plan.append(Step(step_id, f"计算数学表达式: {math_expr}", "calculator", math_expr))
                step_id += 1
        
        elif "搜索" in question_lower or "查找" in question_lower or "什么是" in question_lower:
            # 搜索任务
            keywords = self._extract_keywords(question)
            for keyword in keywords:
                plan.append(Step(step_id, f"搜索关于'{keyword}'的信息", "search", keyword))
                step_id += 1
        
        elif "写入文件" in question_lower or "保存" in question_lower:
            # 文件操作任务
            plan.append(Step(step_id, "搜索相关信息", "search", "python"))
            step_id += 1
            plan.append(Step(step_id, "将信息写入文件", "file_writer", "info.txt|搜索到的信息"))
            step_id += 1
        
        elif "报告" in question_lower or "总结" in question_lower:
            # 复合任务：生成报告
            topics = ["天气", "股票", "新闻"]
            for topic in topics:
                plan.append(Step(step_id, f"搜索{topic}信息", "search", topic))
                step_id += 1
            plan.append(Step(step_id, "生成报告文件", "file_writer", "report.txt|综合报告内容"))
            step_id += 1
        
        else:
            # 默认：简单搜索
            plan.append(Step(step_id, "搜索相关信息", "search", question))
        
        return plan
    
    def _extract_math_expression(self, text: str) -> str:
        """提取数学表达式"""
        # 简单的数学表达式提取
        pattern = r'[\d+\-*/().\s]+'
        matches = re.findall(pattern, text)
        if matches:
            # 返回最长的匹配
            return max(matches, key=len).strip()
        return ""
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = ["北京", "上海", "python", "天气", "股票", "新闻"]
        found_keywords = []
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        return found_keywords if found_keywords else ["python"]  # 默认关键词
    
    def _execute_step(self, step: Step) -> str:
        """执行单个步骤"""
        if step.tool_name and step.tool_name in self.tools:
            tool = self.tools[step.tool_name]
            
            # 动态调整工具输入（基于之前步骤的结果）
            tool_input = step.tool_input
            if step.tool_name == "file_writer" and "|" in tool_input:
                filename, content_template = tool_input.split('|', 1)
                if "搜索到的信息" in content_template:
                    # 收集之前搜索步骤的结果
                    search_results = []
                    for prev_step in self.plan:
                        if prev_step.completed and prev_step.tool_name == "search":
                            search_results.append(f"{prev_step.description}: {prev_step.result}")
                    
                    if search_results:
                        content = "\n".join(search_results)
                        tool_input = f"{filename}|{content}"
                elif "综合报告内容" in content_template:
                    # 生成综合报告
                    report_content = "=== 综合信息报告 ===\n\n"
                    for prev_step in self.plan:
                        if prev_step.completed and prev_step.result:
                            report_content += f"{prev_step.description}:\n{prev_step.result}\n\n"
                    tool_input = f"{filename}|{report_content}"
            
            result = tool.execute(tool_input)
            step.result = result
            step.completed = True
            return result
        else:
            error_msg = f"未知工具: {step.tool_name}"
            step.result = error_msg
            step.completed = True
            return error_msg
    
    def run(self, question: str) -> str:
        """运行Plan-and-Execute循环"""
        print(f"问题: {question}\n")
        
        # 阶段1: 制定计划
        print("=== 制定执行计划 ===")
        self.plan = self._create_plan(question)
        
        if not self.plan:
            return "无法为此问题制定执行计划"
        
        print("执行计划:")
        for step in self.plan:
            print(f"  {step}")
        print()
        
        # 阶段2: 执行计划
        print("=== 执行计划 ===")
        results = []
        
        for step in self.plan:
            print(f"执行: {step.description}")
            
            if step.tool_name:
                result = self._execute_step(step)
                print(f"结果: {result}")
                results.append(result)
                self.execution_log.append(f"Step {step.step_id}: {step.description} -> {result}")
            else:
                step.completed = True
                print("完成")
            
            print()
        
        # 阶段3: 总结结果
        print("=== 执行总结 ===")
        completed_steps = [step for step in self.plan if step.completed]
        print(f"完成步骤: {len(completed_steps)}/{len(self.plan)}")
        
        if results:
            final_result = results[-1]  # 最后一个结果作为最终答案
            print(f"最终结果: {final_result}")
            return final_result
        else:
            return "执行完成，但没有具体结果"
    
    def get_execution_summary(self) -> str:
        """获取执行摘要"""
        summary = "执行摘要:\n"
        for i, step in enumerate(self.plan, 1):
            status = "✓" if step.completed else "✗"
            summary += f"{status} {step.description}\n"
            if step.result:
                summary += f"   结果: {step.result}\n"
        return summary

def main():
    """演示用法"""
    # 创建工具
    tools = [
        Calculator(),
        Search(),
        FileWriter()
    ]
    
    # 创建Agent
    agent = PlanAndExecuteAgent(tools)
    
    # 测试问题
    questions = [
        "计算 (15 + 27) * 3 的结果",
        "搜索Python的相关信息并写入文件",
        "生成一份包含天气、股票和新闻的综合报告"
    ]
    
    for question in questions:
        print("=" * 60)
        result = agent.run(question)
        print("\n" + agent.get_execution_summary())
        print("=" * 60)
        print()

if __name__ == "__main__":
    main()
