from __future__ import annotations

import json
import os
from urllib import request


class LLMClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def use_remote(self) -> bool:
        return bool(self.api_key)

    def chat_json(self, system_prompt: str, user_prompt: str) -> dict:
        if not self.use_remote:
            raise RuntimeError("Remote LLM is not configured.")

        payload = {
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        req = request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        with request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"]
        return json.loads(content)


def mock_label(text: str) -> dict:
    lower_text = text.lower()
    evidence = []
    needs_review = False

    if any(word in lower_text for word in ["扣费", "退款", "账单", "支付", "续费", "对不上"]):
        intent = "billing_issue"
        severity = "high"
    elif any(word in lower_text for word in ["崩溃", "闪退", "bug", "报错", "错误码"]):
        intent = "bug_report"
        severity = "high" if any(word in lower_text for word in ["无法", "崩溃", "无法登录", "没法使用", "无法使用"]) else "medium"
    elif any(word in lower_text for word in ["登录", "账号", "密码", "验证码"]):
        intent = "account_issue"
        severity = "high" if "无法" in lower_text else "medium"
    elif any(word in lower_text for word in ["希望增加", "建议增加", "能不能支持", "功能"]):
        intent = "feature_request"
        severity = "low"
    elif any(word in lower_text for word in ["自杀", "伤害", "违法", "隐私泄露", "泄露"]):
        intent = "safety_risk"
        severity = "critical"
        needs_review = True
    else:
        intent = "general_question"
        severity = "low"

    for clue in ["崩溃", "无法登录", "退款", "扣费", "希望增加", "隐私泄露", "验证码"]:
        if clue in text:
            evidence.append(clue)

    if not evidence:
        evidence.append(text[:18])

    if len(text) > 70 or "但是" in text or "不过" in text:
        needs_review = True

    return {
        "intent": intent,
        "severity": severity,
        "needs_human_review": needs_review,
        "evidence": evidence[:3],
        "reasoning": "Mock label generated from keyword and risk heuristics.",
    }


def mock_review(text: str, annotation: dict) -> dict:
    issues = []
    evidence = annotation.get("evidence", [])

    for item in evidence:
        if item and item not in text:
            issues.append(f"Evidence not found in text: {item}")

    if annotation.get("intent") == "general_question" and annotation.get("severity") in {"high", "critical"}:
        issues.append("General questions usually should not have high severity.")

    if annotation.get("intent") == "safety_risk" and not annotation.get("needs_human_review"):
        issues.append("Safety risk should require human review.")

    return {
        "pass_review": not issues,
        "issues": issues,
        "suggested_fix": "Set needs_human_review=true or adjust labels." if issues else "",
    }
