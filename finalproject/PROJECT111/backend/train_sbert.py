# finalproject/PROJECT111/backend/train_sbert.py

from sentence_transformers import SentenceTransformer, InputExample, losses
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from torch.utils.data import DataLoader
import torch
import os
import pandas as pd
import math

# 1. 베이스 모델 로드 (한국어 모델 예시)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS', device=device)

# 2. 데이터셋 로드 및 분리
# CSV 파일 경로
csv_file_path = '/Users/macbookair/Desktop/finalproj/finalproject/matching_dataset.csv'

# CSV 파일 읽기
try:
    # 결측치가 있는 행은 제거
    df = pd.read_csv(csv_file_path).dropna()
    print(f"'{csv_file_path}' 파일에서 {len(df)}개의 데이터 로드 완료.")
except FileNotFoundError:
    print(f"오류: '{csv_file_path}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    exit()
except Exception as e:
    print(f"CSV 파일 로드 중 오류 발생: {e}")
    exit()

# 데이터를 학습용과 평가용으로 분리 (80:20 비율)
train_df = df.sample(frac=0.8, random_state=42)
eval_df = df.drop(train_df.index)
print(f"학습 데이터: {len(train_df)}개, 평가 데이터: {len(eval_df)}개로 분리합니다.")

# 3. 학습 데이터 준비 (InputExample 형식)
train_examples = []
for index, row in train_df.iterrows():
    user_profile = str(row['사용자 프로필'])
    project_description = str(row['프로젝트 설명'])
    score = float(row['점수'])
    train_examples.append(InputExample(texts=[user_profile, project_description], label=score))

train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.CosineSimilarityLoss(model=model)

# 4. 평가 데이터 준비 및 평가자(Evaluator) 생성
dev_samples = []
for index, row in eval_df.iterrows():
    user_profile = str(row['사용자 프로필'])
    project_description = str(row['프로젝트 설명'])
    score = float(row['점수'])
    dev_samples.append(InputExample(texts=[user_profile, project_description], label=score))

# 평가자는 코사인 유사도와 스피어만 순위 상관계수를 계산합니다.
evaluator = EmbeddingSimilarityEvaluator.from_input_examples(dev_samples, name='sts-dev')

# 5. 모델 학습
num_epochs = 4
warmup_steps = math.ceil(len(train_dataloader) * num_epochs * 0.1)
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', 'my_sbert_model_with_eval')
os.makedirs(output_path, exist_ok=True)

print(f"SBERT 모델 학습 시작 (Epochs: {num_epochs}, Device: {device})...")

# model.fit에 evaluator를 추가하여 학습 중간 및 최종 평가를 수행
model.fit(train_objectives=[(train_dataloader, train_loss)],
          epochs=num_epochs,
          warmup_steps=warmup_steps,
          evaluator=evaluator,
          evaluation_steps=int(len(train_dataloader) * 0.2), # 1 에포크 당 5번 평가
          output_path=output_path,
          show_progress_bar=True
         )

print(f"모델 학습 및 평가 완료! 모델은 '{output_path}'에 저장되었습니다.")