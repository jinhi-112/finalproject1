# management/commands/seed_llm_projects.py
import json, random, re
from typing import List, Dict
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

# ===== ❶ 여기를 실제 API로 교체하세요 (OpenAI/Anthropic 등) =====
def call_llm(system_prompt: str, user_prompt: str) -> str:
    # 예: OpenAI Responses API 사용 시
    # from openai import OpenAI
    # client = OpenAI()
    # resp = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}],
    #     temperature=0.8
    # )
    # return resp.choices[0].message.content
    raise NotImplementedError("LLM API 연결을 구현하세요.")

class Command(BaseCommand):
    help = "LLM으로 의미 있는 프로젝트 더미 생성 (Projects + ProjectSkills)"

    def add_arguments(self, parser):
        parser.add_argument("--n", type=int, default=100, help="생성할 프로젝트 수")

    def handle(self, *args, **opts):
        n = opts["n"]
        with connection.cursor() as cur:
            cur.execute("SELECT skill_id, name FROM Skills")
            id_by_name = {name: sid for (sid, name) in cur.fetchall()}
            allowed = list(id_by_name.keys())

            cur.execute("SELECT user_id FROM Users")
            user_ids = [uid for (uid,) in cur.fetchall()]

        system_prompt = (
            "너는 사이드 프로젝트 기획 더미 데이터를 생성하는 도우미다.\n"
            "- 실제 인물/회사/연락처/PII 금지.\n"
            "- 반드시 유효한 JSON 배열만 출력(설명 금지).\n"
            "- title: 한국어 6~12 단어, description: 200~300자, goal: 1~2문장(명령형).\n"
            "- required_skills/optional_skills는 허용 스킬 목록에서만 선택.\n"
        )
        user_prompt = (
            f"[허용 스킬 목록]\n{json.dumps(allowed, ensure_ascii=False)}\n\n"
            f"[요청]\n- 총 {n}개의 프로젝트를 생성.\n"
            "[스키마]\n"
            "[\n  {\n    \"title\": \"string(KR, 6~12단어)\",\n"
            "    \"description\": \"string(KR, 200~300자)\",\n"
            "    \"goal\": \"string(KR, 1~2문장, 명령형)\",\n"
            "    \"required_skills\": [\"허용 스킬 1~5\"],\n"
            "    \"optional_skills\": [\"허용 스킬 0~4 (중복 금지)\"]\n"
            "  }\n]\n"
            "- JSON 외 텍스트 금지."
        )

        raw = call_llm(system_prompt, user_prompt)
        items = json.loads(raw)
        assert isinstance(items, list)

        # 검증/정규화
        valid = []
        for it in items:
            title = " ".join(it.get("title","").split())
            desc  = it.get("description","").strip()
            goal  = it.get("goal","").strip()

            if not (6 <= len(title.split()) <= 12): continue
            if len(title) > 100: continue
            if not (200 <= len(desc) <= 350): continue
            if not goal: continue

            req = [s for s in it.get("required_skills",[]) if s in id_by_name]
            opt = [s for s in it.get("optional_skills",[]) if s in id_by_name and s not in req]
            if not req: continue

            valid.append({
                "title": title, "description": desc, "goal": goal,
                "required_skills": req, "optional_skills": opt
            })

        if not valid:
            self.stderr.write(self.style.ERROR("유효 항목 없음. 프롬프트/스킬 목록 확인"))
            return

        # INSERT
        now = timezone.now()
        proj_rows = []
        for it in valid:
            creator = random.choice(user_ids) if user_ids else None
            tech_stack = ", ".join(it["required_skills"] + it["optional_skills"])
            proj_rows.append((creator, it["title"], it["description"], it["goal"], tech_stack, 1, now))

        with connection.cursor() as cur:
            cur.executemany("""
                INSERT INTO Projects
                (creator_id, title, description, goal, tech_stack, is_open, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, proj_rows)

            # 최신 N개 project_id 가져와 ProjectSkills 매핑
            cur.execute("SELECT project_id, title FROM Projects ORDER BY project_id DESC LIMIT %s", [len(proj_rows)])
            inserted = cur.fetchall()  # 최신 N개
            title_to_item = {it["title"]: it for it in valid}
            ps_rows = []
            for pid, title in inserted:
                it = title_to_item.get(title)
                if not it: continue
                for s in it["required_skills"]:
                    ps_rows.append((pid, id_by_name[s]))
            if ps_rows:
                cur.executemany(
                    "INSERT IGNORE INTO ProjectSkills (project_id, skill_id) VALUES (%s, %s)",
                    ps_rows
                )

        self.stdout.write(self.style.SUCCESS(f"[OK] LLM Projects inserted: {len(proj_rows)}"))