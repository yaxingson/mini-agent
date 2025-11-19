# mini-agent

## 设计模式

### Reflection

```mermaid
flowchart TB
  query --> g["LLM Generate"]
  g --initial output--> r["LLM Reflect"]
  r --reflected output--> g
  g --> output

```

### Tool use

```mermaid
flowchart LR
  query --> LLM
  vs["Vector Datebase"] -.tool calling.-> LLM
  wa["Web APIs"] -.tool calling.-> LLM
  mcp["MCP Tools"] -.tool calling.-> LLM
  LLM --> output


```


### ReAct

```mermaid
flowchart TB
  input[user task] --> thought
  thought --> tool{call tool ?}
  tool --> |Yes|action
  action --> observation
  observation --> thought
  tool --> |No|output[final anwser]

```


### Plan and Execute

```mermaid
sequenceDiagram
  User ->> MainAgent: User task
  MainAgent ->> PlanModel: Please provide the execution plan
  PlanModel ->> ExecAgent: Please proceed with the first step
  ExecAgent ->> MainAgent: Execution completed and return the result
  MainAgent ->> RePlanModel: Please provide a new execution plan or final answer
  RePlanModel ->> MainAgent: Return the execution plan  

```


### Multi Agent



### Reason without Observation



### Workflow

#### Prompt Chain

```mermaid
flowchart LR
  input --> c1["LLM Call1"]
  c1 --Output1--> gate{gate}
  gate --fail--> exit
  gate --pass--> c2["LLM Call2"]
  c2 --Output2--> c3["LLM Call3"]
  c3 --> output

```


#### Routing

```mermaid
flowchart LR
  input --> r["LLM Call Router"]
  r --> c1["LLM Call1"]
  r -.-> c2["LLM Call2"]
  r -.-> c3["LLM Call3"]
  c1 --> output
  c2 -.-> output
  c3 -.-> output
  
```

#### Parallelization

```mermaid
flowchart LR
  input --> c1["LLM Call1"]
  input --> c2["LLM Call2"]
  input --> c3["LLM Call3"]
  c1 --> aggregator
  c2 --> aggregator
  c3 --> aggregator
  aggregator --> output

```


#### Evaluator-optimizer

```mermaid
flowchart LR
  input --> g["LLM Call Generator"]
  g --solution--> e["LLM Call Evaluator"]
  e --rejected & feedback--> g
  e --accpet--> output

```

#### Orchestrator Workers

```mermaid
flowchart LR
  input --> orchestrator
  orchestrator --> c1["LLM Call1"]
  orchestrator --> c2["LLM Call2"]
  orchestrator --> c3["LLM Call3"]
  c1 --> synthesizer
  c2 --> synthesizer
  c3 --> synthesizer
  synthesizer --> ouput
  
```








