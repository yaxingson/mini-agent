import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

class ReasoningModule:
    """推理模块基类"""
    def __init__(self, name: str, description: str, pattern: str, applicable_domains: List[str]):
        self.name = name
        self.description = description
        self.pattern = pattern  # 推理模式的描述
        self.applicable_domains = applicable_domains
    
    def is_applicable(self, task: str, domain: str = "general") -> bool:
        """判断该推理模块是否适用于给定任务"""
        # 简单的关键词匹配
        keywords = self.pattern.lower().split()
        task_lower = task.lower()
        
        # 检查领域匹配
        domain_match = domain in self.applicable_domains or "general" in self.applicable_domains
        
        # 检查关键词匹配
        keyword_match = any(keyword in task_lower for keyword in keywords)
        
        return domain_match and keyword_match
    
    def __str__(self):
        return f"{self.name}: {self.description}"

class ReasoningModuleLibrary:
    """推理模块库"""
    def __init__(self):
        self.modules = self._initialize_modules()
    
    def _initialize_modules(self) -> List[ReasoningModule]:
        """初始化推理模块库"""
        return [
            ReasoningModule(
                name="Critical Thinking",
                description="Break down the problem, question assumptions, evaluate evidence",
                pattern="analyze evaluate question assumption evidence",
                applicable_domains=["general", "analysis", "decision"]
            ),
            ReasoningModule(
                name="Step-by-Step Reasoning",
                description="Solve problems by breaking them into sequential steps",
                pattern="step sequence process procedure method",
                applicable_domains=["general", "math", "problem-solving"]
            ),
            ReasoningModule(
                name="Creative Thinking",
                description="Generate novel ideas and alternative solutions",
                pattern="creative alternative novel brainstorm generate ideas",
                applicable_domains=["general", "creative", "innovation"]
            ),
            ReasoningModule(
                name="Comparative Analysis",
                description="Compare and contrast different options or solutions",
                pattern="compare contrast difference similarity option choice",
                applicable_domains=["general", "analysis", "decision"]
            ),
            ReasoningModule(
                name="Causal Reasoning",
                description="Identify cause-and-effect relationships",
                pattern="cause effect reason result consequence impact",
                applicable_domains=["general", "analysis", "science"]
            ),
            ReasoningModule(
                name="Systems Thinking",
                description="Consider the whole system and interconnections",
                pattern="system holistic interconnection relationship network",
                applicable_domains=["general", "complex", "systems"]
            ),
            ReasoningModule(
                name="Analogical Reasoning",
                description="Use analogies and similar patterns from other domains",
                pattern="analogy similar pattern like metaphor example",
                applicable_domains=["general", "creative", "learning"]
            ),
            ReasoningModule(
                name="Probabilistic Reasoning",
                description="Consider uncertainty and probability in decision making",
                pattern="probability uncertain likely chance risk estimate",
                applicable_domains=["general", "decision", "prediction"]
            )
        ]
    
    def get_all_modules(self) -> List[ReasoningModule]:
        """获取所有推理模块"""
        return self.modules
    
    def find_applicable_modules(self, task: str, domain: str = "general") -> List[ReasoningModule]:
        """找到适用于给定任务的推理模块"""
        return [module for module in self.modules if module.is_applicable(task, domain)]

@dataclass
class ReasoningStructure:
    """推理结构"""
    selected_modules: List[ReasoningModule]
    adapted_structure: Dict[str, Any]
    implementation_plan: List[str]

class SelfDiscoverAgent:
    """Self-Discover模式Agent"""
    
    def __init__(self):
        self.module_library = ReasoningModuleLibrary()
        self.reasoning_structure: Optional[ReasoningStructure] = None
    
    def discover_and_solve(self, task: str, domain: str = "general") -> Dict[str, Any]:
        """Self-Discover的完整流程：选择、适配、实现"""
        print(f"🔍 Starting Self-Discover process for task: {task}")
        print(f"📂 Domain: {domain}\n")
        
        # Stage 1: SELECT - 选择相关的推理模块
        selected_modules = self._select_modules(task, domain)
        
        # Stage 2: ADAPT - 适配推理模块到具体任务
        adapted_structure = self._adapt_modules(selected_modules, task)
        
        # Stage 3: IMPLEMENT - 实现推理结构解决问题
        solution = self._implement_reasoning(adapted_structure, task)
        
        # 保存推理结构
        self.reasoning_structure = ReasoningStructure(
            selected_modules=selected_modules,
            adapted_structure=adapted_structure,
            implementation_plan=solution.get('reasoning_steps', [])
        )
        
        return solution
    
    def _select_modules(self, task: str, domain: str) -> List[ReasoningModule]:
        """Stage 1: SELECT - 选择相关的推理模块"""
        print("🎯 Stage 1: SELECT - Selecting relevant reasoning modules")
        
        # 找到所有适用的模块
        applicable_modules = self.module_library.find_applicable_modules(task, domain)
        
        # 简单的选择策略：选择前3个最相关的模块
        selected_modules = applicable_modules[:3] if len(applicable_modules) >= 3 else applicable_modules
        
        # 如果没有找到适用的模块，选择一些通用模块
        if not selected_modules:
            all_modules = self.module_library.get_all_modules()
            selected_modules = [
                next(m for m in all_modules if m.name == "Critical Thinking"),
                next(m for m in all_modules if m.name == "Step-by-Step Reasoning")
            ]
        
        print("Selected modules:")
        for i, module in enumerate(selected_modules, 1):
            print(f"  {i}. {module}")
        print()
        
        return selected_modules
    
    def _adapt_modules(self, modules: List[ReasoningModule], task: str) -> Dict[str, Any]:
        """Stage 2: ADAPT - 适配推理模块到具体任务"""
        print("🔧 Stage 2: ADAPT - Adapting modules to the specific task")
        
        adapted_structure = {
            'task': task,
            'reasoning_framework': {},
            'execution_order': []
        }
        
        # 为每个选择的模块创建适配的推理框架
        for i, module in enumerate(modules):
            adapted_component = self._adapt_single_module(module, task)
            component_key = f"component_{i+1}_{module.name.lower().replace(' ', '_')}"
            
            adapted_structure['reasoning_framework'][component_key] = adapted_component
            adapted_structure['execution_order'].append(component_key)
        
        print("Adapted reasoning structure:")
        for key, component in adapted_structure['reasoning_framework'].items():
            print(f"  {key}: {component['description']}")
        print()
        
        return adapted_structure
    
    def _adapt_single_module(self, module: ReasoningModule, task: str) -> Dict[str, Any]:
        """适配单个推理模块"""
        adapted_component = {
            'original_module': module.name,
            'description': f"Apply {module.name} to: {task}",
            'specific_actions': []
        }
        
        # 根据模块类型生成具体的行动步骤
        if module.name == "Critical Thinking":
            adapted_component['specific_actions'] = [
                "Identify key assumptions in the task",
                "Question the validity of given information",
                "Evaluate evidence and sources",
                "Consider alternative perspectives"
            ]
        elif module.name == "Step-by-Step Reasoning":
            adapted_component['specific_actions'] = [
                "Break down the task into smaller sub-problems",
                "Identify the logical sequence of steps",
                "Solve each step systematically",
                "Verify each step before proceeding"
            ]
        elif module.name == "Creative Thinking":
            adapted_component['specific_actions'] = [
                "Brainstorm multiple approaches",
                "Think outside conventional boundaries",
                "Generate novel combinations of ideas",
                "Explore unconventional solutions"
            ]
        elif module.name == "Comparative Analysis":
            adapted_component['specific_actions'] = [
                "Identify different options or approaches",
                "List pros and cons of each option",
                "Compare based on relevant criteria",
                "Select the best option with justification"
            ]
        elif module.name == "Causal Reasoning":
            adapted_component['specific_actions'] = [
                "Identify potential causes",
                "Trace cause-and-effect chains",
                "Analyze contributing factors",
                "Predict consequences of actions"
            ]
        else:
            # 通用适配
            adapted_component['specific_actions'] = [
                f"Apply {module.name} principles",
                "Analyze the problem systematically",
                "Generate insights using this approach",
                "Integrate findings with other approaches"
            ]
        
        return adapted_component
    
    def _implement_reasoning(self, adapted_structure: Dict[str, Any], task: str) -> Dict[str, Any]:
        """Stage 3: IMPLEMENT - 实现推理结构解决问题"""
        print("⚡ Stage 3: IMPLEMENT - Implementing reasoning structure")
        
        solution = {
            'task': task,
            'reasoning_steps': [],
            'insights': [],
            'final_answer': None,
            'confidence': 0.0
        }
        
        # 按照执行顺序应用每个推理组件
        for component_key in adapted_structure['execution_order']:
            component = adapted_structure['reasoning_framework'][component_key]
            
            print(f"Executing: {component['original_module']}")
            
            # 执行推理组件
            component_result = self._execute_reasoning_component(component, task)
            
            solution['reasoning_steps'].append({
                'component': component['original_module'],
                'description': component['description'],
                'result': component_result
            })
            
            solution['insights'].extend(component_result.get('insights', []))
        
        # 综合所有推理步骤得出最终答案
        solution['final_answer'] = self._synthesize_final_answer(solution['reasoning_steps'], task)
        solution['confidence'] = self._calculate_confidence(solution['reasoning_steps'])
        
        print(f"Final answer: {solution['final_answer']}")
        print(f"Confidence: {solution['confidence']:.2f}\n")
        
        return solution
    
    def _execute_reasoning_component(self, component: Dict[str, Any], task: str) -> Dict[str, Any]:
        """执行单个推理组件"""
        module_name = component['original_module']
        actions = component['specific_actions']
        
        result = {
            'insights': [],
            'analysis': {},
            'recommendations': []
        }
        
        # 模拟推理过程（在实际实现中，这里会有更复杂的推理逻辑）
        if module_name == "Critical Thinking":
            result['insights'] = [
                "Identified key assumptions that need validation",
                "Found potential biases in the problem statement",
                "Evaluated the reliability of given information"
            ]
            result['analysis']['assumptions'] = ["Assumption 1", "Assumption 2"]
            result['analysis']['evidence_quality'] = "Medium"
            
        elif module_name == "Step-by-Step Reasoning":
            result['insights'] = [
                "Broke down the problem into manageable steps",
                "Identified logical dependencies between steps",
                "Created a systematic approach to solution"
            ]
            result['analysis']['steps'] = ["Step 1", "Step 2", "Step 3"]
            result['analysis']['complexity'] = "Moderate"
            
        elif module_name == "Creative Thinking":
            result['insights'] = [
                "Generated multiple alternative approaches",
                "Identified unconventional solution paths",
                "Explored creative combinations of existing ideas"
            ]
            result['analysis']['alternatives'] = ["Alternative 1", "Alternative 2"]
            result['analysis']['novelty_score'] = 0.7
            
        elif module_name == "Comparative Analysis":
            result['insights'] = [
                "Compared different solution approaches",
                "Identified trade-offs between options",
                "Ranked solutions based on criteria"
            ]
            result['analysis']['options'] = ["Option A", "Option B"]
            result['analysis']['best_option'] = "Option A"
            
        else:
            result['insights'] = [f"Applied {module_name} to analyze the problem"]
            result['analysis']['general_findings'] = "Various insights generated"
        
        return result
    
    def _synthesize_final_answer(self, reasoning_steps: List[Dict[str, Any]], task: str) -> str:
        """综合所有推理步骤得出最终答案"""
        # 收集所有洞察
        all_insights = []
        for step in reasoning_steps:
            all_insights.extend(step['result'].get('insights', []))
        
        # 简单的答案合成（在实际实现中会更复杂）
        if "math" in task.lower() or "calculate" in task.lower():
            return "Based on systematic analysis, the mathematical solution involves breaking down the problem into steps and applying appropriate formulas."
        elif "decision" in task.lower() or "choose" in task.lower():
            return "After comparative analysis and critical evaluation, the recommended decision is based on weighing pros and cons of available options."
        elif "creative" in task.lower() or "design" in task.lower():
            return "Through creative thinking and systematic analysis, multiple innovative approaches have been identified and can be combined for an optimal solution."
        else:
            return f"Based on multi-faceted reasoning analysis, the solution involves integrating insights from {len(reasoning_steps)} different reasoning approaches."
    
    def _calculate_confidence(self, reasoning_steps: List[Dict[str, Any]]) -> float:
        """计算解决方案的置信度"""
        # 简单的置信度计算：基于使用的推理模块数量和质量
        base_confidence = min(0.9, 0.3 + 0.2 * len(reasoning_steps))
        
        # 根据推理质量调整
        quality_bonus = 0.0
        for step in reasoning_steps:
            insights_count = len(step['result'].get('insights', []))
            quality_bonus += min(0.1, insights_count * 0.02)
        
        return min(1.0, base_confidence + quality_bonus)
    
    def get_reasoning_structure(self) -> Optional[ReasoningStructure]:
        """获取当前的推理结构"""
        return self.reasoning_structure
    
    def explain_reasoning(self) -> str:
        """解释推理过程"""
        if not self.reasoning_structure:
            return "No reasoning structure available. Please run discover_and_solve first."
        
        explanation = "🧠 Reasoning Structure Explanation:\n\n"
        
        explanation += "📋 Selected Modules:\n"
        for i, module in enumerate(self.reasoning_structure.selected_modules, 1):
            explanation += f"  {i}. {module.name}: {module.description}\n"
        
        explanation += "\n🔧 Adapted Structure:\n"
        for key, component in self.reasoning_structure.adapted_structure['reasoning_framework'].items():
            explanation += f"  {component['original_module']}: {component['description']}\n"
        
        explanation += "\n⚡ Implementation Plan:\n"
        for i, step in enumerate(self.reasoning_structure.implementation_plan, 1):
            explanation += f"  {i}. {step}\n"
        
        return explanation

# 示例使用和测试
def demo_self_discover():
    """演示Self-Discover Agent"""
    print("=== Self-Discover Agent Demo ===\n")
    
    agent = SelfDiscoverAgent()
    
    # 测试案例1：数学问题
    print("🧮 Test Case 1: Mathematical Problem")
    print("-" * 50)
    task1 = "How to calculate the optimal investment portfolio allocation for maximum return with minimum risk?"
    result1 = agent.discover_and_solve(task1, domain="math")
    
    print("📊 Results:")
    print(f"Task: {result1['task']}")
    print(f"Final Answer: {result1['final_answer']}")
    print(f"Confidence: {result1['confidence']:.2f}")
    print(f"Number of reasoning steps: {len(result1['reasoning_steps'])}")
    print()
    
    # 测试案例2：创意问题
    print("🎨 Test Case 2: Creative Problem")
    print("-" * 50)
    task2 = "Design an innovative solution to reduce urban traffic congestion using creative approaches"
    result2 = agent.discover_and_solve(task2, domain="creative")
    
    print("📊 Results:")
    print(f"Task: {result2['task']}")
    print(f"Final Answer: {result2['final_answer']}")
    print(f"Confidence: {result2['confidence']:.2f}")
    print(f"Number of insights: {len(result2['insights'])}")
    print()
    
    # 测试案例3：决策问题
    print("🤔 Test Case 3: Decision Problem")
    print("-" * 50)
    task3 = "Should a company adopt remote work policy permanently? Analyze the pros and cons."
    result3 = agent.discover_and_solve(task3, domain="decision")
    
    print("📊 Results:")
    print(f"Task: {result3['task']}")
    print(f"Final Answer: {result3['final_answer']}")
    print(f"Confidence: {result3['confidence']:.2f}")
    print()
    
    # 显示推理结构解释
    print("🔍 Reasoning Structure Explanation for Last Task:")
    print("-" * 50)
    print(agent.explain_reasoning())
    
    # 显示推理模块库
    print("📚 Available Reasoning Modules:")
    print("-" * 50)
    modules = agent.module_library.get_all_modules()
    for i, module in enumerate(modules, 1):
        print(f"{i}. {module.name}")
        print(f"   Description: {module.description}")
        print(f"   Domains: {', '.join(module.applicable_domains)}")
        print()

if __name__ == "__main__":
    demo_self_discover()
