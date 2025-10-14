# teamspace/management/commands/seed_dummy.py

import os
import re
import random
import hashlib
import time
from datetime import date, timedelta
from typing import List, Tuple, Dict, Optional

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone
from faker import Faker

# ---------------------------------
# 전역 설정
# ---------------------------------
DEFAULT_USERS = 50
DEFAULT_PROJECTS = 10
DEFAULT_TEAMS = 8

# --- Data constants aligned with web app ---
KOREAN_REGIONS_CHOICES = [
    ('SEOUL', '서울특별시'), ('BUSAN', '부산광역시'), ('DAEGU', '대구광역시'),
    ('INCHEON', '인천광역시'), ('GWANGJU', '광주광역시'), ('DAEJEON', '대전광역시'),
    ('ULSAN', '울산광역시'), ('SEJONG', '세종특별자치시'), ('GYEONGGI', '경기도'),
    ('GANGWON', '강원도'), ('CHUNGCHEONGBUK', '충청북도'), ('CHUNGCHEONGNAM', '충청남도'),
    ('JEOLLABUK', '전라북도'), ('JEOLLANAM', '전라남도'), ('GYEONGSANGBUK', '경상북도'),
    ('GYEONGSANGNAM', '경상남도'), ('JEJU', '제주특별자치도'),
]
MAJOR_CHOICES = [
    ('PROGRAMMING', '개발/프로그래밍'), ('DATA_AI', '데이터/AI'),
    ('SECURITY_NET', '보안/네트워크'), ('DESIGN', '디자인/기획'),
    ('NON_MAJOR', '비전공자/기타')
]
SPECIALTY_CHOICES = [
    ('frontend', '프론트엔드'), ('backend', '백엔드'), ('ai', 'AI/머신러닝'),
    ('app', '앱 개발'), ('game', '게임 개발'), ('data', '데이터 분석'),
    ('UX', 'UX/UI 디자인'), ('PM', '기획/PM'), ('security', '정보보안')
]
TECH_STACK_CHOICES = [
    ('React', 'React'), ('Vue', 'Vue'), ('HTML/CSS/JS', 'HTML/CSS/JS'),
    ('Django', 'Django'), ('Flask', 'Flask'), ('Node.js', 'Node.js'),
    ('Java', 'Java'), ('Spring', 'Spring'), ('Python', 'Python'),
    ('C/C++', 'C/C++'), ('Kotlin', 'Kotlin'), ('Swift', 'Swift'),
    ('TensorFlow', 'TensorFlow'), ('PyTorch', 'PyTorch'), ('MySQL', 'MySQL'),
    ('MongoDB', 'MongoDB'), ('Other', '기타')
]
COLLAB_TOOL_CHOICES = [
    ('Git', 'Git'), ('GitHub', 'GitHub'), ('Notion', 'Notion'),
    ('Figma', 'Figma'), ('Slack', 'Slack'), ('Discord', 'Discord'),
    ('Jira', 'Jira'), ('Trello', 'Trello')
]
PROJECT_TOPIC_CHOICES = [
    ('web', '웹 서비스'), ('app', '앱 개발'), ('ai', '인공지능'),
    ('chatbot', '챗봇'), ('social', '소셜 미디어'), ('community', '커뮤니티'),
    ('healthcare', '헬스케어'), ('education', '교육'), ('finance', '금융'),
    ('other', '기타')
]
EXPERIENCE_CHOICES = [('NONE', '없음'), ('ONCE', '1회'), ('FEW', '2~3회'), ('MANY', '4회 이상')]
COLLABORATION_STYLE_CHOICES = [('OFFLINE', '오프라인 중심'), ('ONLINE', '온라인 중심'), ('HYBRID', '혼합')]
MEETING_FREQUENCY_CHOICES = [('WEEKLY_1', '주 1회'), ('WEEKLY_2_3', '주 2~3회'), ('DAILY', '매일 가능'), ('PROJECT_ONLY', '프로젝트 중심만 가능')]
BELBIN_CHOICES = [('PL', 'PL'), ('RI', 'RI'), ('CO', 'CO'), ('SH', 'SH'), ('ME', 'ME'), ('TW', 'TW'), ('IMP', 'IMP'), ('CF', 'CF'), ('SP', 'SP')]
TEAM_SIZE_CHOICES = [('SMALL', '2~3명'), ('MEDIUM', '4~5명'), ('LARGE', '6명 이상도 가능/기타')]
AVAILABILITY_CHOICES = [('SHORT', '단기: 1달 이내'), ('MEDIUM', '중기: 2~3달'), ('LONG', '장기: 3달 이상/기타')]

DEFAULT_SKILLS = [item[0] for item in TECH_STACK_CHOICES if item[0] != 'Other']

fake = Faker("ko_KR")
Faker.seed(42)
random.seed(42)

# ===== Persona & Consistent Sampling =====
PERSONAS = {
    "frontend_dev": {
        "major_pool": ['PROGRAMMING', 'DESIGN', 'NON_MAJOR'],
        "specialty_pool": ['frontend', 'app'],
        "skills_core": ["React", "TypeScript", "JavaScript", "HTML/CSS/JS"],
        "skills_opt": ["Vue", "Next.js", "Figma"],
        "experience_pool": ['ONCE', 'FEW'],
        "collab_pool": ['ONLINE', 'HYBRID'],
        "meet_pool": ['WEEKLY_1', 'WEEKLY_2_3'],
        "topics_pool": ['web', 'app', 'community']
    },
    "backend_devops": {
        "major_pool": ['PROGRAMMING', 'SECURITY_NET'],
        "specialty_pool": ['backend', 'security'],
        "skills_core": ["Python", "Django", "Node.js", "MySQL", "Docker", "AWS"],
        "skills_opt": ["PostgreSQL", "Redis", "Kubernetes"],
        "experience_pool": ['FEW', 'MANY'],
        "collab_pool": ['HYBRID', 'OFFLINE'],
        "meet_pool": ['WEEKLY_2_3', 'DAILY'],
        "topics_pool": ['web', 'ai', 'chatbot']
    },
    "ml_engineer": {
        "major_pool": ['PROGRAMMING', 'DATA_AI', 'NON_MAJOR'],
        "specialty_pool": ['ai', 'data'],
        "skills_core": ["Python", "TensorFlow", "PyTorch", "scikit-learn"],
        "skills_opt": ["Docker", "AWS", "OpenCV"],
        "experience_pool": ['ONCE', 'FEW', 'MANY'],
        "collab_pool": ['ONLINE', 'HYBRID'],
        "meet_pool": ['WEEKLY_1', 'WEEKLY_2_3'],
        "topics_pool": ['ai', 'chatbot', 'healthcare']
    },
    "uxui_designer": {
        "major_pool": ['DESIGN', 'NON_MAJOR'],
        "specialty_pool": ['UX', 'PM'],
        "skills_core": ["Figma"],
        "skills_opt": ["Notion", "Jira"],
        "experience_pool": ['ONCE', 'FEW'],
        "collab_pool": ['ONLINE', 'HYBRID'],
        "meet_pool": ['WEEKLY_1', 'WEEKLY_2_3'],
        "topics_pool": ['web', 'app', 'education']
    }
}

PROJECT_TEMPLATES = [
    {
        "topic": "AI 맛집 추천 챗봇",
        "tech_stack": ["Python", "Django", "TensorFlow", "React", "MySQL"],
        "roles": {"백엔드 개발자": 2, "프론트엔드 개발자": 1, "AI 모델러": 1},
        "duration_months": 3
    },
    {
        "topic": "실시간 스터디 그룹 매칭 플랫폼",
        "tech_stack": ["Node.js", "React", "TypeScript", "MongoDB", "Redis"],
        "roles": {"백엔드 개발자": 1, "프론트엔드 개발자": 2},
        "duration_months": 2
    },
    {
        "topic": "반려동물 산책 경로 공유 앱",
        "tech_stack": ["Kotlin", "Swift", "Spring", "Java", "PostgreSQL"],
        "roles": {"안드로이드 개발자": 1, "iOS 개발자": 1, "백엔드 개발자": 1},
        "duration_months": 4
    },
    {
        "topic": "VR/AR 기반 인테리어 시뮬레이터",
        "tech_stack": ["C/C++", "Python"], # Simplified for seeding
        "roles": {"VR/AR 개발자": 2, "3D 모델러": 1, "기획자": 1},
        "duration_months": 6
    }
]

# ---------------------------
# 공용 유틸
# ---------------------------
def sample_user_from_persona(p: dict) -> dict:
    pack = {}
    pack["major"] = random.choice(p["major_pool"])
    pack["specialty"] = ",".join(random.sample(p["specialty_pool"], random.randint(1, len(p["specialty_pool"]))))
    
    core_k = min(len(p["skills_core"]), random.randint(1, len(p["skills_core"])))
    opt_k = min(len(p["skills_opt"]), random.randint(0, len(p["skills_opt"])))
    skills = random.sample(p["skills_core"], core_k) + random.sample(p["skills_opt"], opt_k)
    pack["tech_stack"] = ",".join(list(set(skills)))

    pack["experience_level"] = random.choice(p["experience_pool"])
    pack["collaboration_style"] = random.choice(p["collab_pool"])
    pack["meeting_frequency"] = random.choice(p["meet_pool"])
    pack["preferred_project_topics"] = ",".join(random.sample(p["topics_pool"], random.randint(1, len(p["topics_pool"]))))

    return pack

# ---------------------------------
# 헬퍼 함수 (클래스 밖)
# ---------------------------------
def rand_birth(min_age=18, max_age=40) -> date:
    today = date.today()
    age = random.randint(min_age, max_age)
    start = date(today.year - age, 1, 1)
    end = date(today.year - age, 12, 28)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def executemany(cur, sql: str, rows: List[Tuple]):
    if rows:
        cur.executemany(sql, rows)

# ---------------------------------
# 메인 커맨드
# ---------------------------------
class Command(BaseCommand):
    help = "sideproj 스키마 더미데이터 생성"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=DEFAULT_USERS, help="생성할 사용자 수")
        parser.add_argument("--projects", type=int, default=DEFAULT_PROJECTS, help="생성할 프로젝트 수")
        parser.add_argument("--teams", type=int, default=DEFAULT_TEAMS, help="생성할 팀 수")
        parser.add_argument("--flush", action="store_true", help="모든 테이블 데이터를 비우고 시작(TRUNCATE)")
        parser.add_argument("--skip-deep", action="store_true", help="Users/Skills/UserSkills까지만 생성(빠른 테스트용)")
        parser.add_argument("--use-llm", action="store_true", help="LLM을 사용하여 자기소개 생성")
        # parser.add_argument("--llm-intro", action="store_true", help="LLM을 사용하여 자기소개 생성 (use-llm과 동일)")
        parser.add_argument("--llm-free", action="store_true", help="LLM을 사용하여 프로젝트 소개 자유 생성")

    @transaction.atomic
    def handle(self, *args, **opts):
        users_n = opts["users"]
        projects_n = opts["projects"]
        teams_n = opts["teams"]
        do_flush = opts["flush"]
        skip_deep = opts["skip_deep"]
        self.use_llm = opts["use_llm"] or opts["llm_intro"]
        self.llm_free = opts["llm_free"]

        self.stdout.write(self.style.NOTICE("[seed_sideproj] START"))

        with connection.cursor() as cur:
            if do_flush:
                self._flush_all(cur)

            skill_ids = self._ensure_skills(cur)

            user_ids, user_skill_names_by_uid = self._create_users(cur, users_n)
            cur.execute("SELECT skill_id, name FROM Skills;")
            name_to_id = {name: sid for (sid, name) in cur.fetchall()}
            self._create_user_skills_from_names(cur, user_skill_names_by_uid, name_to_id)

            if not skip_deep:
                project_ids = self._create_projects(cur, projects_n, user_ids)
                team_ids = self._create_teams(cur, teams_n, project_ids)
                self._create_team_members(cur, team_ids, user_ids)
                self._create_match_scores(cur, user_ids, project_ids)
                self._create_evaluations(cur, team_ids, user_ids)
                self._create_portfolios(cur, user_ids, project_ids)

        self.stdout.write(self.style.SUCCESS("[seed_sideproj] DONE"))

    def _flush_all(self, cur):
        self.stdout.write("Dropping all data (FK 순서 유의)…")
        cur.execute("SET FOREIGN_KEY_CHECKS=0;")
        tables = [
            "Portfolios", "Evaluations", "MatchScores", "TeamMembers",
            "Teams", "Projects", "UserSkills", "Skills", "UserEmbeddings", 
            "ProjectEmbeddings", "Users"
        ]
        for tbl in tables:
            try:
                cur.execute(f"TRUNCATE TABLE {tbl};")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Could not truncate {tbl}: {e}'))
        cur.execute("SET FOREIGN_KEY_CHECKS=1;")
        self.stdout.write(self.style.WARNING("All tables truncated."))

    def _ensure_skills(self, cur) -> List[int]:
        self.stdout.write("Seeding Skills…")
        existing = set()
        cur.execute("SELECT name FROM Skills;")
        for (name,) in cur.fetchall():
            existing.add(name)

        rows = [(name,) for name in DEFAULT_SKILLS if name not in existing]
        executemany(cur, "INSERT INTO Skills (name) VALUES (%s)", rows)

        cur.execute("SELECT skill_id FROM Skills;")
        return [sid for (sid,) in cur.fetchall()]

    def _llm_generate_user_intro(self, pack_for_prompt: dict) -> Optional[str]:
        try:
            from openai import OpenAI
            import httpx
        except ImportError:
            self.stdout.write(self.style.WARNING("[LLM] openai 또는 httpx 패키지가 없어 자기소개 폴백 사용"))
            return None

        prompt = f"""
        너는 IT 프로젝트 팀 매칭 플랫폼의 사용자 프로필 자기소개 문구를 작성하는 AI야.
        다음 정보를 바탕으로, 한국어로 2~3문장의 자연스러운 자기소개를 만들어줘.

        [사용자 정보]
        - 주요 전공: {pack_for_prompt.get("major", "")}
        - 전문 분야: {pack_for_prompt.get("specialty", "")}
        - 기술 스택: {pack_for_prompt.get("tech_stack", "")}
        - 숙련도: {pack_for_prompt.get("experience_level", "")}

        [작성 규칙]
        - '안녕하세요'로 시작하지마.
        - '저는' 이나 '입니다' 같은 단조로운 표현 대신, 자신을 어필하는 개성있는 문장으로 작성해줘.
        - 모든 정보를 나열하지 말고, 2~3가지 핵심 정보만 자연스럽게 엮어서 표현해줘.
        - 숙련도에 따라 문장의 톤과 내용을 조절해줘. 예를 들어, 숙련도가 높으면 자신감 있고 전문적인 느낌으로, 낮으면 배우려는 의지가 드러나게 작성해줘.
        - 결과는 자기소개 문단 텍스트만 출력해줘. (따옴표나 다른 마크다운 없이)
        """.strip()

        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                self.stdout.write(self.style.WARNING("[LLM] OPENAI_API_KEY가 없어 자기소개 폴백 사용"))
                return None

            client = OpenAI(api_key=api_key, http_client=httpx.Client())
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=1.1, top_p=0.9, presence_penalty=0.4, frequency_penalty=0.4,
            )
            text = (resp.choices[0].message.content or "").strip()
            return text if text else None
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"[LLM] intro 생성 예외 → 폴백: {e}"))
            return None

    def _llm_generate_project_free(self, template: dict) -> Optional[tuple]:
        try:
            from openai import OpenAI
            import httpx
        except ImportError:
            self.stdout.write(self.style.WARNING("[LLM] openai 또는 httpx 패키지가 없어 프로젝트 폴백 사용"))
            return None

        roles_text = ", ".join([f"{role} {num}명" for role, num in template["roles"].items()])
        duration_text = f'{template["duration_months"]}개월'
        tech_stack_text = ", ".join(template["tech_stack"])

        prompt = f"""
        너는 IT 프로젝트 팀 매칭 플랫폼의 프로젝트 모집 공고를 작성하는 AI야.
        다음 정보를 참고해서, 사용자들이 참여하고 싶게 만드는 매력적인 프로젝트 공고를 만들어줘.

        [프로젝트 정보]
        - 주제: {template["topic"]}
        - 모집 역할: {roles_text}
        - 예상 기간: {duration_text}
        - 주요 기술 스택: {tech_stack_text}

        [작성 규칙]
        - 첫 줄에는 프로젝트의 핵심을 담은 강렬한 제목만 작성해줘.
        - 본문에는 프로젝트에 대한 설명, 목표, 사용하는 기술, 찾는 팀원에 대해 자유롭게 서술해줘.
        - 마지막 줄은 반드시 "목표: [여기에 목표 입력]" 형식으로 끝나야 해.
        - 결과는 제목, 본문, 목표가 포함된 전체 텍스트로 출력해줘.
        """.strip()

        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                self.stdout.write(self.style.WARNING("[LLM] OPENAI_API_KEY가 없어 프로젝트 폴백 사용"))
                return None

            client = OpenAI(api_key=api_key, http_client=httpx.Client())
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9, top_p=1.0,
            )
            text = (resp.choices[0].message.content or "").strip()
            if not text:
                return None

            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            if not lines:
                return None

            title = lines[0][:100]
            goal_line = ""
            for ln in reversed(lines):
                if ln.startswith("목표:"):
                    goal_line = ln
                    break
            
            if goal_line:
                body = "\n".join([ln for ln in lines[1:] if ln != goal_line]).strip()
                goal = goal_line
            else:
                body = "\n".join(lines[1:]).strip()
                goal = f"목표: {duration_text} 내 MVP 출시"

            return (title, body, goal)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"[LLM] 프로젝트 생성 예외 → 폴백: {e}"))
            return None

    def _create_users(self, cur, n_users: int) -> Tuple[List[int], dict]:
        self.stdout.write(f"Seeding Users x {n_users}…")
        
        now = timezone.now()
        staged_users = []
        persona_keys = list(PERSONAS.keys())
        
        major_map = dict(MAJOR_CHOICES)
        specialty_map = dict(SPECIALTY_CHOICES)
        experience_map = dict(EXPERIENCE_CHOICES)
        collab_style_map = dict(COLLABORATION_STYLE_CHOICES)
        meeting_freq_map = dict(MEETING_FREQUENCY_CHOICES)
        topic_map = dict(PROJECT_TOPIC_CHOICES)

        region_ids = [r[0] for r in KOREAN_REGIONS_CHOICES]
        collab_tool_ids = [c[0] for c in COLLAB_TOOL_CHOICES]
        belbin_ids = [b[0] for b in BELBIN_CHOICES]
        team_size_ids = [t[0] for t in TEAM_SIZE_CHOICES]
        availability_ids = [a[0] for a in AVAILABILITY_CHOICES]

        for i in range(n_users):
            p_key = random.choice(persona_keys)
            pack = sample_user_from_persona(PERSONAS[p_key])

            name = fake.name()
            # Generate a unique email that is very unlikely to collide across runs
            email = f"{fake.unique.user_name()}{int(time.time())}{i}@example.com"
            pw = sha256_hex('password123')
            birth = rand_birth()
            
            available_region = ",".join(random.sample(region_ids, random.randint(1, 3)))
            collaboration_tools = ",".join(random.sample(collab_tool_ids, random.randint(2, 4)))
            belbin_role = random.choice(belbin_ids)
            preferred_team_size = random.choice(team_size_ids)
            availability_period = random.choice(availability_ids)
            
            intro = None
            if self.use_llm:
                pack_for_prompt = {
                    "major": major_map.get(pack["major"], ""),
                    "specialty": ", ".join([specialty_map.get(s, "") for s in pack["specialty"].split(",")]),
                    "tech_stack": pack["tech_stack"],
                    "collaboration_style": collab_style_map.get(pack["collaboration_style"], ""),
                    "meeting_frequency": meeting_freq_map.get(pack["meeting_frequency"], ""),
                    "preferred_project_topics": ", ".join([topic_map.get(t, "") for t in pack["preferred_project_topics"].split(",")]),
                    "experience_level": experience_map.get(pack["experience_level"], ""),
                }
                intro = self._llm_generate_user_intro(pack_for_prompt)

            if not intro:
                major_label = major_map.get(pack["major"], "")
                specialty_labels = [specialty_map.get(s, "") for s in pack["specialty"].split(",")]
                intro = f'{major_label} 전공, {specialty_labels[0]} 분야 전문가입니다. {pack["tech_stack"]} 기술을 활용하여 멋진 프로젝트를 만들고 싶습니다.'

            github_url = f"https://github.com/{fake.user_name()}"
            portfolio_url = fake.url()
            is_profile_complete = True
            last_login = now

            staged_users.append((
                { "skills": pack["tech_stack"].split(',') },
                (
                    name, birth, email, pw, intro, now,
                    available_region, github_url, portfolio_url,
                    pack["major"], pack["specialty"], pack["tech_stack"], collaboration_tools,
                    pack["experience_level"], pack["collaboration_style"], pack["meeting_frequency"],
                    belbin_role, preferred_team_size, pack["preferred_project_topics"],
                    availability_period, is_profile_complete, last_login
                )
            ))

        user_rows = [d + (0, 1, 0) for _, d in staged_users]
        executemany(
            cur,
            """
            INSERT INTO Users (
                name, birthdate, email, password, introduction, created_at,
                available_region, github_url, portfolio_url,
                major, specialty, tech_stack, collaboration_tools,
                experience_level, collaboration_style, meeting_frequency,
                belbin_role, preferred_team_size, preferred_project_topics,
                availability_period, is_profile_complete, last_login,
                is_staff, is_active, is_superuser
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            user_rows,
        )

        cur.execute("SELECT user_id FROM Users ORDER BY user_id DESC LIMIT %s;", [len(user_rows)])
        inserted_ids_desc = [uid for (uid,) in cur.fetchall()]
        inserted_ids = list(reversed(inserted_ids_desc))

        user_skill_names_by_uid: Dict[int, List[str]] = {}
        for uid, (pack, _d) in zip(inserted_ids, staged_users):
            user_skill_names_by_uid[uid] = pack.get("skills", [])

        return inserted_ids, user_skill_names_by_uid

    def _create_user_skills_from_names(self, cur, user_skill_names_by_uid: dict, name_to_id: dict):
        self.stdout.write("Seeding UserSkills…")
        rows = []
        PROF_LEVELS = ["Beginner", "Intermediate", "Advanced"]
        for uid, names in user_skill_names_by_uid.items():
            unique_sids: List[int] = []
            for nm in names:
                sid = name_to_id.get(nm)
                if sid and sid not in unique_sids:
                    unique_sids.append(sid)
            for sid in unique_sids:
                rows.append((uid, sid, random.choice(PROF_LEVELS)))
        executemany(
            cur,
            "INSERT IGNORE INTO UserSkills (user_id, skill_id, proficiency_level) VALUES (%s, %s, %s)",
            rows,
        )

    def _create_projects(self, cur, n_projects: int, user_ids: List[int]):
        if n_projects <= 0 or not user_ids:
            self.stdout.write(self.style.WARNING("[skip] projects: n_projects<=0 or missing users"))
            return []

        self.stdout.write(f"Seeding Projects x {n_projects}…")
        rows = []
        now = timezone.now()

        for _ in range(n_projects):
            template = random.choice(PROJECT_TEMPLATES)
            creator = random.choice(user_ids)

            title, desc, goal = None, None, None

            if self.llm_free:
                self.stdout.write(self.style.NOTICE("[LLM] 프로젝트 LLM 생성 시도…"))
                llm_pack = self._llm_generate_project_free(template)
                if llm_pack:
                    title, desc, goal = llm_pack

            roles_text = ", ".join([f"{role} {num}명" for role, num in template["roles"].items()])
            if not title:
                title = template["topic"]
            if not desc:
                desc = f'''저희와 함께 "{title}" 프로젝트를 만들어갈 팀원을 모집합니다.\n\n**모집 분야**\n{roles_text}'''
            if not goal:
                goal = f"{template['duration_months']}개월 내 MVP 출시를 목표로 합니다."

            tech_stack = ",".join(template["tech_stack"])
            recruitment_count = sum(template["roles"].values())

            start_date = (now + timedelta(days=random.randint(15, 45))).date()
            end_date = start_date + timedelta(days=template["duration_months"] * 30)
            application_deadline = start_date - timedelta(days=random.randint(1, 15))

            is_open = True
            
            rows.append((creator, title, desc, goal, tech_stack, recruitment_count, start_date, end_date, application_deadline, is_open, now))

        executemany(
            cur,
            """
            INSERT INTO Projects (creator_id, title, description, goal, tech_stack, recruitment_count, start_date, end_date, application_deadline, is_open, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            rows,
        )
        cur.execute("SELECT project_id FROM Projects;")
        return [pid for (pid,) in cur.fetchall()]

    def _create_teams(self, cur, n_teams: int, project_ids: List[int]) -> List[int]:
        if n_teams <= 0 or not project_ids:
            self.stdout.write(self.style.WARNING("[skip] teams: n_teams<=0 or no projects"))
            return []

        self.stdout.write(f"Seeding Teams x {n_teams}…")
        rows = []
        now = timezone.now()
        for _ in range(n_teams):
            proj = random.choice(project_ids)
            rows.append((proj, now))
        executemany(cur, "INSERT INTO Teams (project_id, created_at) VALUES (%s, %s)", rows)
        cur.execute("SELECT team_id FROM Teams;")
        return [tid for (tid,) in cur.fetchall()]

    def _create_team_members(self, cur, team_ids: List[int], user_ids: List[int]):
        if not team_ids or not user_ids:
            self.stdout.write(self.style.WARNING("[skip] team members: no teams or users"))
            return

        self.stdout.write("Seeding TeamMembers… (팀당 3~6명)")
        rows = []
        now = timezone.now()
        TEAM_ROLES = ["Leader", "Backend", "Frontend", "Designer", "Planner", "Data"]
        for tid in team_ids:
            mcount = min(len(user_ids), random.randint(3, 6))
            if mcount < 1:
                continue
            members = random.sample(user_ids, mcount)
            for idx, uid in enumerate(members):
                role = TEAM_ROLES[0] if idx == 0 else random.choice(TEAM_ROLES[1:])
                rows.append((tid, uid, role, now))
        executemany(
            cur,
            "INSERT IGNORE INTO TeamMembers (team_id, user_id, role, joined_at) VALUES (%s, %s, %s, %s)",
            rows,
        )

    def _create_match_scores(self, cur, user_ids: List[int], project_ids: List[int]):
        if not user_ids or not project_ids:
            self.stdout.write(self.style.WARNING("[skip] match scores: no users/projects"))
            return

        self.stdout.write("Seeding MatchScores… (유저 일부 x 프로젝트 일부)")
        rows = []
        now = timezone.now()
        sample_users = random.sample(user_ids, min(200, len(user_ids)))
        sample_projects = random.sample(project_ids, min(100, len(project_ids)))

        if not sample_projects:
            self.stdout.write(self.style.WARNING("[skip] match scores: sample_projects empty"))
            return

        for uid in sample_users:
            max_targets = min(8, len(sample_projects))
            if max_targets <= 0:
                continue
            targets = random.sample(sample_projects, random.randint(1, max_targets))
            for pid in targets:
                score = round(random.uniform(20.0, 98.0), 2)
                # Provide default values for new score fields and explanation
                rows.append((uid, pid, score, 0, 0, 0, "", now))
        executemany(
            cur,
            """INSERT INTO MatchScores (user_id, project_id, score, tech_score, personality_score, experience_score, explanation, evaluated_at) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            rows,
        )

    def _create_evaluations(self, cur, team_ids: List[int], user_ids: List[int]):
        if not team_ids:
            self.stdout.write(self.style.WARNING("[skip] evaluations: no teams"))
            return
        if not user_ids:
            self.stdout.write(self.style.WARNING("[skip] evaluations: no users"))
            return

        self.stdout.write("Seeding Evaluations… (팀 내 상호 평가 소량)")
        rows = []
        now = timezone.now()

        k = max(1, len(team_ids) // 3)
        k = min(k, len(team_ids))
        pick_teams = random.sample(team_ids, k) if k > 0 else []

        for tid in pick_teams:
            member_count = min(len(user_ids), random.randint(3, 5))
            if member_count < 2:
                continue
            members = random.sample(user_ids, member_count)
            for evaluator in members:
                for evaluatee in members:
                    if evaluator == evaluatee:
                        continue
                    score = random.randint(3, 5)
                    feedback = fake.sentence(nb_words=12)
                    rows.append((evaluator, evaluatee, tid, score, feedback, now))
        executemany(
            cur,
            """
            INSERT INTO Evaluations (evaluator_id, evaluatee_id, team_id, score, feedback, evaluated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            rows,
        )

    def _create_portfolios(self, cur, user_ids: List[int], project_ids: List[int]):
        if not user_ids or not project_ids:
            self.stdout.write(self.style.WARNING("[skip] portfolios: no users/projects"))
            return

        self.stdout.write("Seeding Portfolios… (사용자 일부)")
        rows = []
        now = timezone.now()
        for uid in random.sample(user_ids, min(200, len(user_ids))):
            num_portfolios = random.randint(0, 2)
            if num_portfolios == 0:
                continue
            
            user_project_ids = random.sample(project_ids, min(num_portfolios, len(project_ids)))

            for pid in user_project_ids:
                desc = fake.sentence(nb_words=12)
                url = f"https://github.com/{fake.user_name()}/{fake.word()}"
                rows.append((uid, pid, desc, url, now))
        executemany(
            cur,
            """
            INSERT IGNORE INTO Portfolios (user_id, project_id, description, url, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            rows,
        )
