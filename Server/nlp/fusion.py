from typing import Dict, List


def _has_conflict(a: Dict, b: Dict) -> bool:
    return not (a["end"] <= b["start"] or b["end"] <= a["start"])


def _longer_first_key(x: Dict):
    return (x["start"], -(x["end"] - x["start"]))


def _priority(source: str) -> int:
    # 우선 순위: Numeric > Text > Presidio
    if source == "NumericRecognizer":
        return 3
    if source == "TextRecognizer":
        return 2
    return 1


def fuse_and_resolve(results_local: List[Dict], results_rules: List[Dict] = None) -> List[Dict]:
    """충돌 해결:
    1) 규칙 기반 결과가 다른 결과에 완전히 포함되면 규칙 결과 제거
    2) 시작 오름차순, 길이 내림차순 정렬
    3) 그리디하게 겹치지 않는 결과 선택
    """
    combined = list(results_local)
    if results_rules:
        combined.extend(results_rules)

    if not combined:
        return []

    # 1) 규칙 기반 결과가 다른 결과에 완전히 포함되면 제거
    indices_to_discard = set()
    for i, a in enumerate(combined):
        if a.get("source") not in ("Presidio", "AccountNumberRecognizer", "CvcRecognizer", "PassportRecognizer", "SSMRecognizer"):
            continue
        for j, b in enumerate(combined):
            if i == j:
                continue
            if b["start"] <= a["start"] and b["end"] >= a["end"]:
                indices_to_discard.add(i)
                break
    filtered = [r for idx, r in enumerate(combined) if idx not in indices_to_discard]

    # 2) 시작 오름차순, 길이 내림차순 정렬
    filtered.sort(key=_longer_first_key)

    # 3) 그리디 선택
    final: List[Dict] = []
    last_end = -1
    for res in filtered:
        if res["start"] >= last_end:
            final.append(res)
            last_end = res["end"]

    return final


