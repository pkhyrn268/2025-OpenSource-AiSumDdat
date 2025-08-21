from typing import Dict


TEMPLATE_KEYS = {
    "question1": "답변1",
    "question2": "답변2",
    "question3": "답변3",
    "question4": "답변4",
    "question5": "답변5",
    "question6": "답변6",
}


def _get(d: Dict, k: str) -> str:
    v = d.get(k)
    return v if isinstance(v, str) else ""


def build_prompt(data: Dict) -> str:
    q1 = _get(data, "question1")
    q2 = _get(data, "question2")
    q3 = _get(data, "question3")
    q4 = _get(data, "question4")
    q5 = _get(data, "question5")
    q6 = _get(data, "question6")

    # 명세의 출력 템플릿에 맞춰 직렬화
    lines = []
    if q1:
        lines.append(f"[{q1}] 작업을 시키고 싶습니다.")
    if q2:
        lines.append(f"[{q2}]")
    if q3:
        lines.append(f"답변은 [{q3}] 형식으로,")
    if q4:
        lines.append(f"답변의 수준은 [{q4}] 수준으로 해주세요.")
    if q5:
        lines.append(f"답변의 길이는 [{q5}] 받고 싶습니다.")
    if q6:
        lines.append(f"참고 자료: [{q6}]")

    return "\n".join(lines)


