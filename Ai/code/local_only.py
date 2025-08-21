import torch
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from presidio_analyzer import RecognizerResult, AnalysisExplanation, Pattern, PatternRecognizer
import re





# --- 1. 모델 로딩 ---
print("모델 로딩을 시작합니다...")

numeric_model_path = "./local_models/finetuned_ner_model" 
numeric_ner_pipeline = pipeline(
    "ner", model=AutoModelForTokenClassification.from_pretrained(numeric_model_path),
    tokenizer=AutoTokenizer.from_pretrained(numeric_model_path),
    aggregation_strategy="simple", device=0 if torch.cuda.is_available() else -1
)
print(f"✅ 숫자 모델 '{numeric_model_path}' 로딩 완료")


# --- 2. 규칙 기반 탐지기 정의 ---
account_recognizer = PatternRecognizer(
    supported_entity="AN", name="AccountNumberRecognizer",
    patterns=[Pattern(name="계좌번호 패턴", regex=r"\b\d{2,6}[-]\d{2,6}[-]\d{2,6}\b", score=1.0)]
)
cvc_recognizer = PatternRecognizer(
    supported_entity="CVC", name="CvcRecognizer",
    patterns=[Pattern(name="CVC 패턴", regex=r"\b\d{3}\b", score=0.9)]
)
passport_recognizer = PatternRecognizer(
    supported_entity="PPS", name="PassportRecognizer",
    patterns=[Pattern(name="여권번호 패턴", regex=r"\b[A-Za-z]\d{8}\b", score=1.0)]
)
ssn_recognizer = PatternRecognizer(
    supported_entity="SSN", name="SSMRecognizer",
    patterns=[Pattern(name="주민번호 패턴", regex=r"\b\d{6}[-]\d{7}\b", score=1.0)]
)
rule_recognizers = [account_recognizer, cvc_recognizer, passport_recognizer, ssn_recognizer]
print("✅ 규칙 기반 탐지기 생성 완료")


# --- 3. 헬퍼 함수 정의 ---
def convert_to_presidio_results(pipeline_outputs, recognizer_name):
    results = []
    for entity in pipeline_outputs:
        result = RecognizerResult(
            entity_type=entity['entity_group'], start=entity['start'], end=entity['end'],
            score=entity['score'],
            analysis_explanation=AnalysisExplanation(
                recognizer=recognizer_name, original_score=entity['score'],
                pattern_name=None, pattern=None
            )
        )
        results.append(result)
    return results

def resolve_conflicts(results: list[RecognizerResult]) -> list[RecognizerResult]:

    if not results:
        return []

    rule_recognizer_names = {r.name for r in rule_recognizers}
    discarded_indices = set()

    # 1. 규칙 기반 결과가 다른 결과(모델 또는 다른 규칙)에 완전히 포함되는지 확인
    for i, res1 in enumerate(results):
        # res1이 규칙 기반 결과가 아니면 건너뜁니다.
        if res1.analysis_explanation.recognizer not in rule_recognizer_names:
            continue

        for j, res2 in enumerate(results):
            if i == j:  # 자기 자신과는 비교하지 않습니다.
                continue

            # res2가 res1을 완전히 포함하는지(동일 범위 포함) 확인합니다.
            # (res2.start <= res1.start) and (res2.end >= res1.end)
            is_contained = res2.start <= res1.start and res2.end >= res1.end

            if is_contained:
                # res1(규칙 기반 결과)을 폐기 목록에 추가하고 다음 규칙 검사로 넘어갑니다.
                discarded_indices.add(i)
                break
    
    # 폐기 대상으로 표시되지 않은 결과만 필터링합니다.
    filtered_results = [res for i, res in enumerate(results) if i not in discarded_indices]

    # 2. 필터링된 결과 내에서 겹치는 부분을 최종 해결합니다.
    # 시작 위치(오름차순), 엔터티 길이(내림차순) 순으로 정렬합니다.
    # -> 시작점이 같을 경우, 더 긴 엔터티가 우선순위를 갖습니다.
    sorted_results = sorted(filtered_results, key=lambda r: (r.start, -(r.end - r.start)))
    
    final_results = []
    last_added_end = -1 # 마지막으로 추가된 결과의 끝 위치

    for res in sorted_results:
        # 현재 결과가 마지막으로 추가된 결과와 겹치지 않으면 추가합니다.
        if res.start >= last_added_end:
            final_results.append(res)
            last_added_end = res.end
            
    return final_results


# --- 4. 메인 실행 로직 ---
text = "삼성전자의 변호사인 45세 남성 홍길동(생년월일: 1980년 1월 1일, 주민번호: 800101-1234567, 여권번호: M12345678, 이메일: hong@samsung.law, 전화번호: 010-1234-5678)씨는 2025년 8월 13일 서울에서, 본인의 신한은행 계좌(110-123-987654)와 연동된 신용카드(카드번호: 4512-3456-7890-1234, CVC: 789)의 도용 사실을 신고했다."
#text = "서울에 사는 32세 남성 변호사 김민준(생년월일: 1993년 5월 10일, 주민번호: 930510-1234567)씨는 2025년 8월 15일, 삼성전자에서 자신의 신한은행 계좌(110-234-567890)로 결제를 시도하던 중, 여권번호(M12345678) 정보가 유출된 사실을 알게 되어 개인 이메일(minjun.kim@email.com)과 휴대폰(010-1111-2222)으로 고객센터에 연락했으며, 분실된 카드는 4512-3456-7890-1234이고 CVC는 123이라고 밝혔습니다."
#text = "부산의 IT 개발자인 이서연씨(여성, 28세)는 2024년 12월 24일에 카카오로부터 온 알림을 통해 자신의 국민카드(5123-6789-1234-5678, CVC: 456)가 도용되었음을 확인했고, 여권번호(M87654321)와 주민등록번호(970101-2345678)를 이용해 본인 인증 후, 해당 내역이 자신의 기업은행 계좌(01-2345-6789)와 관련 없음을 전화(010-3333-4444) 및 이메일(seoyeon.lee@email.com)로 신고했으며, 그녀의 생일은 1997년 1월 1일입니다."
#text = "대구에서 근무하는 45세의 남성 의사, 박현우(주민번호: 801120-1987654, 생년월일: 1980년 11월 20일)는 2026년 1월 1일 현대자동차 지점에서 여권(M98765432)을 제시하고 하나은행 계좌(881-123456-789)에 연결된 현대카드(9440-1234-5678-9012, CVC: 789)로 계약했으며, 관련 서류는 그의 전화번호(010-5555-6666)와 메일(hyunwoo.park@email.com)로 전송되었습니다."
#text = "인천 송도의 교사인 최지아씨(여성, 35세, 생년월일: 1990년 3월 14일)는 2025년 9월 30일 네이버를 통해 항공권을 예매하며 주민번호(900314-2121212)와 여권(M24681357) 정보를 입력했고, 결제에 사용된 삼성카드(5521-8765-4321-0987, CVC 567)의 출금 계좌는 우리은행(1002-876-543210)이며, 문의사항은 휴대폰(010-7777-8888)이나 이메일 주소(jia.choi@email.com)로 연락 달라고 남겼습니다."
#text = "광주광역시에 거주하는 대학생 정우진(남성, 21세, 생년월일: 2004년 7월 7일, 주민번호: 040707-3344556)군은 2025년 10월 11일 SK텔레콤 대리점에서 여권번호(M11223344)를 이용해 신규 가입을 진행했으며, 그의 연락처는 010-9999-0000이고 이메일은 woojin.jeong@email.com입니다. 또한, 그는 아르바이트 급여를 받을 농협 계좌(302-1234-5678-01)와 연결된 체크카드(4213-1234-5678-9012, CVC 321) 정보를 함께 제출했습니다."
#text = "대전의 공무원 윤하은(39세, 여성)은 2023년 7월 20일, 대한항공 웹사이트에서 본인(주민번호: 860808-2828282, 생년월일: 1986년 8월 8일)과 자녀의 여권(M33445566) 정보를 등록하고, 신한카드(4488-1234-5678-9012, CVC: 876)로 마일리지를 구매했으며, 이 과정에서 본인 연락처(010-1234-5678)와 이메일(haeun.yoon@email.com), 그리고 자동이체를 위한 IBK기업은행 계좌(275-012345-01-011)를 확인했습니다."
#text = "수원에 사는 51세 남성 자영업자 강태호씨는 2025년 11월 5일 쿠팡에서 발생한 카드 부정사용(롯데카드 4567-1234-5678-9012, CVC 987)을 신고하기 위해 본인의 주민등록번호(740228-1765432)와 생년월일(1974년 2월 28일)을 밝혔고, 여권 만료일(M55667788)과 주거래 계좌(KB국민은행 987654-01-123456), 전화번호(010-2468-1357), 이메일(taeho.kang@email.com)을 고객센터에 전달했습니다."
#text = "제주도의 프리랜서 디자이너인 백시우(26세, 남성, 생년월일: 1999년 10월 25일)는 2026년 2월 14일 애플 계정(siwoo.baek@email.com)에 등록된 현대카드(5321-1234-5678-9012, CVC: 210) 정보 변경을 위해 여권(M66778899)과 주민번호(991025-1543219)로 본인 인증을 했고, 이 과정에서 그의 휴대폰(010-3141-5926)과 카카오뱅크 계좌(3333-01-1234567) 정보가 정확한지 재확인했습니다."
#text = "울산의 현대중공업에 재직 중인 엔지니어 한지민씨(여성, 33세)는 2025년 8월 20일에 회사에 제출할 서류를 준비하며 자신의 생년월일(1992년 4월 16일)과 주민번호(920416-2987654), 여권번호(M77889900), 연락처(010-8282-8282), 개인 메일(jimin.han@email.com), 그리고 급여를 받을 경남은행 계좌(207-12-345678) 및 회사 제휴 법인카드(9410-1234-5678-9012, CVC 112) 정보를 기입했습니다."
#text = "경기도 성남시에 사는 48세 남성 교수 서준영은 2024년 6월 8일, LG전자 서비스센터에 이메일(junyeong.seo@email.com)로 제품 수리를 문의하며 본인 확인을 위해 생년월일(1977년 12월 1일), 주민등록번호(771201-1432198), 여권번호(M88990011), 핸드폰 번호(010-5050-6060)를 제공했고, 환불받을 우체국 계좌(701234-02-123456)와 결제 취소할 BC카드(5200-1234-5678-9012, CVC: 334) 정보를 전달했습니다."

print("\n--- 분석 시작 ---")

# 1. 모델 파이프라인 실행
numeric_model_outputs = numeric_ner_pipeline(text)
numeric_presidio_results = convert_to_presidio_results(numeric_model_outputs, "NumericRecognizer")

# 2. 규칙 기반 탐지기 실행
rule_based_results = []
for recognizer in rule_recognizers:
    results = recognizer.analyze(text=text, entities=recognizer.supported_entities)
    rule_based_results.extend(results)

# 3. 모든 결과를 하나의 리스트로 병합
all_results = numeric_presidio_results + rule_based_results

print("\n\n🔍 [모든 탐지 결과 (병합 전)]")
if all_results:
    for res in sorted(all_results, key=lambda x: x.start):
        print(f"  - {res.entity_type}: '{text[res.start:res.end]}' (Score: {res.score:.2f}, by {res.analysis_explanation.recognizer})")

# 4. 🛡️ 충돌 해결
final_results = resolve_conflicts(all_results)
print("\n\n🛡️ [충돌 해결 후 최종 엔터티 목록]")
if final_results:
    for res in final_results:
        print(f"  - {res.entity_type}: '{text[res.start:res.end]}' (Score: {res.score:.2f}, by {res.analysis_explanation.recognizer})")

# 5. 최종 마스킹
masked_text = text
for res in sorted(final_results, key=lambda x: x.start, reverse=True):
    placeholder = f"[{res.entity_type}]"
    masked_text = masked_text[:res.start] + placeholder + masked_text[res.end:]



#######
DISPLAY_KO = {
    "[PS]": "[이름]",
    "[PN]": "[전화번호]",
    "[LC]": "[위치]",
    "[OG]": "[기관]",
    "[DT]": "[날짜]",
    "[BD]": "[생년월일]",
    "[SSN]": "[주민등록번호]",
    "[AN]": "[계좌번호]",
    "[CCD]": "[카드번호]",
    "[CVC]": "[CVC]",
    "[EM]": "[이메일]",
    "[PPS]": "[여권번호]",
    "[AG]": "[나이]",
    "[GD]": "[성별]",
    "[JOB]": "[직업]"
}

for k, v in DISPLAY_KO.items():
    masked_text = masked_text.replace(k, v)
#######

print("\n\n✅ [최종 마스킹 결과]")
print("[원문]")
print(text)
print("\n[마스킹문]")
print(masked_text)