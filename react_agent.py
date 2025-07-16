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
            # 安全的数学表达式求值
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
        # 模拟知识库
        self.knowledge = {
            "北京": "北京是中国的首都，人口约2100万",
            "上海": "上海是中国最大的城市，人口约2400万",
            "python": "Python是一种高级编程语言，广泛用于数据科学和AI",
            "react": "ReAct是一个结合推理和行动的AI框架"
        }
    
    def execute(self, input_text: str) -> str:
        query = input_text.lower().strip()
        for key, value in self.knowledge.items():
            if key in query:
                return value
        return f"未找到关于'{input_text}'的信息"

class ReActAgent:
    """最小化ReAct Agent"""
    
    def __init__(self, tools: List[Tool], max_iterations: int = 10):
        self.tools = {tool.name: tool for tool in tools}
        self.max_iterations = max_iterations
        
    def _get_tool_descriptions(self) -> str:
        """获取工具描述"""
        descriptions = []
        for tool in self.tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)
    
    def _parse_action(self, text: str) -> Optional[tuple]:
        """解析行动指令"""
        # 匹配 Action: tool_name[input] 格式
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
            r"答案:",
            r"结论:",
            r"最终答案:"
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in stop_patterns)
    
    def run(self, question: str) -> str:
        """运行ReAct循环"""
        prompt_template = """你是一个智能助手，可以使用以下工具来回答问题：

{tools}

请按照以下格式思考和行动：

Thought: [你的思考过程]
Action: tool_name[input]
Observation: [工具执行结果]
... (重复思考-行动-观察)
Final Answer: [最终答案]

问题: {question}

让我们开始：
"""
        
        conversation = prompt_template.format(
            tools=self._get_tool_descriptions(),
            question=question
        )
        
        print(f"问题: {question}\n")
        
        for iteration in range(self.max_iterations):
            print(f"=== 迭代 {iteration + 1} ===")
            
            # 模拟思考过程（在实际应用中这里会调用LLM）
            thought_and_action = self._simulate_thinking(conversation, iteration)
            conversation += thought_and_action
            
            print(thought_and_action)
            
            # 检查是否应该停止
            if self._should_stop(thought_and_action):
                break
            
            # 解析行动
            action_result = self._parse_action(thought_and_action)
            if action_result:
                tool_name, tool_input = action_result
                
                # 执行工具
                if tool_name in self.tools:
                    observation = self.tools[tool_name].execute(tool_input)
                    observation_text = f"Observation: {observation}\n\n"
                    conversation += observation_text
                    print(observation_text)
                else:
                    error_text = f"Observation: 错误 - 未知工具: {tool_name}\n\n"
                    conversation += error_text
                    print(error_text)
        
        return conversation
    
    def _simulate_thinking(self, conversation: str, iteration: int) -> str:
        """模拟思考过程（简化版，实际应用中应调用LLM）"""
        # 这里是一个简化的规则基础模拟
        # 在实际应用中，这里应该调用大语言模型
        
        if "计算" in conversation or "数学" in conversation or any(op in conversation for op in ['+', '-', '*', '/', '=']):
            if iteration == 0:
                return "Thought: 这是一个数学问题，我需要使用计算器来解决。\nAction: calculator[2+3*4]\n"
        
        if "搜索" in conversation or "什么是" in conversation or "介绍" in conversation:
            if iteration == 0:
                # 提取搜索关键词
                keywords = ["北京", "上海", "python", "react"]
                for keyword in keywords:
                    if keyword in conversation.lower():
                        return f"Thought: 我需要搜索关于{keyword}的信息。\nAction: search[{keyword}]\n"
                return "Thought: 我需要搜索相关信息。\nAction: search[python]\n"
        
        # 默认情况
        if iteration == 0:
            return "Thought: 让我分析这个问题并使用合适的工具。\nAction: search[问题关键词]\n"
        else:
            return "Final Answer: 基于以上信息，我已经为您提供了答案。\n"

def main():
    """演示用法"""
    # 创建工具
    tools = [
        Calculator(),
        Search()
    ]
    
    # 创建Agent
    agent = ReActAgent(tools)
    
    # 测试问题
    questions = [
        "计算 15 + 27 * 3 的结果",
        "什么是Python？",
        "北京的人口是多少？"
    ]
    
    for question in questions:
        print("=" * 50)
        result = agent.run(question)
        print("=" * 50)
        print()

if __name__ == "__main__":
    main()
