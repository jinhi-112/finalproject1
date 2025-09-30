import os
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from django.conf import settings

# SBERT 모델 로드 (한 번만 로드하여 재사용)
# settings.py에서 모델 경로를 설정하거나, 기본 모델을 사용합니다.
try:
    sbert_model = SentenceTransformer(getattr(settings, 'SBERT_MODEL_PATH', 'sentence-transformers/all-MiniLM-L6-v2'))
except Exception as e:
    print(f"Error loading SBERT model: {e}")
    sbert_model = None # 모델 로드 실패 시 None으로 설정

def generate_embedding(text: str):
    """
    텍스트를 입력받아 SBERT 임베딩 벡터를 반환합니다.
    """
    if not sbert_model:
        print("SBERT model not loaded. Cannot generate embedding.")
        return None
    if not text:
        return None
    embeddings = sbert_model.encode(text)
    return embeddings.tolist() # JSONField에 저장하기 위해 리스트로 변환

def calculate_similarity(embedding1: list, embedding2: list):
    """
    두 임베딩 벡터 간의 코사인 유사도를 계산합니다.
    """
    if not embedding1 or not embedding2:
        return 0.0
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0.0
    return dot_product / (norm_vec1 * norm_vec2)

def generate_match_explanation(item1_text: str, item2_text: str):
    """
    OpenAI API를 사용하여 매칭된 항목에 대한 자연어 설명을 생성합니다.
    """
    api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        print("OPENAI_API_KEY is not set.")
        return "매칭 설명 생성에 실패했습니다: API 키가 설정되지 않았습니다."

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # 또는 다른 적절한 모델
            messages=[
                {"role": "system", "content": "You are a helpful assistant that explains the matching between two items."},
                {"role": "user", "content": f"다음 두 항목이 왜 잘 매칭되는지 설명해 주세요: '{item1_text}' 와 '{item2_text}'"}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating match explanation with OpenAI API: {e}")
        return f"매칭 설명 생성 중 오류가 발생했습니다: {e}."