"""Flask 기반 마스킹 API 서버 모듈.

- `/health`: 서버 상태 확인용 헬스 체크 엔드포인트
- `/api/masking`: 프롬프트와 (선택) PDF를 받아 개인정보/민감정보를 마스킹

요청 방식 요약:
- multipart/form-data: `prompt_json`(문자열), `pdf_file`(선택)
- application/json: {"prompt_json": {...}} 또는 질문 키(question1, ...)를 직접 포함한 객체
"""

import io
import json
import logging
from typing import Any, Dict, Tuple

from flask import Flask, request

# 패키지 실행과 단일 스크립트 실행을 모두 지원하기 위한 이중 import 처리
try:  # package-relative import
    from .config import LOG_LEVEL, APP_PORT, APP_VERSION
    from .utils.responses import success, error
except Exception:  # pragma: no cover - fallback for script execution
    from config import LOG_LEVEL, APP_PORT, APP_VERSION  # type: ignore
    from utils.responses import success, error  # type: ignore


def create_app() -> Flask:
    """
    Flask 애플리케이션 팩토리.

    - 로깅 레벨을 설정하고
    - 헬스 체크 및 마스킹 처리 라우트를 등록합니다.

    Returns:
        Flask: 구성된 Flask 앱 인스턴스
    """
    app = Flask(__name__)
    app.logger.setLevel(LOG_LEVEL)

    @app.route("/health", methods=["GET"])
    def health() -> Tuple[Any, int]:
        """간단한 헬스 체크 엔드포인트."""
        return success("OK", {"version": APP_VERSION})

    @app.route("/api/masking", methods=["POST"])
    def masking_handler():
        """
        프롬프트(및 선택 PDF)를 받아 개인정보/민감정보를 마스킹합니다.

        요청 형식:
          - multipart/form-data:
              - prompt_json: 프롬프트 템플릿에 들어갈 답변(JSON 문자열)
              - pdf_file: (선택) 함께 분석할 PDF 파일
          - application/json:
              - {"prompt_json": {...}} 또는 질문 키(question1, question2, ...)를 직접 포함한 객체

        응답 필드:
          - original_prompt: 마스킹 전 원본 프롬프트
          - masked_prompt: 마스킹된 프롬프트
          - masked_entities: 마스킹에 사용된 엔티티 목록/치환 정보

        상태 코드:
          - 200: 성공
          - 400: 유효하지 않은 입력
          - 500: 서버 내부 오류
        """

        return error("마스킹 API는 이후 개발 예정입니다.", status=503)


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=APP_PORT)
