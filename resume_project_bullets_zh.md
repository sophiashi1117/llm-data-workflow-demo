# 可直接放简历的项目描述

## 版本一：适合校招简历

**LLM 数据生产与标注评测工作流项目**  
个人项目

- 使用 Python 搭建 LLM 数据生产工作流，完成原始工单数据清洗、去重、结构化预处理，以及标注结果导出等流程自动化。
- 结合 Prompt Engineering 设计多版本提示词模板，对文本进行 intent、severity、needs_human_review 等结构化标注，并约束输出为标准 JSON。
- 按 Agent / Workflow 思路拆分 Router、Labeler、Reviewer 模块，实现样本路由、结果质检和人工复核分流，提升数据标注流程的稳定性与可控性。
- 构建离线评测脚本，对标注结果进行准确率统计和误差样本分析，支持基于评测结果迭代 Prompt 与标注策略。

## 版本二：更贴近岗位 JD

**Prompt Engineering 与 Agent 数据工作流项目**  
个人项目

- 深入理解 LLM 数据生产链路，围绕业务工单场景设计 Prompt 模板和结构化标签体系，产出可用于标注、质检与评测的高质量数据样本。
- 通过 Python 完成数据清洗、预处理、数据分析、链路搭建与结果导出，形成从原始文本到结构化标签的端到端流程。
- 采用 Agent / Workflow 思路完成路由、标注、质检、人工复核等模块拆分，并基于不同样本类型切换 Prompt 版本，提升复杂样本处理能力。
- 结合离线评测结果分析错误样本，迭代 Prompt 和质检规则，优化数据标准与标注策略。

## 版本三：更适合 GitHub + 简历联动

**LLM Annotation & Evaluation Workflow**  
GitHub 个人项目

- Built an end-to-end LLM data workflow for preprocessing, prompt-based annotation, review routing, and offline evaluation.
- Designed prompt templates for structured JSON output and labeled support-ticket data with intent, severity, and human-review flags.
- Implemented agent-style modules including Router, Labeler, and Reviewer to improve annotation consistency and send uncertain cases to a review queue.
- Added evaluation scripts to compare predictions against gold labels and analyze error samples for prompt iteration.

