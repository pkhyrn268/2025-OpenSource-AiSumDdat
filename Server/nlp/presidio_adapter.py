from functools import lru_cache
from typing import Dict, List

# Presidio를 사용할 수 있으면 엔진을 쓰고,
# 없으면 간단한 정규식 인식기로 대체합니다.
# 한 번 만든 객체는 캐시에 보관해 재사용합니다.

try:
    from presidio_analyzer import (  # type: ignore
        AnalyzerEngine,
        Pattern,
        PatternRecognizer,
    )  # type: ignore
except Exception:  # pragma: no cover
    AnalyzerEngine = None  # type: ignore


# Presidio 분석 엔진을 준비합니다. (없으면 None 반환)
# 첫 생성 후 캐시에 저장되어 재사용됩니다.
@lru_cache(maxsize=1)
def _get_engine():  # type: ignore
    if AnalyzerEngine is None:
        return None
    try:
        engine = AnalyzerEngine(supported_languages=["en", "ko", "kr"])  # type: ignore
        return engine
    except Exception:
        return None


# 정규식 기반 인식기들을 한 번 만들어 재사용합니다.
@lru_cache(maxsize=1)
def _get_rule_recognizers():
    """패턴 기반 인식기 세트."""
    try:
        account_recognizer = PatternRecognizer(
            supported_entity="AN",
            name="AccountNumberRecognizer",
            patterns=[Pattern(name="계좌번호 패턴", regex=r"\b\d{2,6}[-]\d{2,6}[-]\d{2,6}\b", score=1.0)],
        )
        cvc_recognizer = PatternRecognizer(
            supported_entity="CVC",
            name="CvcRecognizer",
            patterns=[Pattern(name="CVC 패턴", regex=r"\b\d{3}\b", score=0.9)],
        )
        passport_recognizer = PatternRecognizer(
            supported_entity="PPS",
            name="PassportRecognizer",
            patterns=[Pattern(name="여권번호 패턴", regex=r"\b[A-Za-z]\d{8}\b", score=1.0)],
        )
        ssn_recognizer = PatternRecognizer(
            supported_entity="SSN",
            name="SSMRecognizer",
            patterns=[Pattern(name="주민번호 패턴", regex=r"\b\d{6}[-]\d{7}\b", score=1.0)],
        )
        return [account_recognizer, cvc_recognizer, passport_recognizer, ssn_recognizer]
    except Exception:
        return []


def analyze_with_presidio(text: str) -> List[Dict]:
    """룰 기반 탐지.

    Presidio 엔진이 있으면 다국어 분석을 수행하고,
    항상 커스텀 정규식 인식기 결과도 함께 사용합니다.
    최종 결과는 공통 딕셔너리 형식으로 바꿔 반환합니다.
    """
    engine = _get_engine()
    if engine is None:
        rule_recognizers = _get_rule_recognizers()
        all_results = []
        for recognizer in rule_recognizers:
            try:
                all_results.extend(recognizer.analyze(text=text, entities=recognizer.supported_entities))
            except Exception:
                continue
    else:
        try:
            results_en = engine.analyze(text=text, language="en")
        except Exception:
            results_en = []
        try:
            results_ko = engine.analyze(text=text, language="ko", entities=["KR_RRN"])  # type: ignore
        except Exception:
            try:
                results_ko = engine.analyze(text=text, language="kr", entities=["KR_RRN"])  # type: ignore
            except Exception:
                results_ko = []
        all_results = list(results_en) + list(results_ko)

        # 정규식도 추가 병행
        for recognizer in _get_rule_recognizers():
            try:
                all_results.extend(recognizer.analyze(text=text, entities=recognizer.supported_entities))
            except Exception:
                continue

    converted: List[Dict] = []
    for r in all_results:
        try:
            converted.append(
                {
                    "entity_type": getattr(r, "entity_type", None) or getattr(r, "supported_entity", ""),
                    "start": int(r.start),
                    "end": int(r.end),
                    "score": float(getattr(r, "score", 1.0)),
                    "source": getattr(getattr(r, "analysis_explanation", None), "recognizer", "Presidio"),
                }
            )
        except Exception:
            continue
    return converted


