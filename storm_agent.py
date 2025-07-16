import time
import threading
from abc import ABC, abstractmethod
from queue import Queue
from typing import Dict, Any, List, Optional

class Agent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, skills: List[str]):
        self.name = name
        self.skills = skills
        self.task_queue = Queue()
        self.is_running = False
        self.thread = None
    
    def start(self):
        """启动Agent"""
        self.is_running = True
        self.thread = threading.Thread(target=self._work_loop)
        self.thread.start()
        print(f"Agent {self.name} started")
    
    def stop(self):
        """停止Agent"""
        self.is_running = False
        if self.thread:
            self.thread.join()
    
    def _work_loop(self):
        """工作循环"""
        while self.is_running:
            try:
                task = self.task_queue.get(timeout=0.1)
                result = self.process(task['data'])
                if task['callback']:
                    task['callback'](result)
            except:
                continue
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """处理任务的抽象方法"""
        pass
    
    def can_handle(self, skill: str) -> bool:
        """检查是否能处理某种技能"""
        return skill in self.skills

class DataAgent(Agent):
    """数据处理Agent"""
    
    def __init__(self):
        super().__init__("DataAgent", ["analyze", "filter", "transform"])
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理数据任务"""
        task_type = data.get('type')
        values = data.get('values', [])
        
        if task_type == 'analyze':
            return {
                'count': len(values),
                'sum': sum(values) if values else 0,
                'avg': sum(values) / len(values) if values else 0
            }
        
        elif task_type == 'filter':
            threshold = data.get('threshold', 0)
            filtered = [x for x in values if x > threshold]
            return {'filtered': filtered, 'count': len(filtered)}
        
        elif task_type == 'transform':
            multiplier = data.get('multiplier', 2)
            transformed = [x * multiplier for x in values]
            return {'transformed': transformed}
        
        return {'error': 'Unknown task type'}

class MathAgent(Agent):
    """数学计算Agent"""
    
    def __init__(self):
        super().__init__("MathAgent", ["calculate", "fibonacci", "prime"])
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理数学任务"""
        task_type = data.get('type')
        
        if task_type == 'fibonacci':
            n = data.get('n', 10)
            fib = self._fibonacci(n)
            return {'fibonacci': fib, 'length': len(fib)}
        
        elif task_type == 'prime':
            num = data.get('number', 2)
            is_prime = self._is_prime(num)
            return {'number': num, 'is_prime': is_prime}
        
        elif task_type == 'calculate':
            a = data.get('a', 0)
            b = data.get('b', 0)
            op = data.get('operation', 'add')
            
            if op == 'add':
                result = a + b
            elif op == 'multiply':
                result = a * b
            elif op == 'power':
                result = a ** b
            else:
                result = 0
            
            return {'result': result, 'operation': f"{a} {op} {b}"}
        
        return {'error': 'Unknown task type'}
    
    def _fibonacci(self, n: int) -> List[int]:
        """生成斐波那契数列"""
        if n <= 0:
            return []
        elif n == 1:
            return [0]
        
        fib = [0, 1]
        for i in range(2, n):
            fib.append(fib[i-1] + fib[i-2])
        return fib
    
    def _is_prime(self, num: int) -> bool:
        """检查是否为质数"""
        if num < 2:
            return False
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                return False
        return True

class StormCoordinator:
    """Storm协调器 - 最小化实现"""
    
    def __init__(self):
        self.agents: List[Agent] = []
        self.results: List[Any] = []
    
    def add_agent(self, agent: Agent):
        """添加Agent"""
        self.agents.append(agent)
        print(f"Added {agent.name} with skills: {agent.skills}")
    
    def start_all(self):
        """启动所有Agent"""
        for agent in self.agents:
            agent.start()
        print("All agents started")
    
    def stop_all(self):
        """停止所有Agent"""
        for agent in self.agents:
            agent.stop()
        print("All agents stopped")
    
    def submit_task(self, skill: str, data: Dict[str, Any]) -> bool:
        """提交任务"""
        # 找到能处理该技能的Agent
        suitable_agent = self._find_agent(skill)
        
        if suitable_agent:
            # 创建回调函数来收集结果
            def callback(result):
                self.results.append({
                    'agent': suitable_agent.name,
                    'skill': skill,
                    'result': result,
                    'timestamp': time.time()
                })
                print(f"Task completed by {suitable_agent.name}: {result}")
            
            # 提交任务
            task = {'data': data, 'callback': callback}
            suitable_agent.task_queue.put(task)
            print(f"Task submitted to {suitable_agent.name}")
            return True
        
        print(f"No agent found for skill: {skill}")
        return False
    
    def _find_agent(self, skill: str) -> Optional[Agent]:
        """找到能处理指定技能的Agent"""
        for agent in self.agents:
            if agent.can_handle(skill):
                return agent
        return None
    
    def get_results(self) -> List[Dict[str, Any]]:
        """获取所有结果"""
        return self.results.copy()
    
    def clear_results(self):
        """清空结果"""
        self.results.clear()

def demo():
    """演示Storm系统"""
    print("=== Minimal Storm Agent Demo ===\n")
    
    # 创建协调器
    coordinator = StormCoordinator()
    
    # 创建Agent
    data_agent = DataAgent()
    math_agent = MathAgent()
    
    # 添加Agent到协调器
    coordinator.add_agent(data_agent)
    coordinator.add_agent(math_agent)
    
    # 启动所有Agent
    coordinator.start_all()
    
    print("\n--- Submitting Tasks ---")
    
    # 提交数据分析任务
    coordinator.submit_task('analyze', {
        'type': 'analyze',
        'values': [1, 2, 3, 4, 5, 10, 15, 20]
    })
    
    # 提交斐波那契计算任务
    coordinator.submit_task('fibonacci', {
        'type': 'fibonacci',
        'n': 8
    })
    
    # 提交数据过滤任务
    coordinator.submit_task('filter', {
        'type': 'filter',
        'values': [1, 5, 10, 15, 20, 25],
        'threshold': 10
    })
    
    # 提交质数检查任务
    coordinator.submit_task('prime', {
        'type': 'prime',
        'number': 17
    })
    
    # 提交数学计算任务
    coordinator.submit_task('calculate', {
        'type': 'calculate',
        'a': 5,
        'b': 3,
        'operation': 'power'
    })
    
    # 提交数据转换任务
    coordinator.submit_task('transform', {
        'type': 'transform',
        'values': [1, 2, 3, 4, 5],
        'multiplier': 3
    })
    
    # 等待任务完成
    print("\nWaiting for tasks to complete...")
    time.sleep(2)
    
    # 显示结果
    print("\n--- Results ---")
    results = coordinator.get_results()
    for i, result in enumerate(results, 1):
        print(f"{i}. Agent: {result['agent']}")
        print(f"   Skill: {result['skill']}")
        print(f"   Result: {result['result']}")
        print(f"   Time: {time.ctime(result['timestamp'])}")
        print()
    
    print(f"Total completed tasks: {len(results)}")
    
    # 停止所有Agent
    coordinator.stop_all()
    print("Demo completed!")

if __name__ == "__main__":
    demo()
