# teamspace/management/commands/seed_dummy_large.py
# 대규모 더미데이터 생성 (기본: 사용자 500 / 프로젝트 120 / 팀 80)
# 실행: python manage.py seed_dummy_large

import os
import re
import random
import hashlib
from datetime import date, timedelta
from typing import List, Tuple, Dict, Optional

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone
from faker import Faker

# ---------------------------------
# 전역 설정
# ---------------------------------
DEFAULT_USERS = 500
DEFAULT_PROJECTS = 120
DEFAULT_TEAMS = 80

# Skills 테이블은 영문으로 시딩
DEFAULT_SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript",
    "Django", "Spring", "Node.js", "Express", "React", "Next.js", "Vue",
    "MySQL", "PostgreSQL", "MongoDB", "Redis",
    "AWS", "GCP", "Azure", "Docker", "Kubernetes",
    "TensorFlow", "PyTorch", "scikit-learn", "OpenCV", "Figma", "Git"
]

# 한글 스킬 → Skills.name(영문) 매핑
SKILL_KR2EN = {
    "리액트": "React",
    "자바스크립트": "JavaScript",
    "타입스크립트": "TypeScript",
    "뷰": "Vue",
    "넥스트": "Next.js",
    "노드": "Node.js",
    "익스프레스": "Express",
    "장고": "Django",
    "마이SQL": "MySQL",
    "자바": "Java",
    "파이썬": "Python",
    "포스트그레SQL": "PostgreSQL",
    "레디스": "Redis",
    "몽고디비": "MongoDB",
    "도커": "Docker",
    "쿠버네티스": "Kubernetes",
    "AWS": "AWS",
    "GCP": "GCP",
    "애저": "Azure",
    "텐서플로": "TensorFlow",
    "파이토치": "PyTorch",
    "사이킷런": "scikit-learn",
    "오픈CV": "OpenCV",
    "피그마": "Figma",
    "깃": "Git",
}

# 역할 영→한 표시용 (LLM 프롬프트/검증용)
ROLE_EN2KR = {
    "Frontend": "프론트엔드",
    "Backend": "백엔드",
    "Designer": "디자이너",
    "Planner": "기획",
    "Data": "데이터",
}
REGIONS_KR = [
    "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시",
    "대전광역시", "울산광역시", "세종특별자치시",
    "경기도", "강원도", "충청북도", "충청남도",
    "전라북도", "전라남도", "경상북도", "경상남도",
    "제주특별자치도",
]

# 현실감 있는 대략적 가중치(합계 1.0 근사)
REGION_WEIGHTS = {
    "서울특별시": 0.22, "경기도": 0.27, "인천광역시": 0.07,
    "부산광역시": 0.07, "대구광역시": 0.05, "대전광역시": 0.04, "울산광역시": 0.02, "세종특별자치시": 0.01,
    "광주광역시": 0.04, "강원도": 0.03, "충청북도": 0.03, "충청남도": 0.04,
    "전라북도": 0.03, "전라남도": 0.03, "경상북도": 0.05, "경상남도": 0.06, "제주특별자치도": 0.02,
}

PROF_LEVELS = ["Beginner", "Intermediate", "Advanced"]  # ENUM과 일치
TEAM_ROLES = ["Leader", "Backend", "Frontend", "Designer", "Planner", "Data"]

fake = Faker("ko_KR")
Faker.seed(42)
random.seed(42)

PROJECT_TOPICS = [
    "AI 면접 솔루션", "맛집 추천 및 예약", "여행 계획 공유", "스터디 그룹 매칭",
    "반려동물 산책 동반", "중고 거래 플랫폼", "개인 포트폴리오 웹사이트",
    "온라인 투표 시스템", "뉴스레터 구독 서비스"
]
ROLES_NEEDED = {
    "프론트엔드 개발자": [1, 2, 3],
    "백엔드 개발자": [1, 2],
    "UI/UX 디자이너": [1],
    "AI 모델러": [1, 2],
    "iOS 앱 개발자": [1, 2],
    "Android 앱 개발자": [1, 2],
}
PROJECT_DURATIONS = ["1개월", "2개월", "3개월", "6개월"]

# ===== Persona & Consistent Sampling =====
PERSONAS = {
    "backend_devops": {
        "role_pool": ["Backend"],
        "major_pool": ["컴퓨터공학", "정보보호"],
        "skills_core": ["도커", "쿠버네티스", "레디스", "포스트그레SQL", "깃"],
        "skills_opt": ["AWS", "GCP", "Azure", "몽고디비"],
        "experience_pool": ["중수", "고수"],
        "collab_pool": ["혼합", "오프라인 중심"],
        "meet_pool": ["주 2~3회", "매일 가능"],
        "topics_pool": ["API", "데이터", "성능", "아키텍처"]
    },
    "ml_engineer": {
        "role_pool": ["Data"],
        "major_pool": ["컴퓨터공학", "기타"],
        "skills_core": ["텐서플로", "파이토치", "사이킷런", "오픈CV", "깃"],
        "skills_opt": ["도커", "쿠버네티스", "AWS"],
        "experience_pool": ["초보", "중수", "고수"],
        "collab_pool": ["온라인 중심", "혼합"],
        "meet_pool": ["주 1회", "주 2~3회"],
        "topics_pool": ["ML", "컴퓨터비전", "모델서빙"]
    },
    "uxui_designer": {
        "role_pool": ["Designer", "Planner"],
        "major_pool": ["디자인", "기타"],
        "skills_core": ["피그마", "깃"],
        "skills_opt": [],
        "experience_pool": ["초보", "중수"],
        "collab_pool": ["온라인 중심", "혼합"],
        "meet_pool": ["주 1회", "주 2~3회"],
        "topics_pool": ["UX", "UI", "리서치", "와이어프레임"]
    }
}

# 스킬 상관 (선택)
PAIR_BONUS = {("리액트", "타입스크립트"): 0.3, ("노드", "레디스"): 0.2}

# ---------------------------
# 공용 유틸
# ---------------------------
def weighted_choice(items, weights=None):
    if not items:
        return None
    if not weights:
        return random.choice(items)
    total = sum(weights)
    r = random.uniform(0, total)
    s = 0.0
    for item, w in zip(items, weights):
        s += w
        if r <= s:
            return item
    return items[-1]

def sample_user_from_persona(p: dict) -> dict:
    role = random.choice(p["role_pool"])
    major = weighted_choice(p["major_pool"], weights=[0.7] + [0.3] * (len(p["major_pool"]) - 1))
    if "초보" in p["experience_pool"]:
        exp = weighted_choice(p["experience_pool"], weights=[0.6, 0.4] if len(p["experience_pool"]) == 2 else None)
    else:
        exp = weighted_choice(p["experience_pool"], weights=[0.4, 0.6] if len(p["experience_pool"]) == 2 else None)

    core_k = min(len(p["skills_core"]), random.randint(2, 4))
    opt_k = min(len(p["skills_opt"]), random.randint(0, 2))
    skills = random.sample(p["skills_core"], core_k) + random.sample(p["skills_opt"], opt_k)

    if skills:
        first = skills[0]
        for (a, b), bonus in PAIR_BONUS.items():
            if first == a and b not in skills and random.random() < bonus:
                skills.append(b)
            if first == b and a not in skills and random.random() < bonus:
                skills.append(a)
    # dedup (order-preserving)
    seen = set()
    skills = [s for s in skills if not (s in seen or seen.add(s))]

    collab = random.choice(p["collab_pool"])
    meet = random.choice(p["meet_pool"])
    topics = ", ".join(random.sample(p["topics_pool"], k=min(3, len(p["topics_pool"]))))

    return {
        "role": role,
        "major": major,
        "experience_level": exp,
        "skills": skills,
        "collaboration_style": collab,
        "meeting_frequency": meet,
        "preferred_project_topics": topics,
    }

INTRO_TMPL = (
    "안녕하세요, {major} 전공의 {role} 지망생입니다. "
    "현재 수준은 {experience_level}이며, {skills} 역량을 중심으로 성장하고 있습니다. "
    "협업은 {collaboration_style}을 선호하고 미팅은 {meeting_frequency}로 진행하길 바랍니다. "
    "관심 주제는 {preferred_project_topics}입니다."
)

def build_intro(pack: dict) -> str:
    return INTRO_TMPL.format(
        major=pack["major"],
        role=pack["role"],
        experience_level=pack["experience_level"],
        skills=", ".join(pack["skills"]),
        collaboration_style=pack["collaboration_style"],
        meeting_frequency=pack["meeting_frequency"],
        preferred_project_topics=pack["preferred_project_topics"],
    )

# --- 다양성 후처리(짧은 소개문에만 라이트 적용) ---
def _postprocess_intro_variation(text: str) -> str:
    if not text:
        return text
    s = text.strip()
    # 금지 인사 후처리(혹시 남아있으면 제거)
    s = re.sub(r"^\s*안녕하세요[^\n]*\n?", "", s)
    s = re.sub(r"^\s*안녕하세요[^\n]*$", "", s)

    # 한 문장/짧은 경우에만 소폭 변형
    parts = re.split(r'(?:[.!?]|다\.)\s+', s)
    if len(parts) == 1 and 15 <= len(s) <= 160:
        variants = [
            lambda t: t.replace("입니다.", "이에요.") if "입니다." in t else t,
            lambda t: t.replace("합니다.", "해요.") if "합니다." in t else t,
            lambda t: t + " 함께 만들어갈 분과 대화 나누고 싶어요.",
        ]
        s = random.choice(variants)(s)
    return s.strip()

# --- 검증: 영문 기준으로 정규화하여 중복 카운트 방지 ---
def validate_user_pack(u: dict) -> List[str]:
    errors: List[str] = []

    # 기준 세트(영문)
    FRONT_EN = {"React", "JavaScript", "TypeScript", "Vue", "Next.js"}
    BACK_EN  = {"Node.js", "Python", "Django", "MySQL", "PostgreSQL", "Redis"}
    DESIGN_EN= {"Figma"}

    KR2EN = SKILL_KR2EN.copy()

    role = u.get("role")
    exp  = u.get("experience_level")

    S_en  = set(u.get("skills_en", []))
    S_kr  = set(u.get("skills_kr",  []))
    S_raw = set(u.get("skills",     []))

    S_from_kr  = {KR2EN.get(s, s) for s in S_kr}
    S_from_raw = {KR2EN.get(s, s) for s in S_raw}
    S = S_en | S_from_kr | S_from_raw  # 영문 기준 dedup

    if role == "Frontend" and not (S & FRONT_EN):
        errors.append("Frontend인데 프론트 핵심 스킬이 없음")
    if role == "Backend" and not (S & BACK_EN):
        errors.append("Backend인데 백엔드 핵심 스킬이 없음")
    if role in {"Designer", "Planner"} and "Figma" not in S:
        errors.append("디자이너/기획인데 Figma 미포함")

    if exp == "고수" and len(S) < 3:
        errors.append("고수인데 스킬 3개 미만")
    if exp == "초보" and len(S) > 5:
        errors.append("초보인데 스킬 과다")

    return errors

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
    help = "sideproj 스키마(Users/Skills/UserSkills/Projects/Teams/TeamMembers/MatchScores/Evaluations/Portfolios) 더미데이터 생성"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=DEFAULT_USERS, help="생성할 사용자 수")
        parser.add_argument("--projects", type=int, default=DEFAULT_PROJECTS, help="생성할 프로젝트 수")
        parser.add_argument("--teams", type=int, default=DEFAULT_TEAMS, help="생성할 팀 수")
        parser.add_argument("--flush", action="store_true", help="모든 테이블 데이터를 비우고 시작(TRUNCATE)")
        parser.add_argument("--skip-deep", action="store_true", help="Users/Skills/UserSkills까지만 생성(빠른 테스트용)")

        # LLM 옵션
        parser.add_argument("--use-llm", action="store_true", help="LLM 기능 전체 on/off")
        parser.add_argument("--llm-free", action="store_true", help="프로젝트 텍스트 자유 형식 LLM 생성")
        parser.add_argument("--llm-intro", action="store_true", help="유저 자기소개 LLM 생성")

    @transaction.atomic
    def handle(self, *args, **opts):
        users_n = opts["users"]
        projects_n = opts["projects"]
        teams_n = opts["teams"]
        do_flush = opts["flush"]
        skip_deep = opts["skip_deep"]

        self.use_llm = bool(opts.get("use_llm", False))
        self.llm_free = bool(opts.get("llm_free", False))
        self.llm_intro = bool(opts.get("llm_intro", False))

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
                project_ids = self._create_projects(cur, projects_n, user_ids, skill_ids)
                team_ids = self._create_teams(cur, teams_n, project_ids)
                self._create_team_members(cur, team_ids, user_ids)
                self._create_match_scores(cur, user_ids, project_ids)
                self._create_evaluations(cur, team_ids, user_ids)
                self._create_portfolios(cur, user_ids, project_ids)

        self.stdout.write(self.style.SUCCESS("[seed_sideproj] DONE"))

    # ---------------------------
    # 내부 메서드들
    # ---------------------------
    def _flush_all(self, cur):
        self.stdout.write("Dropping all data (FK 순서 유의)…")
        cur.execute("SET FOREIGN_KEY_CHECKS=0;")
        for tbl in [
            "Portfolios", "Evaluations", "MatchScores", "TeamMembers",
            "Teams", "Projects", "UserSkills", "Skills", "Users"
        ]:
            cur.execute(f"TRUNCATE TABLE {tbl};")
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

    def _create_users(self, cur, n_users: int) -> Tuple[List[int], dict]:
        """
        returns: (user_ids, user_skill_names_by_user_id)
        user_skill_names_by_user_id: {user_id: ["React","TypeScript",...]}  # 영문 스킬명
        """
        self.stdout.write(f"Seeding Users x {n_users}…")

        cur.execute("SELECT skill_id, name FROM Skills;")
        skill_name_to_id = {name: sid for (sid, name) in cur.fetchall()}
        allowed_skill_names = set(skill_name_to_id.keys())

        EN2KR = {v: k for k, v in SKILL_KR2EN.items()}

        PRIORITY_SKILLS = [
            "React", "TypeScript", "JavaScript", "Node.js", "Python", "Django", "MySQL",
            "PostgreSQL", "Redis", "Docker", "Kubernetes", "Figma", "Git", "AWS", "GCP", "Azure",
            "MongoDB", "TensorFlow", "PyTorch", "scikit-learn", "OpenCV"
        ]
        priority_allowed = [s for s in PRIORITY_SKILLS if s in allowed_skill_names]
        any_allowed = list(allowed_skill_names)

        now = timezone.now()
        staged_users: List[Tuple[dict, Tuple]] = []
        persona_keys = list(PERSONAS.keys())
        recent_intros = set()

        for _ in range(n_users):
            tried = 0
            max_try = 5 * max(1, len(persona_keys))
            success = False

            while tried < max_try and not success:
                tried += 1
                p_key = random.choice(persona_keys)
                p = PERSONAS[p_key]

                pack = sample_user_from_persona(p)

                # 1) 한글 → 영문 매핑
                pack["skills"] = [SKILL_KR2EN.get(s, s) for s in pack["skills"]]
                # 2) 실제 존재하는 스킬만 유지
                pack["skills"] = [s for s in pack["skills"] if s in allowed_skill_names]
                if not pack["skills"]:
                    continue

                # 표시/검증은 KR도 함께 준비
                display_pack = dict(pack)
                display_pack["skills"] = [EN2KR.get(s, s) for s in pack["skills"]]
                display_pack["role"] = ROLE_EN2KR.get(pack["role"], pack["role"])  # 역할 한글화

                # ---- 자기소개: LLM 우선 → 폴백 ----
                intro = None
                if self.use_llm and self.llm_intro:
                    intro = self._llm_generate_user_intro({
                        **display_pack,
                        "skills": display_pack["skills"]
                    })
                if not intro:
                    intro = build_intro(display_pack)

                # 검증(영문 기준)
                cand_for_validation = {
                    **pack,
                    "introduction": intro,
                    "skills_en": pack["skills"],
                    "skills_kr": display_pack["skills"],
                }
                errors = validate_user_pack(cand_for_validation)
                if errors:
                    continue

                # 소개 다양성 후처리
                intro = _postprocess_intro_variation(intro)

                # 중복 방지 소폭
                key = intro.strip()
                if key in recent_intros:
                    suffix = random.choice([
                        " 빠르게 시도하고 배우며 성장하고 싶어요.",
                        " 유연한 커뮤니케이션을 지향합니다.",
                        " 함께 해볼 이야기가 많습니다."
                    ])
                    if len(intro) + len(suffix) < 1200:
                        intro = intro + suffix
                recent_intros.add(key)
                if len(recent_intros) > 50:
                    recent_intros.pop()

                name = fake.name()
                email = f"{fake.unique.user_name()}{random.randint(1000,9999)}@example.com"
                pw = sha256_hex(fake.password(length=12))
                birth = rand_birth()

                available_region = random.choice(REGIONS_KR)
                github_url = f"https://github.com/{fake.user_name()}"
                portfolio_url = fake.url()
                major = pack["major"]
                specialty = pack["role"]
                tech_stack = ", ".join(pack["skills"])  # EN 저장
                collaboration_tools = random.choice(["Slack", "Discord", "Notion", "Teams"])
                experience_level = pack["experience_level"]
                collaboration_style = pack["collaboration_style"]
                meeting_frequency = pack["meeting_frequency"]
                belbin_role = random.choice(["PL", "RI", "CO", "SH", "ME", "TW", "IMP", "CF", "SP"])
                preferred_team_size = random.choice(["2~3명", "4~5명", "6명 이상"])
                preferred_project_topics = pack["preferred_project_topics"]
                availability_period = random.choice(["1달 이내", "2~3달", "장기(3달 이상)", "1Y"])
                is_profile_complete = True
                last_login = now

                staged_users.append((
                    pack,
                    (
                        name, birth, email, pw, intro, now,
                        available_region, github_url, portfolio_url,
                        major, specialty, tech_stack, collaboration_tools,
                        experience_level, collaboration_style, meeting_frequency,
                        belbin_role, preferred_team_size, preferred_project_topics,
                        availability_period, is_profile_complete, last_login
                    )
                ))
                success = True

            if not success:
                # Fallback: 허용 스킬 강제 구성
                fb_skills = []
                if priority_allowed:
                    fb_skills.extend(random.sample(priority_allowed, k=min(len(priority_allowed), random.randint(2, 4))))
                remain_k = max(0, random.randint(0, 2) - len(fb_skills))
                if remain_k > 0 and any_allowed:
                    extra = [s for s in random.sample(any_allowed, k=min(len(any_allowed), remain_k)) if s not in fb_skills]
                    fb_skills.extend(extra)
                if not fb_skills and any_allowed:
                    fb_skills = [random.choice(any_allowed)]

                pack = {
                    "major": random.choice(["컴퓨터공학", "디자인", "기타"]),
                    "role": random.choice(["Frontend", "Backend", "Designer", "Data"]),
                    "experience_level": random.choice(["초보", "중수"]),
                    "collaboration_style": random.choice(["오프라인 중심", "온라인 중심", "혼합"]),
                    "meeting_frequency": random.choice(["주 1회", "주 2~3회", "매일 가능"]),
                    "preferred_project_topics": fake.sentence(nb_words=5),
                    "skills": fb_skills,
                }

                display_pack = dict(pack)
                display_pack["skills"] = [EN2KR.get(s, s) for s in pack["skills"]]
                display_pack["role"] = ROLE_EN2KR.get(pack["role"], pack["role"])

                intro = None
                if self.use_llm and self.llm_intro:
                    intro = self._llm_generate_user_intro({
                        **display_pack,
                        "skills": display_pack["skills"]
                    })
                if not intro:
                    intro = build_intro(display_pack)

                intro = _postprocess_intro_variation(intro)

                name = fake.name()
                email = f"{fake.unique.user_name()}{random.randint(1000,9999)}@example.com"
                pw = sha256_hex(fake.password(length=12))
                birth = rand_birth()

                staged_users.append((
                    pack,
                    (
                        name, birth, email, pw, intro, now,
                        fake.city(), f"https://github.com/{fake.user_name()}", fake.url(),
                        pack["major"], pack["role"], ", ".join(pack["skills"]),
                        random.choice(["Slack", "Discord", "Notion", "Teams"]),
                        pack["experience_level"], pack["collaboration_style"], pack["meeting_frequency"],
                        random.choice(["PL", "RI", "CO", "SH", "ME", "TW", "IMP", "CF", "SP"]),
                        random.choice(["2~3명", "4~5명", "6명 이상"]),
                        pack["preferred_project_topics"],
                        random.choice(["1달 이내", "2~3달", "장기(3달 이상)", "1Y"]),
                        True, now
                    )
                ))

        # INSERT Users
        user_rows = [d + (0, 1, 0) for _, d in staged_users]  # (is_staff, is_active, is_superuser)
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
            VALUES (%s, %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s)
            """,
            user_rows,
        )

        # 방금 삽입된 user_id 조회
        cur.execute("SELECT user_id FROM Users ORDER BY user_id DESC LIMIT %s;", [len(user_rows)])
        inserted_ids_desc = [uid for (uid,) in cur.fetchall()]
        inserted_ids = list(reversed(inserted_ids_desc))  # 삽입 순서와 맞춤

        # user_id -> skills(영문명) 매핑
        user_skill_names_by_uid: Dict[int, List[str]] = {}
        for uid, (pack, _d) in zip(inserted_ids, staged_users):
            user_skill_names_by_uid[uid] = pack.get("skills", [])  # EN 스킬

        return inserted_ids, user_skill_names_by_uid

    def _create_user_skills_from_names(self, cur, user_skill_names_by_uid: dict, name_to_id: dict):
        self.stdout.write("Seeding UserSkills… (개연성 기반 선택 반영)")
        rows = []
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

    # ---------------------------
    # LLM: 유저 자기소개
    # ---------------------------
    def _llm_generate_user_intro(self, pack_display_kr: dict) -> Optional[str]:
        """
        유저 자기소개를 LLM으로 자유 생성.
        입력(pack_display_kr): 전공/역할/스킬(한글명), 협업 스타일/미팅 빈도/관심 주제 등
        출력: 한글 자기소개 문자열 (실패 시 None)
        """
        try:
            from openai import OpenAI
        except Exception:
            self.stdout.write(self.style.WARNING("[LLM] openai 패키지가 없어 자기소개 폴백 사용"))
            return None

        major = pack_display_kr.get("major", "")
        role_kr = pack_display_kr.get("role", "")
        skills = pack_display_kr.get("skills", [])
        collaboration_style = pack_display_kr.get("collaboration_style", "")
        meeting_frequency = pack_display_kr.get("meeting_frequency", "")
        preferred_topics = pack_display_kr.get("preferred_project_topics", "")
        experience_level = pack_display_kr.get("experience_level", "")

        # 역할별 필수 키워드 1개(검증 통과 유도)
        required_kw = ""
        rk = role_kr or ""
        if "프론트" in rk:
            required_kw = "프론트"
        elif "백엔드" in rk:
            required_kw = "백엔드"
        elif "디자" in rk:
            required_kw = "디자인"
        elif "기획" in rk:
            required_kw = "기획"
        elif "데이터" in rk:
            required_kw = "데이터"

        tones = ["담백한", "활기찬", "차분한", "실무자 느낌의", "학생다운", "커뮤니티 친화적인"]
        styles = ["~해요체", "~합니다체", "서술형 혼합"]
        chosen_tone = random.choice(tones)
        chosen_style = random.choice(styles)

        prompt = f"""
너는 지원 플랫폼의 사용자 소개 문구를 작성하는 도우미야.
다음 정보를 참고해서 2~4문장의 자연스러운 한국어 자기소개를 만들어줘.

[정보]
- 전공: {major}
- 역할: {role_kr}
- 보유기술(예시): {", ".join(skills)}
- 협업 스타일: {collaboration_style}
- 미팅 빈도: {meeting_frequency}
- 관심 주제: {preferred_topics}
- 숙련도: {experience_level}

[요청]
- 톤: {chosen_tone}, 문체: {chosen_style}
- 첫 문장은 '안녕하세요'로 시작하지 마. (반드시 금지)
- '저는 ~입니다.' 패턴을 반복하지 말고, 문장 종결을 다양화해.
- 보유 기술은 1~2개만 자연스럽게 언급해.
- 과장 금지, 구체성 1~2개(관심 주제/협업 방식) 포함.
- 결과는 자기소개 문단 텍스트만 출력(앞뒤 따옴표/코드블럭/마크다운 금지).
- 아래 키워드 중 하나를 반드시 포함: {required_kw}
""".strip()

        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                self.stdout.write(self.style.WARNING("[LLM] OPENAI_API_KEY가 없어 자기소개 폴백 사용"))
                return None

            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=1.05,
                top_p=0.95,
                presence_penalty=0.4,
                frequency_penalty=0.4,
                messages=[{"role": "user", "content": prompt}],
            )
            text = (resp.choices[0].message.content or "").strip()
            if not text:
                return None
            if len(text) > 1200:
                text = text[:1200]
            # 금지 인사/단조로운 종결 후처리
            text = _postprocess_intro_variation(text)
            return text
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"[LLM] intro 생성 예외 → 폴백: {e}"))
            return None

    # ---------------------------
    # LLM: 프로젝트 자유 생성
    # ---------------------------
    def _llm_generate_project_free(self, topic: str, roles_text: str, duration: str, tech_stack_text: str) -> Optional[tuple]:
        """
        완전 자유 형식. 반환: (title, description, goal)
        - 최소 규칙: 첫 줄=제목, 마지막 줄에 '목표:' 1문장 포함 권장
        - 실패 시 None 반환(폴백)
        """
        try:
            from openai import OpenAI
        except Exception:
            self.stdout.write(self.style.WARNING("[LLM] openai 패키지가 없어 프로젝트 폴백 사용"))
            return None

        prompt = f"""
다음 정보를 참고만 하되, 형식/톤을 완전히 자유롭게 한국어로 공고 문구를 작성하세요.
- 주제(참고): {topic}
- 모집 역할(참고): {roles_text}
- 기간(참고): {duration}
- 기술스택(참고): {tech_stack_text}

요청(최소 규칙):
- 첫 줄은 강렬한 '제목' 한 줄로만.
- 본문은 자연스러운 설명.
- 마지막 줄에 '목표'를 한 문장으로 포함(예: "목표: 6주 내 MVP 출시").
이 외에는 아무 형식 제약 없음.
""".strip()

        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                self.stdout.write(self.style.WARNING("[LLM] OPENAI_API_KEY 가 설정되지 않아 폴백"))
                return None

            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.9,
                messages=[{"role": "user", "content": prompt}],
            )
            text = (resp.choices[0].message.content or "").strip()
            if not text:
                self.stdout.write(self.style.WARNING("[LLM] 빈 응답 → 폴백"))
                return None

            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            if not lines:
                self.stdout.write(self.style.WARNING("[LLM] 라인 분해 실패 → 폴백"))
                return None

            title = lines[0][:100]  # DB varchar(100) 보호

            goal_line = ""
            for ln in reversed(lines):
                if ln.startswith("목표") or ln.lower().startswith("goal"):
                    goal_line = ln
                    break

            if goal_line:
                body = "\n".join([ln for ln in lines[1:] if ln != goal_line]).strip()
                goal = goal_line
            else:
                body = "\n".join(lines[1:]).strip()
                goal = f"목표: {duration} 내 가시적 결과물(MVP) 도출"

            return (title, body, goal)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"[LLM] 예외 발생 → 폴백: {e}"))
            return None

    # ---------------------------
    # 프로젝트/팀/매칭/평가/포트폴리오
    # ---------------------------
    def _create_projects(self, cur, n_projects: int, user_ids: List[int], skill_ids: List[int]) -> List[int]:
        if n_projects <= 0 or not user_ids or not skill_ids:
            self.stdout.write(self.style.WARNING("[skip] projects: n_projects<=0 or missing users/skills"))
            return []

        self.stdout.write(f"Seeding Projects x {n_projects}…")
        rows = []
        now = timezone.now()

        used_titles = set()

        for _ in range(n_projects):
            creator = random.choice(user_ids)
            topic = random.choice(PROJECT_TOPICS)

            num_roles_to_recruit = random.randint(2, 4)
            recruiting_roles = random.sample(list(ROLES_NEEDED.keys()), num_roles_to_recruit)
            role_strings = []
            for role in recruiting_roles:
                num_needed = random.choice(ROLES_NEEDED[role])
                role_strings.append(f"{role} {num_needed}명")
            roles_text = ", ".join(role_strings)

            duration = random.choice(PROJECT_DURATIONS)

            req_count = min(random.randint(2, 5), len(skill_ids))
            required_ids = random.sample(skill_ids, req_count) if req_count else []
            names = []
            if required_ids:
                cur.execute(
                    "SELECT name FROM Skills WHERE skill_id IN (" + ",".join(["%s"] * len(required_ids)) + ")",
                    required_ids
                )
                names = [name for (name,) in cur.fetchall()]
            tech_stack_text = ", ".join(names)

            title = desc = goal = None

            # ---- LLM 자유 모드 ----
            if self.use_llm and self.llm_free:
                self.stdout.write("[LLM] 프로젝트 문구 LLM 자유 생성 시도…")
                llm_pack = self._llm_generate_project_free(topic, roles_text, duration, tech_stack_text)
                if llm_pack:
                    title, desc, goal = llm_pack

            # ---- 폴백(템플릿) ----
            if not title:
                title = f"{topic} — 팀원 모집"
            if not desc:
                my_role = random.choice(["PM", "리드 개발자"])
                desc = (
                    f"모집 역할: {roles_text}\n"
                    f"저는 {my_role} 역할을 맡아 프로젝트를 이끌 예정입니다.\n"
                    f"함께 멋진 서비스를 만들어봐요!"
                )
            if not goal:
                goal = f"목표: {duration} 내 MVP 출시"

            if title in used_titles and len(title) <= 96:
                title += random.choice([" 🚀", " 🔥", " v2", " plus"])
            used_titles.add(title)

            rows.append((creator, title[:100], desc, goal, tech_stack_text, True, now))

        executemany(
            cur,
            """
            INSERT INTO Projects (creator_id, title, description, goal, tech_stack, is_open, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
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
                rows.append((uid, pid, score, now))
        executemany(
            cur,
            "INSERT INTO MatchScores (user_id, project_id, score, evaluated_at) VALUES (%s, %s, %s, %s)",
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
            for _ in range(random.randint(0, 2)):
                pid = random.choice(project_ids)
                desc = fake.sentence(nb_words=12)
                url = f"https://github.com/{fake.user_name()}/{fake.word()}"
                rows.append((uid, pid, desc, url, now))
        executemany(
            cur,
            """
            INSERT INTO Portfolios (user_id, project_id, description, url, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            rows,
        )
