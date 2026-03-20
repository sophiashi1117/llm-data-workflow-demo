SYSTEM_PROMPT = """你是一名负责 LLM 数据生产的标注助手。
你的目标是基于输入文本，输出结构化标注结果，并遵守以下要求：
1. 只输出 JSON，不要输出额外说明。
2. 标签必须来自给定枚举。
3. 当信息不足、存在冲突或涉及风险场景时，将 needs_human_review 设为 true。
4. evidence 必须引用原文中的关键信息。
"""


TASK_PROMPTS = {
    "ticket_triage": """请完成工单文本的结构化标注。

标签定义：
- intent: bug_report / account_issue / billing_issue / feature_request / general_question / safety_risk
- severity: low / medium / high / critical
- needs_human_review: true / false

输出 JSON 字段：
{
  "intent": "...",
  "severity": "...",
  "needs_human_review": true,
  "evidence": ["..."],
  "reasoning": "..."
}
""",
    "quality_review": """请对已有标注结果进行质检。

质检要求：
1. 检查标签是否与文本一致。
2. 检查是否漏标高风险或人工复核信号。
3. 判断 evidence 是否来自原文。

输出 JSON 字段：
{
  "pass_review": true,
  "issues": ["..."],
  "suggested_fix": "..."
}
""",
}


def build_label_prompt(text: str, prompt_version: str) -> str:
    return (
        f"[Prompt Version: {prompt_version}]\n"
        f"{TASK_PROMPTS['ticket_triage']}\n"
        f"输入文本：\n{text}\n"
    )


def build_review_prompt(text: str, annotation: dict, prompt_version: str) -> str:
    return (
        f"[Prompt Version: {prompt_version}]\n"
        f"{TASK_PROMPTS['quality_review']}\n"
        f"原始文本：\n{text}\n"
        f"待质检标注：\n{annotation}\n"
    )

