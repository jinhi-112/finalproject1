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
# settings.py에서 모델 경로를 설정합니다.
try:
    sbert_model = SentenceTransformer(getattr(settings, 'SBERT_MODEL_PATH'))
except Exception as e:
    logger.error(f"Error loading SBERT model from {getattr(settings, 'SBERT_MODEL_PATH')}: {e}")
    sbert_model = None # 모델 로드 실패 시 None으로 설정

def generate_embedding(text: str):
    """
    텍스트를 입력받아 SBERT 임베딩 벡터를 반환합니다.
    """
    if sbert_model is None:
        logger.warning("SBERT model not loaded. Cannot generate embedding.")
        return None
    if not text:
        return None
    embeddings = sbert_model.encode(text, convert_to_tensor=False) # 텐서 대신 numpy 배열로 반환
    return embeddings.tolist() # JSONField에 저장하기 위해 리스트로 변환

def calculate_similarity(embedding1: list, embedding2: list):
    """
    두 임베딩 벡터 간의 코사인 유사도를 계산합니다.
    """
    if not embedding1 or not embedding2:
        return 0.0 # 임베딩이 없으면 유사도 0 반환
    try:
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        # 코사인 유사도 계산
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
        return 0.0

def generate_match_explanation(user_data: dict, project_data: dict, similarity_score: float):
    """
    OpenAI API를 사용하여 사용자 프로필과 프로젝트 정보 기반으로 매칭 설명을 생성하고(~습니다 말투로 해줘),
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

    prompt = f"""사용자 프로필과 프로젝트 정보를 바탕으로, {similarity_score:.0f}% 라는 매칭률이 나온 이유를 상세히 분석해주세요. 모든 설명은 반드시 ‘~습니다’ 체로 정중하게 작성해주세요.

[분석 기준]
1.  **기술 매칭 (100점 만점):** 사용자의 기술 스택과 프로젝트의 기술 스택을 비교하여 점수를 매겨주세요.
2.  **성향 적합도 (100점 만점):** 사용자의 협업 스타일, 선호 주제 등과 프로젝트의 특성을 비교하여 점수를 매겨주세요.
3.  **경험 수준 (100점 만점):** 사용자의 전공, 프로젝트 경험 등과 프로젝트의 연관성을 평가하여 점수를 매겨주세요.
4.  **추천 이유 분석 (두 가지 형식으로 출력):**
    *   **추천 페이지용 (`for_recommendation_page`):**
        *   `primary_reason`: 매칭률에 가장 긍정적인 영향을 미친 핵심적인 이유 1가지를 요약해주세요. (예: 보유하신 React, Node.js 기술이 프로젝트에 완벽히 매칭됩니다.)
        *   `additional_reasons`: 그 외에 일치하는 점 1~2가지를 추가로 요약해주세요. (예: AI/ML 분야에 대한 관심사가 일치합니다.)
    *   **상세 페이지용 (`for_detail_page`):**
        *   `positive_points`: 매칭 점수에 긍정적인 영향을 준 요인을 **기술적 측면**과 **기술 외적(성향, 경험 등) 측면**에서 각각 가장 중요한 것 1가지씩, 구체적인 데이터를 근거로 상세히 설명해주세요.
        *   `negative_points`: 매칭 점수에 부정적인 영향을 준 요인들을 구체적인 데이터를 근거로 1~2가지 상세히 설명하고, 점수를 높이기 위한 조언을 포함해주세요.

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
  "explanation": {{
      "for_recommendation_page": {{
          "primary_reason": "<가장 중요한 매칭 이유 한 문장>",
          "additional_reasons": [
              "<추가적인 매칭 이유 1>",
              "<추가적인 매칭 이유 2>"
          ]
      }},
      "for_detail_page": {{
          "positive_points": [
              "<기술적 측면의 긍정적 요인 상세 설명>",
              "<기술 외적 측면의 긍정적 요인 상세 설명>"
          ],
          "negative_points": [
              "<매칭률에 부정적 영향을 미친 요인 및 조언 상세 설명 1>",
              "<매칭률에 부정적 영향을 미친 요인 및 조언 상세 설명 2>"
          ]
      }}
  }}
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


from teamspace.models import User, Projects, MatchScores

class MatchService:
    @staticmethod
    def get_or_create_match_score(user: User, project: Projects):
        logger.info(f"Attempting to get or create match score for user {user.email} and project {project.title}")
        match_score_entry, created = MatchScores.objects.get_or_create(
            user=user, project=project,
            defaults={'score': 0.0, 'explanation': {}}
        )

        # 이미 유효한 점수와 설명이 있다면 새로 계산하지 않고 즉시 반환
        if not created and match_score_entry.explanation and match_score_entry.score != 0.0:
            logger.info(f"Match score already exists and is valid for user {user.email} and project {project.title}. Returning existing entry.")
            return match_score_entry

        # 1. 사용자 및 프로젝트 데이터 분리 (기술 vs 프로필)
        user_tech_text = user.tech_stack or ""
        user_profile_text = f"{user.major or ''} {user.specialty or ''} {user.experience_level or ''} {user.preferred_project_topics or ''} {user.introduction or ''}"

        project_tech_text = project.tech_stack or ""
        project_profile_text = f"{project.title or ''} {project.description or ''} {project.goal or ''}"

        # 2. 각 부분에 대한 임베딩 생성
        user_tech_embedding = generate_embedding(user_tech_text)
        user_profile_embedding = generate_embedding(user_profile_text)
        project_tech_embedding = generate_embedding(project_tech_text)
        project_profile_embedding = generate_embedding(project_profile_text)

        # 3. 각 부분의 유사도 계산
        tech_similarity = calculate_similarity(user_tech_embedding, project_tech_embedding)
        profile_similarity = calculate_similarity(user_profile_embedding, project_profile_embedding)

        # 4. 가중 평균을 이용한 최종 점수 계산 (기술: 60%, 프로필: 40%)
        # 기본 점수 20점을 추가
        base_score = 20.0
        tech_weight = 0.6
        profile_weight = 0.4
        
        # 최종 점수 계산
        weighted_score = (tech_similarity * tech_weight + profile_similarity * profile_weight) * 100
        
        # 기본 점수를 더하되, 100점을 넘지 않도록 함
        final_score = min(base_score + weighted_score, 100.0)

        match_score_entry.score = round(final_score, 2)

        # 5. 매칭 설명 생성
        user_data = {
            "major": user.major, "specialty": user.specialty, "tech_stack": user.tech_stack,
            "experience_level": user.experience_level, "preferred_project_topics": user.preferred_project_topics,
            "collaboration_style": user.collaboration_style, "belbin_role": user.belbin_role,
        }
        project_data = {
            "title": project.title, "description": project.description,
            "goal": project.goal, "tech_stack": project.tech_stack,
        }
        
        logger.info(f"User tech_stack before explanation generation: {user.tech_stack}") # ADDED LOGGING
        logger.info(f"Generating match explanation for user {user.email} and project {project.title}")
        explanation_data = generate_match_explanation(user_data, project_data, match_score_entry.score)
        logger.info(f"Generated explanation data: {explanation_data}")
        if explanation_data:
            match_score_entry.tech_score = explanation_data.get("tech_score", 0)
            match_score_entry.personality_score = explanation_data.get("personality_score", 0)
            match_score_entry.experience_score = explanation_data.get("experience_score", 0)
            match_score_entry.explanation = explanation_data.get("explanation", {})
        else:
            match_score_entry.explanation = {
                "for_recommendation_page": {"primary_reason": "추천 이유를 생성하지 못했습니다.", "additional_reasons": []},
                "for_detail_page": {"positive_points": [], "negative_points": ["추천 이유를 생성하지 못했습니다."]}
            }
        
        logger.info(f"Calculated weighted score {match_score_entry.score}% for user {user.email} and project {project.title}. Created: {created}")
        
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
        logger.info(f"MatchService: Found {len(recommended_projects_data)} recommended projects for user {user.email}")
        
        return recommended_projects_data

     