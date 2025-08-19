import os
from dataclasses import dataclass
from functools import lru_cache


def _getenv_bool(key: str, default: bool) -> bool:
    """환경변수 boolean 파싱."""
    value = os.getenv(key)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "y")


@dataclass(frozen=True)
class AppConfig:
    """애플리케이션 전역 설정 값."""
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    port: int = int(os.getenv("PORT", "8080"))
    default_locale: str = os.getenv("DEFAULT_LOCALE", "ko")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    text_model_path: str = os.getenv(
        "TEXT_MODEL_PATH", "Leo97/KoELECTRA-small-v3-modu-ner"
    )
    numeric_model_path: str = os.getenv(
        "NUMERIC_MODEL_PATH", "./test/local_models/finetuned_ner_model"
    )
    use_cuda: bool = _getenv_bool("USE_CUDA", True)
    disable_local_ner: bool = _getenv_bool("DISABLE_LOCAL_NER", False)
    disable_presidio: bool = _getenv_bool("DISABLE_PRESIDIO", False)


CONFIG = AppConfig()


def _resolve_device() -> int:
    """GPU 사용 가능 여부에 따라 device 인덱스 결정."""
    try:
        import torch  # type: ignore

        if CONFIG.use_cuda and torch.cuda.is_available():
            return 0
        return -1
    except Exception:
        return -1


@lru_cache(maxsize=1)
def get_device() -> int:
    """지연 계산/캐시된 device 인덱스."""
    return _resolve_device()


# 자주 쓰는 별칭 (가독성용)
LOG_LEVEL = CONFIG.log_level
APP_PORT = CONFIG.port
DEFAULT_LOCALE = CONFIG.default_locale
APP_VERSION = CONFIG.app_version
TEXT_MODEL_PATH = CONFIG.text_model_path
NUMERIC_MODEL_PATH = CONFIG.numeric_model_path
DISABLE_LOCAL_NER = CONFIG.disable_local_ner
DISABLE_PRESIDIO = CONFIG.disable_presidio


__all__ = [
    "CONFIG",
    "get_device",
    "LOG_LEVEL",
    "APP_PORT",
    "DEFAULT_LOCALE",
    "APP_VERSION",
    "TEXT_MODEL_PATH",
    "NUMERIC_MODEL_PATH",
    "DISABLE_LOCAL_NER",
    "DISABLE_PRESIDIO",
    "AppConfig",
]


