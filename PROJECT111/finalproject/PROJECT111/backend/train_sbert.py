# finalproject/PROJECT111/backend/train_sbert.py

from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import torch
import os
import pandas as pd # pandas 라이브러리 추가

# 1. 베이스 모델 로드 (한국어 모델 예시)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS', device=device)

# 2. 학습 데이터 준비 (InputExample 형식)
# CSV 파일 경로
csv_file_path = '/Users/macbookair/Desktop/finalproj/finalproject/matching_dataset.csv'

# CSV 파일 읽기
try:
    df = pd.read_csv(csv_file_path)
    print(f"'{csv_file_path}' 파일에서 {len(df)}개의 데이터 로드 완료.")
except FileNotFoundError:
    print(f"오류: '{csv_file_path}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    exit()
except Exception as e:
    print(f"CSV 파일 로드 중 오류 발생: {e}")
    exit()

train_examples = []
for index, row in df.iterrows():
    user_profile = row['사용자 프로필']
    project_description = row['프로젝트 설명']
    score = float(row['점수']) # 점수를 float 타입으로 변환
    train_examples.append(InputExample(texts=[user_profile, project_description], label=score))

# DataLoader 생성
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

# 3. 손실 함수 선택
train_loss = losses.CosineSimilarityLoss(model=model)

# 4. 모델 학습
num_epochs = 4 # 에포크 수 (데이터 양에 따라 조절)
warmup_steps = int(len(train_dataloader) * num_epochs * 0.1) # 워밍업 스텝

# 모델 저장 경로 설정 (backend 디렉토리 내 output 폴더)
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', 'my_sbert_model')
os.makedirs(output_path, exist_ok=True) # 폴더가 없으면 생성

print(f"SBERT 모델 학습 시작 (Epochs: {num_epochs}, Device: {device})...")
model.fit(train_objectives=[(train_dataloader, train_loss)],
          epochs=num_epochs,
          warmup_steps=warmup_steps,
          output_path=output_path, # 학습된 모델 저장 경로
          show_progress_bar=True,
          evaluator=None # 필요하다면 여기에 평가자 추가
         )

print(f"모델 학습 완료 및 '{output_path}'에 저장 완료!")
