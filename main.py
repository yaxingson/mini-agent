import time
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv(override=True)

os.environ['OPENAI_API_KEY'] = os.getenv('DASHSCOPE_API_KEY')
os.environ['OPENAI_BASE_URL'] = os.getenv('DASHSCOPE_BASE_URL')

dirname = os.path.dirname(__file__)

def get_current_time():
  return time.strftime('%H:%M:%S', time.localtime())

def read_file(file_path):
  if not os.path.exists(os.path.join(dirname, file_path)):
    return f'File {file_path} does not exist.'
  try:
    with open(file_path, 'r', encoding='utf-8') as file:
      return file.read()
  except Exception as e:
    return f'Error reading file {file_path}: {e}'

def write_file(file_path, content, append=False):
  try: 
    with open(file_path, 'a' if append else 'w', encoding='utf-8') as file:
      file.write(content)
    return f'File {file_path} written successfully.'
  except Exception as e:
    return f'Error writing file {file_path}: {e}'

def tavily_search(query):
  try:
    client = TavilyClient()
    response = client.search(query, language='zh-CN')
    if response and 'results' in response:
      results = response['results']
      return '\n'.join(result['content'] for result in results)
    else:
      return f'No results found for query: {query}'
  except Exception as e:
    return f'Error during Tavily search: {e}' 

def calculate(a, b, operation):
  try:
    if operation == 'add':
      return a + b
    elif operation == 'subtract':
      return a - b
    elif operation == 'multiply':
      return a * b
    elif operation == 'divide':
      if b != 0:
        return a / b
      else:
        return 'Error: Division by zero'
    else:
      return f'Unknown operation: {operation}'
  except Exception as e:
    return f'Error during calculation: {e}'

tools = [
  {
    'type': 'function',
    'function': {
      'name': 'read_file',
      'description': 'Read the content of a file.',
      'parameters': {
        'type': 'object',
        'properties': {
          'file_path': {
            'type': 'string',
            'description': 'The path to the file to read.'
          }
        },
        'required': ['file_path']
      }
    }
  },
  {
    'type': 'function',
    'function': {
      'name': 'write_file',
      'description': 'Write content to a file.',
      'parameters': {
        'type': 'object',
        'properties': {
          'file_path': {
            'type': 'string',
            'description': 'The path to the file to write.'
          },
          'content': {
            'type': 'string',
            'description': 'The content to write to the file.'
          },
          'append': {
            'type': 'boolean',
            'description': 'Whether to append to the file (default is false).'
          }
        },
        'required': ['file_path', 'content']
      }
    }
  },
  {
    'type': 'function',
    'function': {
      'name': 'tavily_search',
      'description': 'Perform a search using Tavily.',
      'parameters': {
        'type': 'object',
        'properties': {
          'query': {
            'type': 'string',
            'description': 'The search query.'
          }
        },
        'required': ['query']
      }
    },
  },
  {
    'type': 'function',
    'function': {
      'name': 'calculate',
      'description': 'Perform a calculation with two numbers.',
      'parameters': {
        'type': 'object',
        'properties': {
          'a': {
            'type': 'number',
            'description': 'The first number.'
          },
          'b': {
            'type': 'number',
            'description': 'The second number.'
          },
          'operation': {
            'type': 'string',
            'enum': ['add', 'subtract', 'multiply', 'divide'],
            'description': 'The operation to perform.'
          }
        },
        'required': ['a', 'b', 'operation']
      }
    }
  },
  {
    'type': 'function', 
    'function': {
      'name': 'get_current_time',
      'description': 'Get the current time in HH:MM:SS format.',
      'parameters': {
        'type': 'object',
        'properties': {},
        'required': []
      }
    }
  },
]

react_agent_template = '''
你是Devin，一个被设计来协助各种任务的人工智能代理，追求简洁的回答策略，不要涉及法律问题。

工具:
------

您可以使用以下工具：

{tools}

要使用工具，请使用以下格式：

{{
  "action": {{
    "name": "要采取的动作，应该是[{tool_names}]之一。",
    "args": {{
      "参数1": "值1",
      "参数2": "值2"
    }},
  }},
  "thoughts": {{
    "text": "如果需要，描述你的思考过程",
    "reasoning": "如果需要，描述你的推理过程" ,
    "criticism": "如果需要，描述你的批评或反思",
    "plan": "如果需要，描述你的计划",
    "observation": "如果需要，描述你的观察结果"
  }}
}}


当你有话要对人类说，或者如果你不需要使用工具，你必须使用以下格式：

{{
  "action": {{
    "name": "finish",
    "args": {{
      "speak": "你的最终答案"
    }}
  }}
}}

开始吧!

以前的对话记录：
{chat_history}

新输入：{input}

{agent_scratchpad}

确保输出结果是有效的JSON字符串格式，并且可以由python的`json.loads`函数直接解析。
'''

class Devin:
  def __init__(self):
    self.client = OpenAI()
    self.chat_history = []
    self.agent_scratch = ''
    self.available_tools = {
      'get_current_time': get_current_time,
      'read_file': read_file,
      'write_file': write_file,
      'tavily_search': tavily_search,
      'calculate': calculate,
    }

  def generate_prompt(self, query):
    return react_agent_template.format(
      tools=json.dumps([tool['function'] for tool in tools], indent=2, ensure_ascii=False),
      tool_names=', '.join(tool['function']['name'] for tool in tools),
      chat_history='\n'.join(f"{msg['role']}: {msg['content']}" for msg in self.chat_history),
      input=query,
      agent_scratchpad=self.agent_scratch
    )

  def invoke_llm(self, prompt):
    completion = self.client.chat.completions.create(
      model='qwen-plus',
      messages=self.chat_history,
    )
    chat_completion_message = completion.choices[0].message 

    print(chat_completion_message.content)

    response = json.loads(chat_completion_message.content)
    return response
  
  def execute(self, query):
    count = 0

    prompt = self.generate_prompt(query)
    self.chat_history.append({'role':'system', 'content':prompt})

    while count < 7:
      count += 1

      start_time = time.time()
      print(f'[{count}]：开始调用LLM处理...')

      response = self.invoke_llm(prompt)

      end_time = time.time()
      print(f'[{count}]：LLM处理完成，耗时：{end_time - start_time:.2f}秒')

      if not (response and isinstance(response, dict)):
        print(f'[{count}]：LLM处理结果异常，重新尝试...')
        continue
      
      action = response.get('action')
      action_name = action.get('name')
      action_args = action.get('args', {})
      
      if action_name == 'finish':
        answer = action_args.get('speak')
        print(f'Assistant: {answer}')
        self.chat_history.append({'role':'user', 'content':query})
        self.chat_history.append({'role':'assistant', 'content':answer})
        break

      try:
        tool_func = self.available_tools.get(action_name)
        result = tool_func(**action_args) if tool_func else None
        
        self.agent_scratch += f'Action: {action_name}, Args: {action_args}, Result: {result}\n'
        print(f'[{count}]：动作执行成功，结果：{result}')
        
        self.chat_history.append({'role':'user', 'content':query})
        self.chat_history.append({'role':'assistant', 'content': result})
      except Exception as e:
        print(f'[{count}]：执行动作失败，错误：{e}')
        continue

    if count >= 7:
      print('执行任务失败')
    else:
      pass

  def start(self):
    while True:
      user_input = input('User: ')
      if user_input.lower() == 'q':
        print(f'[{get_current_time()}]：Devin AI Agent 关闭...') 
        break
      self.execute(user_input)

if __name__ == '__main__':
  print(f'[{get_current_time()}]：Devin AI Agent 启动...')   
  Devin().start()
