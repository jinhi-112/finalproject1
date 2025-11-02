# management/commands/rerank_with_gpt.py
import json
from django.core.management.base import BaseCommand
from django.db import connection

def call_gpt_json(system_prompt: str, user_prompt: str):
    # TODO: 실제 GPT 호출로 교체. 반드시 JSON을 반환하도록 모델 설정/프롬프트.
    raise NotImplementedError

class Command(BaseCommand):
    help = "Top-K 후보를 GPT로 리랭킹하고 이유(설명) 생성"

    def add_arguments(self, parser):
        parser.add_argument("--user", type=int, required=True)
        parser.add_argument("--k", type=int, default=50)
        parser.add_argument("--n", type=int, default=10)

    def handle(self, *args, **opts):
        user_id = opts["user"]; K = opts["k"]; N = opts["n"]

        with connection.cursor() as cur:
            # 사용자 요약
            cur.execute("""
                SELECT experience_level, collaboration_style, meeting_frequency,
                       preferred_project_topics, tech_stack
                FROM Users WHERE user_id=%s
            """, [user_id])
            ue = cur.fetchone()
            if not ue:
                self.stderr.write("해당 사용자 없음")
                return
            exp, style, freq, topics, stack = ue
            user_profile = {
                "experience_level": exp, "collaboration_style": style,
                "meeting_frequency": freq, "preferred_topics": topics, "tech_stack": stack
            }

            # 추천 후보(K)는 recommend_topk.py 결과를 DB에 쓰지 않으므로 여기서 간이 계산:
            cur.execute("""
                SELECT e.entity_id AS project_id, e.vector
                FROM Embeddings e
                WHERE e.entity_type='project'
            """)
            projects_vec = cur.fetchall()
            cur.execute("SELECT vector FROM Embeddings WHERE entity_type='user' AND entity_id=%s", [user_id])
            uv = cur.fetchone()
            if not uv:
                self.stderr.write("임베딩 먼저 생성하세요(build_embeddings).")
                return

        # 여기서는 성능보다 파이프라인 데모에 집중—상단 recommend_topk.py를 먼저 돌려 후보 pid K개 리스트를 받아온 다음
        # 그 리스트로 아래 메타를 모아 GPT에 보내는 흐름을 권장합니다.
        # 간소화를 위해 'Projects'에서 메타를 모으는 예시만 보여줄게.

        with connection.cursor() as cur:
            cur.execute("""
              SELECT project_id, title, tech_stack
              FROM Projects
              ORDER BY project_id DESC
              LIMIT %s
            """, [K])
            cand = [{"project_id": pid, "title": t, "tech_stack": s} for (pid, t, s) in cur.fetchall()]

        system_prompt = (
            "You are a ranking assistant for user–project matching.\n"
            "- Return strict JSON only. No extra text.\n"
            "- Consider skill overlap first, then textual relevance (title), then preferences.\n"
        )
        user_prompt = json.dumps({
            "user_profile": user_profile,
            "candidates": cand,
            "top_n": N
        }, ensure_ascii=False)

        raw = call_gpt_json(system_prompt, user_prompt)
        result = json.loads(raw)  # [{"project_id": int, "score": float, "reasons": ["..",".."]}, ...]
        print(json.dumps(result, ensure_ascii=False, indent=2))
