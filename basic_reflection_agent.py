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
            "新闻": "最新科技新闻：AI技术在各行业应用加速",
            "react": "ReAct是一个结合推理和行动的AI框架",
            "错误信息": "这是一个明显错误的信息：地球是平的"
        }
    
    def execute(self, input_text: str) -> str:
        query = input_text.lower().strip()
        for key, value in self.knowledge.items():
            if key in query:
                return value
        return f"未找到关于'{input_text}'的信息"

class Validator(Tool):
    """验证工具"""
    def __init__(self):
        super().__init__(
            name="validator",
            description="验证信息的准确性，输入要验证的信息"
        )
        # 简单的验证规则
        self.validation_rules = {
            "地球是平的": False,
            "python": True,
            "北京": True,
            "上海": True,
            "天气": True,
            "股票": True
        }
    
    def execute(self, input_text: str) -> str:
        text_lower = input_text.lower()
        
        # 检查明显错误的信息
        if "地球是平的" in text_lower:
            return "验证失败：地球是球形的，不是平的"
        
        # 检查数学计算
        if any(op in input_text for op in ['+', '-', '*', '/', '=']):
            try:
                # 简单验证数学表达式
                if "=" in input_text:
                    parts = input_text.split("=")
                    if len(parts) == 2:
                        left = eval(parts[0].strip())
                        right = float(parts[1].strip())
                        if abs(left - right) < 0.001:
                            return "验证通过：数学计算正确"
                        else:
                            return f"验证失败：{parts[0].strip()} = {left}，不等于 {right}"
            except:
                return "验证失败：无法验证数学表达式"
        
        # 检查其他信息
        for key, is_valid in self.validation_rules.items():
            if key in text_lower:
                if is_valid:
                    return f"验证通过：关于{key}的信息看起来正确"
                else:
                    return f"验证失败：关于{key}的信息不正确"
        
        return "验证通过：信息看起来合理"

class ReflectionStep:
    """反思步骤"""
    def __init__(self, step_id: int, action_type: str, content: str, result: str = None):
        self.step_id = step_id
        self.action_type = action_type  # "action", "reflection", "correction"
        self.content = content
        self.result = result
        self.is_valid = None
    
    def __str__(self):
        type_symbol = {
            "action": "→",
            "reflection": "🤔",
            "correction": "🔧"
        }
        return f"{type_symbol.get(self.action_type, '?')} Step {self.step_id} ({self.action_type}): {self.content}"

class BasicReflectionAgent:
    """基础反思Agent - 执行后反思并纠正错误"""
    
    def __init__(self, tools: List[Tool], max_iterations: int = 5, max_corrections: int = 2):
        self.tools = {tool.name: tool for tool in tools}
        self.max_iterations = max_iterations
        self.max_corrections = max_corrections
        self.reflection_history = []
        self.correction_count = 0
    
    def _get_tool_descriptions(self) -> str:
        """获取工具描述"""
        descriptions = []
        for tool in self.tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)
    
    def _parse_action(self, text: str) -> Optional[tuple]:
        """解析行动指令"""
        pattern = r"Action:\s*(\w+)\[([^\]]*)\]"
        match = re.search(pattern, text)
        if match:
            tool_name = match.group(1)
            tool_input = match.group(2)
            return tool_name, tool_input
        return None
    
    def _should_stop(self, text: str) -> bool:
        """判断是否应该停止"""
        stop_patterns = [
            r"Final Answer:",
            r"最终答案:",
            r"结论:",
            r"答案:"
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in stop_patterns)
    
    def _execute_action(self, tool_name: str, tool_input: str) -> str:
        """执行工具行动"""
        if tool_name in self.tools:
            result = self.tools[tool_name].execute(tool_input)
            return result
        else:
            return f"错误：未知工具 {tool_name}"
    
    def _reflect_on_result(self, action: str, result: str) -> tuple:
        """对结果进行反思"""
        reflection_prompts = {
            "calculator": f"检查计算结果是否合理：{result}",
            "search": f"验证搜索结果的准确性：{result}",
            "validator": f"分析验证结果：{result}"
        }
        
        # 简化的反思逻辑
        issues = []
        
        # 检查明显的错误
        if "错误" in result or "失败" in result:
            issues.append("执行过程中出现错误")
        
        # 检查不合理的结果
        if "地球是平的" in result:
            issues.append("结果包含明显错误的信息")
        
        # 检查数学计算
        if action == "calculator" and not result.replace('.', '').replace('-', '').isdigit():
            if "错误" not in result:
                issues.append("计算结果格式异常")
        
        # 生成反思
        if issues:
            reflection = f"发现问题：{'; '.join(issues)}"
            needs_correction = True
        else:
            reflection = "结果看起来合理"
            needs_correction = False
        
        return reflection, needs_correction
    
    def _generate_correction(self, original_action: str, original_input: str, issue: str) -> tuple:
        """生成纠正行动"""
        if "错误信息" in issue or "地球是平的" in issue:
            # 如果搜索到错误信息，尝试验证
            return "validator", original_input
        
        elif "计算" in issue:
            # 如果计算有问题，重新计算
            return "calculator", original_input
        
        elif "验证失败" in issue:
            # 如果验证失败，尝试搜索更准确的信息
            return "search", original_input
        
        else:
            # 默认：使用验证工具
            return "validator", f"验证：{original_input}"
    
    def _simulate_thinking(self, question: str, iteration: int, context: str) -> str:
        """模拟思考过程"""
        if iteration == 0:
            # 初始思考
            if "计算" in question or any(op in question for op in ['+', '-', '*', '/']):
                math_expr = self._extract_math_expression(question)
                if math_expr:
                    return f"Thought: 这是一个数学问题，我需要计算 {math_expr}\nAction: calculator[{math_expr}]\n"
            
            elif "搜索" in question or "什么是" in question:
                keywords = self._extract_keywords(question)
                if keywords:
                    return f"Thought: 我需要搜索关于{keywords[0]}的信息\nAction: search[{keywords[0]}]\n"
            
            return "Thought: 让我分析这个问题\nAction: search[问题关键词]\n"
        
        else:
            # 基于上下文继续思考
            if "验证失败" in context:
                return "Thought: 之前的信息可能有误，我需要重新搜索\nAction: search[准确信息]\n"
            elif "错误" in context:
                return "Thought: 出现了错误，让我尝试其他方法\nAction: validator[验证信息]\n"
            else:
                return "Final Answer: 基于以上分析和验证，我已经得到了可靠的答案\n"
    
    def _extract_math_expression(self, text: str) -> str:
        """提取数学表达式"""
        pattern = r'[\d+\-*/().\s]+'
        matches = re.findall(pattern, text)
        if matches:
            return max(matches, key=len).strip()
        return ""
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = ["北京", "上海", "python", "天气", "股票", "新闻", "react", "错误信息"]
        found_keywords = []
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        return found_keywords if found_keywords else ["信息"]
    
    def run(self, question: str) -> str:
        """运行反思循环"""
        print(f"问题: {question}\n")
        
        conversation = ""
        self.reflection_history = []
        self.correction_count = 0
        
        for iteration in range(self.max_iterations):
            print(f"=== 迭代 {iteration + 1} ===")
            
            # 生成思考和行动
            thought_and_action = self._simulate_thinking(question, iteration, conversation)
            conversation += thought_and_action
            print(thought_and_action)
            
            # 检查是否应该停止
            if self._should_stop(thought_and_action):
                break
            
            # 解析并执行行动
            action_result = self._parse_action(thought_and_action)
            if action_result:
                tool_name, tool_input = action_result
                
                # 执行行动
                result = self._execute_action(tool_name, tool_input)
                
                # 记录行动步骤
                action_step = ReflectionStep(
                    len(self.reflection_history) + 1,
                    "action",
                    f"{tool_name}[{tool_input}]",
                    result
                )
                self.reflection_history.append(action_step)
                
                observation_text = f"Observation: {result}\n"
                conversation += observation_text
                print(observation_text)
                
                # 反思结果
                print("=== 反思阶段 ===")
                reflection, needs_correction = self._reflect_on_result(tool_name, result)
                
                reflection_step = ReflectionStep(
                    len(self.reflection_history) + 1,
                    "reflection",
                    reflection
                )
                self.reflection_history.append(reflection_step)
                
                print(f"Reflection: {reflection}")
                
                # 如果需要纠正且未超过纠正次数限制
                if needs_correction and self.correction_count < self.max_corrections:
                    print("=== 纠正阶段 ===")
                    correction_tool, correction_input = self._generate_correction(tool_name, tool_input, reflection)
                    
                    correction_result = self._execute_action(correction_tool, correction_input)
                    
                    correction_step = ReflectionStep(
                        len(self.reflection_history) + 1,
                        "correction",
                        f"{correction_tool}[{correction_input}]",
                        correction_result
                    )
                    self.reflection_history.append(correction_step)
                    
                    print(f"Correction: {correction_tool}[{correction_input}] -> {correction_result}")
                    
                    # 更新对话上下文
                    conversation += f"Correction: {correction_result}\n"
                    self.correction_count += 1
                
                print()
        
        return conversation
    
    def get_reflection_summary(self) -> str:
        """获取反思摘要"""
        summary = "反思摘要:\n"
        for step in self.reflection_history:
            summary += f"  {step}\n"
            if step.result:
                summary += f"    结果: {step.result}\n"
        
        summary += f"\n总计: {len([s for s in self.reflection_history if s.action_type == 'action'])} 个行动, "
        summary += f"{len([s for s in self.reflection_history if s.action_type == 'reflection'])} 次反思, "
        summary += f"{len([s for s in self.reflection_history if s.action_type == 'correction'])} 次纠正"
        
        return summary

def main():
    """演示用法"""
    # 创建工具
    tools = [
        Calculator(),
        Search(),
        Validator()
    ]
    
    # 创建Agent
    agent = BasicReflectionAgent(tools)
    
    # 测试问题
    questions = [
        "计算 15 + 27 * 3 的结果",
        "搜索关于错误信息的内容",
        "什么是Python编程语言？"
    ]
    
    for question in questions:
        print("=" * 60)
        result = agent.run(question)
        print(agent.get_reflection_summary())
        print("=" * 60)
        print()

if __name__ == "__main__":
    main()
