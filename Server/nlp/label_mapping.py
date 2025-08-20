from typing import Optional


# 원본 라벨 -> 표준 코드(약어) 정규화
_MAP_TO_CODE = {
    # 인물/조직/위치
    "PERSON": "PS", "PER": "PS", "PS": "PS",
    "ORG": "OG", "ORGANIZATION": "OG", "OG": "OG",
    "LOC": "LC", "LOCATION": "LC", "LC": "LC",

    # 날짜/시간/수량/나이
    "DATE": "DT", "DAT": "DT", "DT": "DT",
    "TIME": "TI", "TI": "TI",
    "QUANTITY": "QT", "QT": "QT",
    "AGE": "AG", "AG": "AG",

    # 연락처/식별자
    "PHONE_NUMBER": "PH", "PHONE": "PH", "TEL": "PH", "PH": "PH", "PN": "PH",
    "EMAIL_ADDRESS": "EM", "EMAIL": "EM", "EM": "EM",
    "CREDIT_CARD": "CC", "CREDIT_CARD_NUMBER": "CC", "CARD_NUMBER": "CC", "CC": "CC", "CCD": "CC",
    "ACCOUNT_NUMBER": "AC", "BANK_ACCOUNT": "AC", "AC": "AC", "AN": "AC",
    "SOCIAL_SECURITY_NUMBER": "RRN", "KR_RRN": "RRN", "RRN": "RRN", "SSN": "RRN",

    # 스크립트 전용 라벨(그대로 유지)
    "CVC": "CVC", "PPS": "PPS",

    # 그 외(모델/데이터에 있을 수 있는 라벨들)
    "FD": "FD", "TR": "TR", "CV": "CV", "AM": "AM",
    "PT": "PT", "MT": "MT", "AF": "AF", "EV": "EV", "TM": "TM",
}

# 표준 코드 -> 한국어 표시명
_DISPLAY_KO = {
    "PS": "이름",
    "OG": "기관",
    "LC": "주소/지역",
    "DT": "날짜",
    "TI": "시간",
    "QT": "수량",
    "AG": "나이",
    "PH": "전화번호",
    "EM": "이메일",
    "CC": "카드번호",
    "AC": "계좌번호",
    "RRN": "주민등록번호",
    "CVC": "CVC",
    "PPS": "여권번호",
    # 기타 도메인 라벨(선택)
    "FD": "학문",
    "TR": "이론",
    "CV": "문명",
    "AM": "동물",
    "PT": "식물",
    "MT": "물질",
    "AF": "인공물",
    "EV": "이벤트",
    "TM": "단위",
}

# 표준 코드 -> 영어 표시명(옵션)
_DISPLAY_EN = {
    "PS": "NAME",
    "OG": "ORGANIZATION",
    "LC": "LOCATION",
    "DT": "DATE",
    "TI": "TIME",
    "QT": "QUANTITY",
    "AG": "AGE",
    "PH": "PHONE",
    "EM": "EMAIL",
    "CC": "CREDIT_CARD",
    "AC": "ACCOUNT_NUMBER",
    "RRN": "SSN",
    "CVC": "CVC",
    "PPS": "PASSPORT",
    "FD": "FIELD",
    "TR": "TERM",
    "CV": "CIVILIZATION",
    "AM": "ANIMAL",
    "PT": "PLANT",
    "MT": "MATERIAL",
    "AF": "ARTIFACT",
    "EV": "EVENT",
    "TM": "UNIT",
}


def to_standard_label(label: str) -> Optional[str]:
    if not label:
        return None
    return _MAP_TO_CODE.get(label)


def to_display_label(label: str, locale: str = "ko") -> str:
    """
    원본/표준 라벨을 받아 표시용 라벨 텍스트를 반환합니다.
    1) 표준 코드로 정규화 → 2) locale에 맞는 표시명 조회 → 3) 없으면 코드 그대로
    """
    code = to_standard_label(label) or label
    if locale.lower().startswith("ko"):
        return _DISPLAY_KO.get(code, code)
    if locale.lower().startswith("en"):
        return _DISPLAY_EN.get(code, code)
    return code


