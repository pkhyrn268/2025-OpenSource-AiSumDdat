#직업 태그 추가한 버전

import torch
import json
from datasets import load_dataset
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
    TrainingArguments,
    Trainer,
)
import numpy as np
import evaluate

# --- 1. 설정 및 로딩 ---
# 경로 설정
base_model_path = "./local_models/KoELECTRA-small-v3-modu-ner"  # 1단계에서 다운로드한 원본 모델 경로
dataset_path = "./DATASET/data.jsonl" # 2단계에서 생성한 데이터셋 경로
finetuned_model_output_path = "./local_models/finetuned_ner_model" # 최종 파인튜닝된 모델이 저장될 경로

# 라벨 맵 로딩 (2단계에서 사용한 것과 반드시 동일해야 함)
label2id = {
    "O": 0,
    "B-PS": 1, "I-PS": 2,          # 사람
    "B-LC": 3, "I-LC": 4,          # 위치
    "B-OG": 5, "I-OG": 6,          # 기관
    "B-DT": 7, "I-DT": 8,          # 날짜
    "B-BD": 9, "I-BD": 10,         # 생년월일
    "B-PN": 11, "I-PN": 12,        # 전화번호
    "B-SSN": 13, "I-SSN": 14,      # 주민번호
    "B-AN": 15, "I-AN": 16,        # 계좌번호
    "B-CCD": 17, "I-CCD": 18,      # 카드번호
    "B-CVC": 19, "I-CVC": 20,      # CVC
    "B-EM": 21, "I-EM": 22,        # 이메일
    "B-PPS": 23, "I-PPS": 24,      # 여권번호 (PPS: Passport)
    "B-AG": 25, "I-AG": 26,        # 나이
    "B-GD": 27, "I-GD": 28,        # 성별
    "B-JOB":29, "I-JOB":30         # 직업
}

id2label = {v: k for k, v in label2id.items()}
all_labels = list(label2id.keys()) # 모든 라벨 리스트

# 토크나이저 로딩
tokenizer = AutoTokenizer.from_pretrained(base_model_path)

# 모델 로딩
# **중요**: ignore_mismatched_sizes=True를 추가하여 크기가 다른 분류 레이어는 무시하고 새로 초기화
model = AutoModelForTokenClassification.from_pretrained(
    base_model_path,
    num_labels=len(all_labels),
    id2label=id2label,
    label2id=label2id,
    ignore_mismatched_sizes=True,
)

# 데이터셋 로딩
raw_datasets = load_dataset('json', data_files=dataset_path, split="train")

# --- 2. 데이터 전처리 ---
def tokenize_and_align_labels(examples):
    """데이터셋을 토크나이징하고, 라벨을 토큰에 맞게 정렬하는 함수"""
    tokenized_inputs = tokenizer(
        examples["tokens"], 
        truncation=True, 
        is_split_into_words=True # 입력이 이미 단어 리스트임을 명시
    )

    labels = []
    for i, label in enumerate(examples[f"ner_tags"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None: # [CLS], [SEP] 같은 스페셜 토큰
                label_ids.append(-100)
            elif word_idx != previous_word_idx: # 새로운 단어의 첫 토큰
                label_ids.append(label[word_idx])
            else: # 같은 단어의 서브워드 토큰
                label_ids.append(-100)
            previous_word_idx = word_idx
        labels.append(label_ids)
    
    tokenized_inputs["labels"] = labels
    return tokenized_inputs


# ======================================================================
# ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ 디버깅 및 검증 로직 ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
# ======================================================================
print("INFO: 🔍 데이터셋 개별 검증을 시작합니다...")
found_error = False
for i, example in enumerate(raw_datasets):
    # 1. 'tokens' 또는 'ner_tags' 키 존재 여부 확인
    if 'tokens' not in example or 'ner_tags' not in example:
        print(f"ERROR: 💥 {i}번째 데이터에 'tokens' 또는 'ner_tags' 키가 없습니다. 확인해주세요.")
        print(f"   - 내용: {example}")
        found_error = True
        break
        
    # 2. 개수 불일치 확인
    if len(example['tokens']) != len(example['ner_tags']):
        print(f"ERROR: 💥 {i}번째 데이터에서 개수 불일치 발견!")
        print(f"   - 토큰 ({len(example['tokens'])}개): {example['tokens']}")
        print(f"   - 라벨 ({len(example['ner_tags'])}개): {example['ner_tags']}")
        found_error = True
        break

    # 3. 빈 문자열("") 또는 None 값 확인
    if "" in example['tokens'] or None in example['tokens']:
        print(f"ERROR: 💥 {i}번째 데이터의 'tokens' 리스트에 빈 문자열이나 None 값이 있습니다.")
        print(f"   - 토큰: {example['tokens']}")
        found_error = True
        break
        
    # 4. 전처리 함수를 직접 실행하여 실제 오류 재현
    try:
        # 함수가 배치(batch) 단위로 동작하므로, 개별 데이터를 리스트로 묶어 테스트
        mock_batch = {
            'tokens': [example['tokens']],
            'ner_tags': [example['ner_tags']]
        }
        tokenize_and_align_labels(mock_batch)
    except IndexError as e:
        print(f"ERROR: 💥 {i}번째 데이터 처리 중 'IndexError' 발생!")
        print(f"   - 이 데이터에 문제가 있을 확률이 매우 높습니다. 내용을 자세히 확인해주세요.")
        print(f"   - 토큰 ({len(example['tokens'])}개): {example['tokens']}")
        print(f"   - 라벨 ({len(example['ner_tags'])}개): {example['ner_tags']}")
        found_error = True
        break

if found_error:
    print("\nINFO: 🛑 위에 보고된 문제가 있는 데이터를 'data.jsonl' 파일에서 수정한 후 다시 실행해주세요.")
    exit() # 프로그램 종료
else:
    print("INFO: ✅ 모든 데이터가 개별 검증을 통과했습니다. 모델 훈련을 계속합니다.")
# ======================================================================
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ 검증 로직 끝 ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
# ======================================================================


# 데이터셋에 전처리 함수 적용
tokenized_datasets = raw_datasets.map(tokenize_and_align_labels, batched=True, remove_columns=raw_datasets.column_names)

# 데이터 로더를 위한 collator 설정
data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

# --- 3. 훈련(Training) 설정 ---
# 평가 지표 설정 (seqeval)
seqeval = evaluate.load("seqeval")

def compute_metrics(p):
    """예측값과 실제값을 받아 성능을 계산하는 함수"""
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)

    true_predictions = [
        [all_labels[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [all_labels[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]

    results = seqeval.compute(predictions=true_predictions, references=true_labels)
    return {
        "precision": results["overall_precision"],
        "recall": results["overall_recall"],
        "f1": results["overall_f1"],
        "accuracy": results["overall_accuracy"],
    }

# Trainer를 위한 인자(argument) 설정
training_args = TrainingArguments(
    output_dir=finetuned_model_output_path,      # 모델과 로그가 저장될 경로
    learning_rate=2e-5,                          # 학습률
    per_device_train_batch_size=8,               # 장치(GPU)당 훈련 배치 사이즈
    num_train_epochs=20,                          # 총 훈련 에포크 수
    weight_decay=0.01,                           # 가중치 감소 (과적합 방지)
    logging_strategy="epoch",                    # 에포크 단위로 로그 기록
    # evaluation_strategy="epoch",             # 실제로는 검증 데이터셋을 분리하여 평가해야 함
    # save_strategy="epoch",
    # load_best_model_at_end=True,
)

# Trainer 객체 생성
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets,
    # eval_dataset=... # 검증 데이터셋을 여기에 전달
    tokenizer=tokenizer,
    data_collator=data_collator,
    # compute_metrics=compute_metrics, # 평가 시 주석 해제
)

# --- 4. 훈련 실행 및 저장 ---
print("INFO: 🚀 모델 파인튜닝을 시작합니다!")
trainer.train()

print("INFO: ✅ 훈련이 완료되었습니다.")
trainer.save_model(finetuned_model_output_path)
print(f"INFO: ✅ 파인튜닝된 모델이 '{finetuned_model_output_path}' 경로에 저장되었습니다.")