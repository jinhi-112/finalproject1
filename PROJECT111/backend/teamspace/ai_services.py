import os
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from django.conf import settings
import json
import httpx
import logging # Import logging

logger = logging.getLogger(__name__) # Get logger instance

# SBERT 모델 로드 (한 번만 로드하여 재사용)
# settings.py에서 모델 경로를 설정하거나, 기본 모델을 사용합니다.
try:
    sbert_model = SentenceTransformer(getattr(settings, 'SBERT_MODEL_PATH', 'sentence-transformers/all-MiniLM-L6-v2'))
except Exception as e:
    logger.error(f"Error loading SBERT model: {e}") # Use logger
    sbert_model = None # 모델 로드 실패 시 None으로 설정

def generate_embedding(text: str):
    """
    텍스트를 입력받아 SBERT 임베딩 벡터를 반환합니다.
    """
    if not sbert_model:
        logger.warning("SBERT model not loaded. Cannot generate embedding.") # Use logger
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

def generate_match_explanation(user_data: dict, project_data: dict, similarity_score: float):
    """
    OpenAI API를 사용하여 사용자 프로필과 프로젝트 정보 기반으로 매칭 설명을 생성하고,
    세부 점수를 포함한 JSON을 반환합니다.
    """
    api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        logger.warning("OPENAI_API_KEY is not set.")
        return None

    client = OpenAI(
        api_key=api_key,
        http_client=httpx.Client(trust_env=False)
    )

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
  "tech_score": <기술 매칭 점수 (0-30 사이 정수)>,
  "personality_score": <성향 적합도 점수 (0-25 사이 정수)>,
  "experience_score": <경험 수준 점수 (0-20 사이 정수)>,
  "explanation": "<종합 설명 텍스트>"
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes the match between a user and a project and returns the result in JSON format."},
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


from teamspace.models import User, Projects, UserEmbedding, ProjectEmbedding, MatchScores

class MatchService:
    @staticmethod
    def get_or_create_match_score(user: User, project: Projects):
        logger.info(f"Attempting to get or create match score for user {user.email} and project {project.title}")
        match_score_entry, created = MatchScores.objects.get_or_create(
            user=user, project=project,
            defaults={'score': 0.0, 'explanation': ''}
        )

        if not created and match_score_entry.explanation and match_score_entry.score != 0.0:
            logger.info(f"Match score already exists and is valid for user {user.email} and project {project.title}. Returning existing entry.")
            return match_score_entry

        # 임베딩이 없는 경우 처리
        try:
            user_embedding_obj = UserEmbedding.objects.get(user=user)
            project_embedding_obj = ProjectEmbedding.objects.get(project=project)
        except (UserEmbedding.DoesNotExist, ProjectEmbedding.DoesNotExist) as e:
            logger.warning(f"Embedding missing for user {user.email} or project {project.title}: {e}")
            match_score_entry.score = 0.0
            match_score_entry.explanation = "임베딩이 생성되지 않아 매칭 점수를 계산할 수 없습니다."
            match_score_entry.save()
            return match_score_entry

        user_embedding = user_embedding_obj.embedding


        
        project_embedding = project_embedding_obj.embedding

        if user_embedding and project_embedding:
            score = calculate_similarity(user_embedding, project_embedding) * 100 # 백분율로 변환
            match_score_entry.score = round(score, 2)

            # 매칭 설명 생성 (여기서는 간단히 사용자/프로필 데이터를 넘김)
            # 실제로는 더 상세한 데이터를 넘겨야 정확한 설명이 가능
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
            logger.info(f"Calculated score {match_score_entry.score}% and explanation for user {user.email} and project {project.title}. Created: {created}")
        else:
            match_score_entry.score = 0.0
            match_score_entry.explanation = "임베딩 데이터가 유효하지 않아 매칭 점수를 계산할 수 없습니다."
            logger.warning(f"Invalid embedding data for user {user.email} or project {project.title}")
        
        match_score_entry.save()
        return match_score_entry

    @staticmethod
    def get_user_project_match(user: User, project: Projects):
        """
        특정 사용자와 프로젝트 간의 매칭 점수 및 설명을 반환합니다.
        없으면 새로 계산하여 반환합니다.
        """
        return MatchService.get_or_create_match_score(user, project)

    @staticmethod
    def get_recommended_projects(user: User):
        logger.info(f"MatchService: Getting recommended projects for user {user.email}")
        all_projects = Projects.objects.filter(is_open=True) # 열려있는 프로젝트만 대상으로
        recommended_projects_data = []

        for project in all_projects:
            match_score_entry = MatchService.get_or_create_match_score(user, project)
            recommended_projects_data.append({
                'project': project,
                'score': match_score_entry.score,
                'explanation': match_score_entry.explanation
            })
        
        # 점수가 높은 순서대로 정렬
        recommended_projects_data.sort(key=lambda x: x['score'], reverse=True)
        logger.info(f"MatchService: Found {len(recommended_projects_data)} recommended projects for user {user.email}")
        
        return recommended_projects_data 