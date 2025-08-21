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
    from .services.prompt_builder import build_prompt
    # from .services.pdf_service import extract_text_from_pdf
    from .services.masking_service import mask_text_with_models
    from .utils.responses import success, error
except Exception:  # pragma: no cover - fallback for script execution
    from config import LOG_LEVEL, APP_PORT, APP_VERSION  # type: ignore
    from services.prompt_builder import build_prompt  # type: ignore
    from services.pdf_service import extract_text_from_pdf  # type: ignore
    from services.masking_service import mask_text_with_models  # type: ignore
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
        try:
            # 1) form-data 우선 처리: prompt_json 필드가 존재하면 이를 먼저 사용
            prompt_data: Dict[str, Any] | None = None
            if "prompt_json" in request.form:
                prompt_json_raw: str = request.form.get("prompt_json", "").strip()
                if prompt_json_raw:
                    try:
                        prompt_data = json.loads(prompt_json_raw)
                    except Exception:
                        return error("prompt_json JSON 파싱에 실패했습니다.", 400)

            # 2) JSON 본문 처리(form-data 미제공 시):
            #    - {"prompt_json": {...}}
            #    - 또는 question* 키를 직접 포함한 dict
            if prompt_data is None:
                body_json = request.get_json(silent=True) or {}
                if isinstance(body_json, dict):
                    if "prompt_json" in body_json and isinstance(body_json["prompt_json"], dict):
                        prompt_data = body_json["prompt_json"]
                    elif any(k.startswith("question") for k in body_json.keys()):
                        prompt_data = body_json  # 직접 질문 키 전달

            if not isinstance(prompt_data, dict):
                return error("필수 입력이 누락되었습니다. form의 prompt_json 또는 JSON 본문을 사용하세요.", 400)

            # 템플릿 답변으로부터 전체 프롬프트 생성
            original_prompt_all = build_prompt(prompt_data)

            # (선택) PDF 첨부 처리
            if "pdf_file" in request.files and request.files["pdf_file"]:
                try:
                    pdf_storage = request.files["pdf_file"]
                    pdf_bytes = io.BytesIO(pdf_storage.read())
                    pdf_text = extract_text_from_pdf(pdf_bytes)
                    if pdf_text:
                        # 구분자와 함께 PDF 본문을 프롬프트에 추가
                        original_prompt_all = (
                            f"{original_prompt_all}\n\n[PDF 내용]\n{pdf_text}"
                        )
                except Exception as e:
                    logging.exception("PDF 파일 처리 중 오류")
                    return error("PDF 파일 처리 중 오류가 발생했습니다.", 500)

            # 반환은 question2의 내용만
            q2_text = prompt_data.get("question2", "")
            if not isinstance(q2_text, str):
                q2_text = ""

            # 모델들을 활용해 question2 텍스트만 마스킹
            masked_prompt, masked_entities = mask_text_with_models(q2_text)

            return success(
                "마스킹 처리가 완료되었습니다.",
                {
                    # 반환은 question2만
                    "original_prompt": q2_text,
                    "masked_prompt": masked_prompt,
                    "masked_entities": masked_entities,
                },
            )
        except Exception as e:
            logging.exception("/api/masking 처리 중 오류")
            return error("서버 내부 오류가 발생했습니다.", 500)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=APP_PORT)
