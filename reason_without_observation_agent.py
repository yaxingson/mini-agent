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
            "react": "ReAct是一个结合推理和行动的AI框架"
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

class ReasoningStep:
    """推理步骤"""
    def __init__(self, step_id: int, reasoning: str, action: str = None, tool_input: str = None):
        self.step_id = step_id
        self.reasoning = reasoning
        self.action = action
        self.tool_input = tool_input
        self.predicted_result = None
    
    def __str__(self):
        return f"Step {self.step_id}: {self.reasoning}"

class ReasonWithoutObservationAgent:
    """Reason Without Observation Agent - 先完整推理再执行"""
    
    def __init__(self, tools: List[Tool], max_reasoning_steps: int = 5):
        self.tools = {tool.name: tool for tool in tools}
        self.max_reasoning_steps = max_reasoning_steps
        self.reasoning_chain = []
        self.execution_results = []
    
    def _get_tool_descriptions(self) -> str:
        """获取工具描述"""
        descriptions = []
        for tool in self.tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)
    
    def _generate_reasoning_chain(self, question: str) -> List[ReasoningStep]:
        """生成完整的推理链（不执行工具）"""
        reasoning_chain = []
        step_id = 1
        
        # 分析问题并生成推理步骤
        question_lower = question.lower()
        
        if "计算" in question_lower or any(op in question for op in ['+', '-', '*', '/', '=']):
            # 数学推理链
            math_expr = self._extract_math_expression(question)
            if math_expr:
                reasoning_chain.append(ReasoningStep(
                    step_id, 
                    f"这是一个数学计算问题，需要计算表达式: {math_expr}",
                    "calculator",
                    math_expr
                ))
                step_id += 1
                
                # 预测结果
                try:
                    predicted = eval(math_expr)
                    reasoning_chain[-1].predicted_result = f"预期结果约为: {predicted}"
                except:
                    reasoning_chain[-1].predicted_result = "预期得到数值结果"
                
                reasoning_chain.append(ReasoningStep(
                    step_id,
                    f"计算完成后，我将得到 {math_expr} 的准确数值结果"
                ))
        
        elif "搜索" in question_lower or "什么是" in question_lower or "介绍" in question_lower:
            # 搜索推理链
            keywords = self._extract_keywords(question)
            for keyword in keywords:
                reasoning_chain.append(ReasoningStep(
                    step_id,
                    f"需要搜索关于'{keyword}'的信息来回答问题",
                    "search",
                    keyword
                ))
                reasoning_chain[-1].predicted_result = f"预期获得{keyword}的详细信息"
                step_id += 1
            
            reasoning_chain.append(ReasoningStep(
                step_id,
                "基于搜索结果，我将能够提供准确的答案"
            ))
        
        elif "写入" in question_lower or "保存" in question_lower or "文件" in question_lower:
            # 文件操作推理链
            reasoning_chain.append(ReasoningStep(
                step_id,
                "首先需要获取要写入的内容信息",
                "search",
                "python"
            ))
            reasoning_chain[-1].predicted_result = "获得相关信息内容"
            step_id += 1
            
            reasoning_chain.append(ReasoningStep(
                step_id,
                "然后将获得的信息写入指定文件",
                "file_writer",
                "output.txt|获得的信息内容"
            ))
            reasoning_chain[-1].predicted_result = "成功创建文件"
            step_id += 1
            
            reasoning_chain.append(ReasoningStep(
                step_id,
                "文件创建完成，任务执行成功"
            ))
        
        elif "比较" in question_lower or "分析" in question_lower:
            # 比较分析推理链
            topics = self._extract_keywords(question)
            if len(topics) >= 2:
                for topic in topics[:2]:  # 最多比较两个主题
                    reasoning_chain.append(ReasoningStep(
                        step_id,
                        f"搜索{topic}的信息用于比较分析",
                        "search",
                        topic
                    ))
                    reasoning_chain[-1].predicted_result = f"获得{topic}的详细信息"
                    step_id += 1
                
                reasoning_chain.append(ReasoningStep(
                    step_id,
                    f"基于收集的信息，我将能够进行{topics[0]}和{topics[1]}的比较分析"
                ))
        
        else:
            # 默认推理链
            reasoning_chain.append(ReasoningStep(
                step_id,
                "分析问题，确定需要搜索相关信息",
                "search",
                question[:20]  # 使用问题前20个字符作为搜索词
            ))
            reasoning_chain[-1].predicted_result = "获得相关信息"
            step_id += 1
            
            reasoning_chain.append(ReasoningStep(
                step_id,
                "基于搜索结果提供答案"
            ))
        
        return reasoning_chain
    
    def _extract_math_expression(self, text: str) -> str:
        """提取数学表达式"""
        pattern = r'[\d+\-*/().\s]+'
        matches = re.findall(pattern, text)
        if matches:
            return max(matches, key=len).strip()
        return ""
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = ["北京", "上海", "python", "天气", "股票", "新闻", "react"]
        found_keywords = []
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        return found_keywords if found_keywords else ["信息"]
    
    def _execute_reasoning_chain(self) -> List[str]:
        """执行推理链中的所有行动"""
        results = []
        collected_info = {}
        
        for step in self.reasoning_chain:
            if step.action and step.action in self.tools:
                tool = self.tools[step.action]
                
                # 动态调整工具输入
                tool_input = step.tool_input
                if step.action == "file_writer" and "|" in tool_input:
                    filename, content_template = tool_input.split('|', 1)
                    if "获得的信息内容" in content_template:
                        # 使用之前收集的信息
                        content = "\n".join(collected_info.values()) if collected_info else "默认内容"
                        tool_input = f"{filename}|{content}"
                
                result = tool.execute(tool_input)
                results.append(result)
                
                # 收集信息用于后续步骤
                if step.action == "search":
                    collected_info[step.tool_input] = result
                
                print(f"执行 {step.action}[{tool_input}] -> {result}")
        
        return results
    
    def run(self, question: str) -> str:
        """运行Reason Without Observation循环"""
        print(f"问题: {question}\n")
        
        # 阶段1: 完整推理（不执行工具）
        print("=== 推理阶段 ===")
        self.reasoning_chain = self._generate_reasoning_chain(question)
        
        print("推理链:")
        for step in self.reasoning_chain:
            print(f"  {step}")
            if step.predicted_result:
                print(f"    预期: {step.predicted_result}")
            if step.action:
                print(f"    行动: {step.action}[{step.tool_input}]")
        print()
        
        # 阶段2: 执行所有行动
        print("=== 执行阶段 ===")
        self.execution_results = self._execute_reasoning_chain()
        print()
        
        # 阶段3: 生成最终答案
        print("=== 结果阶段 ===")
        if self.execution_results:
            final_answer = self._generate_final_answer(question, self.execution_results)
            print(f"最终答案: {final_answer}")
            return final_answer
        else:
            final_answer = "基于推理分析，已完成问题处理"
            print(f"最终答案: {final_answer}")
            return final_answer
    
    def _generate_final_answer(self, question: str, results: List[str]) -> str:
        """基于执行结果生成最终答案"""
        if not results:
            return "推理完成，但没有执行结果"
        
        # 根据问题类型生成不同的答案格式
        question_lower = question.lower()
        
        if "计算" in question_lower:
            # 数学计算结果
            for result in results:
                if result.replace('.', '').replace('-', '').isdigit():
                    return f"计算结果是: {result}"
            return f"计算完成: {results[-1]}"
        
        elif "什么是" in question_lower or "介绍" in question_lower:
            # 信息查询结果
            return f"根据搜索结果: {results[0]}"
        
        elif "文件" in question_lower:
            # 文件操作结果
            return f"操作完成: {results[-1]}"
        
        elif "比较" in question_lower:
            # 比较分析结果
            if len(results) >= 2:
                return f"比较结果 - 信息1: {results[0]}; 信息2: {results[1]}"
        
        # 默认返回最后一个结果
        return results[-1]
    
    def get_reasoning_summary(self) -> str:
        """获取推理摘要"""
        summary = "推理摘要:\n"
        for step in self.reasoning_chain:
            summary += f"- {step.reasoning}\n"
            if step.predicted_result:
                summary += f"  预期: {step.predicted_result}\n"
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
    agent = ReasonWithoutObservationAgent(tools)
    
    # 测试问题
    questions = [
        "计算 (25 + 15) * 2 的结果",
        "什么是Python编程语言？",
        "搜索Python信息并保存到文件",
        "比较北京和上海的信息"
    ]
    
    for question in questions:
        print("=" * 60)
        result = agent.run(question)
        print("\n" + agent.get_reasoning_summary())
        print("=" * 60)
        print()

if __name__ == "__main__":
    main()
