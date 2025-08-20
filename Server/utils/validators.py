from typing import Any, Dict, Tuple


def require_key(data: Dict[str, Any], key: str) -> Tuple[bool, str]:
    if key not in data:
        return False, f"필수 파라미터 {key}이(가) 누락되었습니다."
    if isinstance(data[key], str) and not data[key].strip():
        return False, f"필수 파라미터 {key}이(가) 누락되었습니다."
    return True, ""


__all__ = ["require_key"]


