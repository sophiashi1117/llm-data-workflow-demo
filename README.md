# LLM Data Workflow Demo

一个面向校招作品集的 LLM 数据生产 / Prompt Engineering / Agent Workflow 演示项目。

这个项目模拟了真实的大模型数据生产链路：

1. 对原始工单数据进行清洗、去重、结构化预处理
2. 通过 Prompt 模板生成结构化标注结果
3. 使用 Agent/Workflow 思路进行路由、标注、质检和人工复核分流
4. 对标注结果进行离线评测，输出准确率和误差样本

## Why This Project

这个项目专门对齐以下岗位关键词：

- Prompt Engineering
- Agent / Workflow
- LLM 数据生产
- 数据清洗与预处理
- 数据标注 / 质检 / 评测
- Python 工程化与流程自动化

## Project Structure

```text
llm-data-workflow-demo/
├─ data/
│  ├─ raw/tickets.jsonl
│  ├─ processed/tickets.cleaned.jsonl
│  └─ gold/labels.jsonl
├─ outputs/
├─ src/
│  ├─ client.py
│  ├─ evaluate.py
│  ├─ preprocess.py
│  ├─ prompts.py
│  ├─ utils.py
│  └─ workflow.py
├─ run_demo.py
├─ requirements.txt
└─ README.md
```

## Core Workflow

### 1. Data Preprocessing

- 规范化文本格式
- 去除重复样本
- 过滤过短文本
- 保留来源、时间和语言等元信息

### 2. Prompt Engineering

- 设计系统提示词，约束输出为 JSON
- 定义任务标签枚举与 evidence 规则
- 根据长文本和风险样本切换不同 Prompt Version

### 3. Agent / Workflow

- `Router`：为不同样本选择不同的 Prompt 版本
- `Labeler`：生成 intent / severity / needs_human_review 等结构化标签
- `Reviewer`：校验标注结果与 evidence 是否一致
- `Human Review Queue`：将高风险或不确定样本进入人工复核队列

### 4. Offline Evaluation

- 计算 intent accuracy
- 计算 severity accuracy
- 计算 human review flag accuracy
- 计算 exact match
- 输出误差样本，支持继续迭代 Prompt

## Quick Start

使用本地 Mock 模式运行：

```bash
python run_demo.py
```

如果你有 OpenAI-compatible API，也可以配置环境变量后切换到远程模型：

```bash
set OPENAI_API_KEY=your_key
set OPENAI_BASE_URL=https://api.openai.com/v1
set OPENAI_MODEL=gpt-4o-mini
python run_demo.py
```

## Outputs

运行后会生成：

- `outputs/annotations.jsonl`
- `outputs/review_queue.jsonl`
- `outputs/summary.json`
- `outputs/metrics.json`
- `outputs/evaluation_report.md`

## Resume Bullets

你可以基于这个项目，在简历里这样写：

1. 独立完成 LLM 数据生产工作流项目，使用 Python 搭建数据清洗、Prompt 标注、质检复核和离线评测链路，实现从原始数据到结构化标签产出的自动化流程。
2. 设计多版本 Prompt 模板，围绕工单场景完成 intent、severity、人工复核标记等结构化标注，并通过 evidence 约束和 JSON 输出规范提升结果一致性。
3. 按 Agent / Workflow 思路拆分 Router、Labeler、Reviewer 等模块，对高风险和不确定样本自动分流到人工复核队列，提升数据生产效率和可控性。
4. 构建离线评测脚本，对标注结果进行准确率和误差样本分析，支持基于评测结果持续迭代 Prompt 和标注策略。

## GitHub Tips

上传到 GitHub 时，建议仓库名使用：

- `llm-data-workflow-demo`
- `llm-annotation-eval-workflow`
- `prompt-agent-data-pipeline`

建议补充：

- 项目截图
- 运行结果截图
- 你自己的思考总结
- 下一步优化计划

