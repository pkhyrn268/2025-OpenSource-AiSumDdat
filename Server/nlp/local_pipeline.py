from typing import Dict, List

from functools import lru_cache
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

# 실행 환경에 따라 임포트 경로가 달라질 수 있어 두 경로를 지원합니다.
try:
    from ..config import TEXT_MODEL_PATH, NUMERIC_MODEL_PATH, get_device  # type: ignore
except Exception:  # pragma: no cover
    from backend.config import TEXT_MODEL_PATH, NUMERIC_MODEL_PATH, get_device  # type: ignore


# 일반 텍스트에서 개체를 찾는 파이프라인을 준비합니다.
# 한 번 만든 뒤 캐시에 보관해 재사용합니다.
@lru_cache(maxsize=1)
def _get_text_pipe():
    return pipeline(
        "ner",
        model=AutoModelForTokenClassification.from_pretrained(TEXT_MODEL_PATH),
        tokenizer=AutoTokenizer.from_pretrained(TEXT_MODEL_PATH),
        aggregation_strategy="simple",
        device=get_device(),
    )


# 숫자·식별자 같은 패턴 위주의 개체를 찾는 파이프라인을 준비합니다.
# 한 번 만든 뒤 캐시에 보관해 재사용합니다.
@lru_cache(maxsize=1)
def _get_numeric_pipe():
    return pipeline(
        "ner",
        model=AutoModelForTokenClassification.from_pretrained(NUMERIC_MODEL_PATH),
        tokenizer=AutoTokenizer.from_pretrained(NUMERIC_MODEL_PATH),
        aggregation_strategy="simple",
        device=get_device(),
    )


# 모델 출력 목록을 공통 딕셔너리 형식으로 바꿉니다.
# entity_type/start/end/score/source 키를 사용합니다.
def _convert(pipeline_outputs, recognizer_name: str) -> List[Dict]:
    results: List[Dict] = []
    for ent in pipeline_outputs:
        results.append(
            {
                "entity_type": ent.get("entity_group"),
                "start": int(ent.get("start")),
                "end": int(ent.get("end")),
                "score": float(ent.get("score", 0.0)),
                "source": recognizer_name,
            }
        )
    return results


# 텍스트용과 숫자용 모델을 모두 실행하고 결과를 하나로 합칩니다.
def run_dual_pipelines(text: str) -> List[Dict]:
    text_out = _get_text_pipe()(text)
    num_out = _get_numeric_pipe()(text)
    return _convert(text_out, "TextRecognizer") + _convert(num_out, "NumericRecognizer")


# 숫자/식별자 전용 모델만 실행합니다.
def run_numeric_pipeline(text: str) -> List[Dict]:
    """숫자/식별자 전용 모델만 실행합니다."""
    num_out = _get_numeric_pipe()(text)
    return _convert(num_out, "NumericRecognizer")


