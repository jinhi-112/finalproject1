import os
import numpy as np
from openai import OpenAI
from django.conf import settings
import json
import httpx
import logging

logger = logging.getLogger(__name__)

# --------------------------
# Lazy-load SBERT 모델 관리
# --------------------------
from sentence_transformers import SentenceTransformer
_sbert_model = None  # 전역 변수 (처음엔 None)

def get_sbert_model():
    """SBERT 모델을 처음 사용할 때만 로드하도록 설정"""
    global _sbert_model
    if _sbert_model is None:
        model_path = getattr(settings, 'SBERT_MODEL_PATH', os.path.join(os.getcwd(), "backend", "output", "my_sbert_model"))
        logger.info(f"📦 Loading SBERT model from: {model_path}")
        try:
            _sbert_model = SentenceTransformer(model_path)
        except Exception as e:
            logger.error(f"⚠️ Error loading SBERT model from {model_path}: {e}")
            # 로드 실패 시 기본 모델로 대체
            _sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("✅ Fallback: Loaded default 'all-MiniLM-L6-v2' model")
    return _sbert_model


# --------------------------
# 임베딩 생성
# --------------------------
def generate_embedding(text: str):
    """텍스트를 입력받아 SBERT 임베딩 벡터를 반환합니다."""
    if not text:
        return None
    try:
        model = get_sbert_model()
        embeddings = model.encode(text, convert_to_tensor=False)
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"❌ Error generating embedding: {e}")
        return None


# --------------------------
# 코사인 유사도 계산
# --------------------------
def calculate_similarity(embedding1: list, embedding2: list):
    """두 임베딩 벡터 간의 코사인 유사도를 계산"""
    if not embedding1 or not embedding2:
        return 0.0
    try:
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
        return 0.0


# --------------------------
# OpenAI 기반 매칭 설명 생성
# --------------------------
def generate_match_explanation(user_data: dict, project_data: dict, similarity_score: float):
    """OpenAI API로 매칭 분석 및 설명 생성"""
    api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        logger.warning("OPENAI_API_KEY is not set.")
        return None

    client = OpenAI(api_key=api_key, http_client=httpx.Client(trust_env=False))

    user_info_str = json.dumps(user_data, ensure_ascii=False, indent=2)
    project_info_str = json.dumps(project_data, ensure_ascii=False, indent=2)

    prompt = f"""사용자 프로필과 프로젝트 정보가 주어지면, 이 둘의 전반적인 매칭률이 {similarity_score:.0f}%인 이유를 분석해주세요.

[분석 기준]
1. 기술 매칭: 사용자의 기술 스택과 프로젝트의 기술 스택의 일치도를 평가 (100점 만점)
2. 성향 적합도: 사용자의 협업 스타일, 선호 주제 등과 프로젝트의 특성의 일치도를 평가 (100점 만점)
3. 경험 수준: 사용자의 전공, 숙련도와 프로젝트의 연관성을 평가 (100점 만점)
4. 종합 설명: 위 세부 점수를 바탕으로, 왜 이런 점수가 나왔는지 종합적으로 2-3문장으로 설명.

[사용자 정보]
{user_info_str}

[프로젝트 정보]
{project_info_str}

[출력 형식]
반드시 아래와 같은 JSON 형식으로만 응답해주세요.
{{
  "tech_score": <기술 매칭 점수 (0-100 사이 정수)>,
  "personality_score": <성향 적합도 점수 (0-100 사이 정수)>,
  "experience_score": <경험 수준 점수 (0-100 사이 정수)>,
  "explanation": "<종합 설명 텍스트>"
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes user–project match and returns JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.5
        )
        result_json = json.loads(response.choices[0].message.content)
        return result_json
    except Exception as e:
        logger.error(f"Error generating match explanation with OpenAI API: {e}")
        return None


# --------------------------
# Match Service
# --------------------------
from teamspace.models import User, Projects, UserEmbedding, ProjectEmbedding, MatchScores

class MatchService:
    """사용자와 프로젝트 매칭 점수 및 추천 로직"""
    @staticmethod
    def get_or_create_match_score(user: User, project: Projects):
        logger.info(f"🔍 Calculating match score for user {user.email} and project {project.title}")
        match_score_entry, created = MatchScores.objects.get_or_create(
            user=user, project=project,
            defaults={'score': 0.0, 'explanation': ''}
        )

        # 기존 데이터가 유효하면 그대로 반환
        if not created and match_score_entry.explanation and match_score_entry.score != 0.0:
            return match_score_entry

        # 임베딩 확인
        try:
            user_embedding_obj = UserEmbedding.objects.get(user=user)
            project_embedding_obj = ProjectEmbedding.objects.get(project=project)
        except (UserEmbedding.DoesNotExist, ProjectEmbedding.DoesNotExist):
            match_score_entry.score = 0.0
            match_score_entry.explanation = "임베딩이 생성되지 않아 매칭 점수를 계산할 수 없습니다."
            match_score_entry.save()
            return match_score_entry

        user_embedding = user_embedding_obj.embedding
        project_embedding = project_embedding_obj.embedding

        # 유사도 계산
        if user_embedding and project_embedding:
            score = calculate_similarity(user_embedding, project_embedding) * 100
            match_score_entry.score = round(score, 2)

            user_data = {
                "major": user.major,
                "specialty": user.specialty,
                "tech_stack": user.tech_stack,
                "experience_level": user.experience_level,
                "preferred_project_topics": user.preferred_project_topics,
                "collaboration_style": user.collaboration_style,
                "belbin_role": user.belbin_role,
            }
            project_data = {
                "title": project.title,
                "description": project.description,
                "goal": project.goal,
                "tech_stack": project.tech_stack,
            }

            explanation_data = generate_match_explanation(user_data, project_data, match_score_entry.score)
            if explanation_data:
                match_score_entry.tech_score = explanation_data.get("tech_score", 0)
                match_score_entry.personality_score = explanation_data.get("personality_score", 0)
                match_score_entry.experience_score = explanation_data.get("experience_score", 0)
                match_score_entry.explanation = explanation_data.get("explanation", "설명을 생성하지 못했습니다.")
            else:
                match_score_entry.explanation = "매칭 분석 데이터 생성에 실패했습니다."
        else:
            match_score_entry.score = 0.0
            match_score_entry.explanation = "임베딩 데이터가 유효하지 않아 매칭 점수를 계산할 수 없습니다."
        
        match_score_entry.save()
        return match_score_entry

    @staticmethod
    def get_user_project_match(user: User, project: Projects):
        """특정 사용자와 프로젝트의 매칭 결과 반환 (없으면 새로 계산)"""
        return MatchService.get_or_create_match_score(user, project)

    @staticmethod
    def get_recommended_projects(user: User):
        """AI 기반 프로젝트 추천"""
        all_projects = Projects.objects.filter(is_open=True)
        recommended_projects_data = []

        for project in all_projects:
            match_score_entry = MatchService.get_or_create_match_score(user, project)
            recommended_projects_data.append({
                'project': project,
                'score': match_score_entry.score,
                'explanation': match_score_entry.explanation
            })

        recommended_projects_data.sort(key=lambda x: x['score'], reverse=True)
        return recommended_projects_data
