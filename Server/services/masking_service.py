from typing import List, Tuple, Dict

try:
    from ..nlp.fusion import fuse_and_resolve
    from ..nlp.label_mapping import to_standard_label, to_display_label
    from ..config import DEFAULT_LOCALE
except Exception:  # pragma: no cover
    from backend.nlp.fusion import fuse_and_resolve  # type: ignore
    from backend.nlp.label_mapping import to_standard_label, to_display_label  # type: ignore
    from backend.config import DEFAULT_LOCALE  # type: ignore


def _mask_from_results(text: str, results: List[Dict]) -> Tuple[str, List[Dict]]:
    # 뒤에서 앞으로 치환
    masked = text
    masked_entities: List[Dict] = []
    for r in sorted(results, key=lambda x: x["start"], reverse=True):
        entity_text = text[r["start"] : r["end"]]
        code = to_standard_label(r["entity_type"]) or r["entity_type"]
        display = to_display_label(code, locale=DEFAULT_LOCALE)
        masked = masked[: r["start"]] + f"[{display}]" + masked[r["end"] :]
        masked_entities.append({"entity": entity_text, "label": display})

    # 중복 제거(첫 등장 우선)
    seen = set()
    uniq_entities: List[Dict] = []
    for item in masked_entities:
        key = (item["entity"], item["label"])
        if key in seen:
            continue
        seen.add(key)
        uniq_entities.append(item)

    return masked, uniq_entities


def mask_text_with_models(text: str) -> Tuple[str, List[Dict]]:
    # 지연 임포트: 필요할 때만 무거운 모듈 로드
    try:
        from ..nlp.local_pipeline import run_numeric_pipeline  # type: ignore
        from ..nlp.presidio_adapter import analyze_with_presidio  # type: ignore
        from ..config import DISABLE_LOCAL_NER, DISABLE_PRESIDIO  # type: ignore
    except Exception:
        from backend.nlp.local_pipeline import run_numeric_pipeline  # type: ignore
        from backend.nlp.presidio_adapter import analyze_with_presidio  # type: ignore
        from backend.config import DISABLE_LOCAL_NER, DISABLE_PRESIDIO  # type: ignore

    # 스크립트 방식: 숫자/식별자 전용 NER만 실행
    local_results = [] if DISABLE_LOCAL_NER else run_numeric_pipeline(text)
    # Presidio 규칙 결과
    presidio_results = [] if DISABLE_PRESIDIO else analyze_with_presidio(text)

    # 병합/정렬/충돌해결
    merged_results = fuse_and_resolve(local_results, presidio_results)

    # 마스킹 및 엔티티 목록 생성
    return _mask_from_results(text, merged_results)


