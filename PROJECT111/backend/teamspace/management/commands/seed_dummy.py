# teamspace/management/commands/seed_dummy.py

import random
import hashlib
from datetime import date, timedelta
from typing import List, Tuple

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

DEFAULT_SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript",
    "Django", "Spring", "Node.js", "Express", "React", "Next.js", "Vue",
    "MySQL", "PostgreSQL", "MongoDB", "Redis",
    "AWS", "GCP", "Azure", "Docker", "Kubernetes",
    "TensorFlow", "PyTorch", "scikit-learn", "OpenCV", "Figma", "Git"
]

PROF_LEVELS = ["Beginner", "Intermediate", "Advanced"]  # ENUM과 일치
TEAM_ROLES = ["Leader", "Backend", "Frontend", "Designer", "Planner", "Data"]

fake = Faker("ko_KR")

PROJECT_TOPICS = ["AI 면접 솔루션", "맛집 추천 및 예약", "여행 계획 공유", "스터디 그룹 매칭", "반려동물 산책 동반", "중고 거래 플랫폼", "개인 포트폴리오 웹사이트", "온라인 투표 시스템", "뉴스레터 구독 서비스"]
ROLES_NEEDED = {
    "프론트엔드 개발자": [1, 2, 3],
    "백엔드 개발자": [1, 2],
    "UI/UX 디자이너": [1],
    "AI 모델러": [1, 2],
    "iOS 앱 개발자": [1, 2],
    "Android 앱 개발자": [1, 2]
}
PROJECT_DURATIONS = ["1개월", "2개월", "3개월", "6개월"]


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

    @transaction.atomic
    def handle(self, *args, **opts):
        users_n = opts["users"]
        projects_n = opts["projects"]
        teams_n = opts["teams"]
        do_flush = opts["flush"]
        skip_deep = opts["skip_deep"]

        self.stdout.write(self.style.NOTICE("[seed_sideproj] START"))

        with connection.cursor() as cur:
            # settings.py 의 default DB가 sideproj를 가리키고 있어야 함
            # 필요시 강제: cur.execute("USE sideproj;")

            if do_flush:
                self._flush_all(cur)

            skill_ids = self._ensure_skills(cur)
            user_ids = self._create_users(cur, users_n)
            self._create_user_skills(cur, user_ids, skill_ids)

            if not skip_deep:
                project_ids = self._create_projects(cur, projects_n, user_ids, skill_ids)
                team_ids = self._create_teams(cur, teams_n, project_ids)
                self._create_team_members(cur, team_ids, user_ids)
                self._create_match_scores(cur, user_ids, project_ids)
                self._create_evaluations(cur, team_ids, user_ids)
                self._create_portfolios(cur, user_ids, project_ids)

        self.stdout.write(self.style.SUCCESS("[seed_sideproj] DONE"))

    # ---------------------------
    # 내부 메서드들 (반드시 클래스 안 들여쓰기 유지)
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

    def _create_users(self, cur, n_users: int) -> List[int]:
        self.stdout.write(f"Seeding Users x {n_users}…")

        rows = []
        now = timezone.now()
        for _ in range(n_users):
            name = fake.name()
            email = f"{fake.unique.user_name()}{random.randint(1000,9999)}@example.com"
            pw = sha256_hex(fake.password(length=12))
            birth = rand_birth()

            intro_templates = [
                "안녕하세요, 저는 {job}에 관심이 많은 {name}입니다. {sentence}",
                "저는 {city}에서 온 {job} 지망생 {name}입니다. {sentence}",
                "꾸준히 배우며 성장하는 {job} {name}입니다. {sentence}",
                "팀워크를 중시하는 {job} {name}이고, {sentence}",
                "{name}입니다. 새로운 {job} 경험을 통해 성장하고 싶습니다. {sentence}"
            ]
            intro = random.choice(intro_templates).format(
                name=name,
                job=fake.job(),
                city=fake.city(),
                sentence=fake.sentence(nb_words=10)
            )

            created = now

            # ── 추가된 컬럼들 ──
            available_region = fake.city()  # VARCHAR(20)
            github_url = f"https://github.com/{fake.user_name()}"  # VARCHAR(200)
            portfolio_url = fake.url()  # VARCHAR(200)
            major = random.choice(["컴퓨터공학", "정보보호", "디자인", "경영", "기타", "비전공자"])  # VARCHAR(20)
            specialty = fake.job()  # VARCHAR(255)
            tech_stack = ", ".join(random.sample(DEFAULT_SKILLS, random.randint(1, 5)))  # VARCHAR(255)
            collaboration_tools = random.choice(["Slack", "Discord", "Notion", "Teams"])  # VARCHAR(255)
            experience_level = random.choice(["초보", "중수", "고수"])  # VARCHAR(10)
            collaboration_style = random.choice(["오프라인 중심", "온라인 중심", "혼합"])  # VARCHAR(10)
            meeting_frequency = random.choice(["주 1회", "주 2~3회", "매일 가능"])  # VARCHAR(20)
            belbin_role = random.choice(["PL", "RI", "CO", "SH", "ME", "TW", "IMP", "CF", "SP"])  # VARCHAR(3) 예시 약어
            preferred_team_size = random.choice(["2~3명", "4~5명", "6명 이상"])  # VARCHAR(10)
            preferred_project_topics = fake.sentence(nb_words=5)  # VARCHAR(255)
            availability_period = random.choice(["1달 이내", "2~3달", "장기(3달 이상)", "1Y"])  # VARCHAR(10)
            is_profile_complete = True  # BOOLEAN
            last_login = now  # DATETIME NULL

            rows.append((
                name, birth, email, pw, intro, created,
                available_region, github_url, portfolio_url,
                major, specialty, tech_stack, collaboration_tools,
                experience_level, collaboration_style, meeting_frequency,
                belbin_role, preferred_team_size, preferred_project_topics,
                availability_period, is_profile_complete, last_login
            ))

        executemany(
            cur,
            """
            INSERT INTO Users (
                name, birthdate, email, password, introduction, created_at,
                available_region, github_url, portfolio_url,
                major, specialty, tech_stack, collaboration_tools,
                experience_level, collaboration_style, meeting_frequency,
                belbin_role, preferred_team_size, preferred_project_topics,
                availability_period, is_profile_complete, last_login
            )
            VALUES (%s, %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s)
            """,
            rows,
        )

        cur.execute("SELECT user_id FROM Users;")
        return [uid for (uid,) in cur.fetchall()]

    def _create_user_skills(self, cur, user_ids: List[int], skill_ids: List[int]):
        self.stdout.write("Seeding UserSkills… (각 유저 1~6 개)")
        rows = []
        for uid in user_ids:
            k = random.randint(1, 6)
            chosen = random.sample(skill_ids, k)
            for sid in chosen:
                rows.append((uid, sid, random.choice(PROF_LEVELS)))
        executemany(
            cur,
            "INSERT IGNORE INTO UserSkills (user_id, skill_id, proficiency_level) VALUES (%s, %s, %s)",
            rows,
        )

    def _create_projects(self, cur, n_projects: int, user_ids: List[int], skill_ids: List[int]) -> List[int]:
        self.stdout.write(f"Seeding Projects x {n_projects}…")
        rows = []
        now = timezone.now()
        for _ in range(n_projects):
            creator = random.choice(user_ids)
            
            # --- 테마 기반 텍스트 생성 ---
            topic = random.choice(PROJECT_TOPICS)
            
            # 1. 제목 생성
            title = f"{topic} 프로젝트 함께하실 분 구합니다!"

            # 2. 설명 생성 (필요 역할)
            num_roles_to_recruit = random.randint(2, 4)
            recruiting_roles = random.sample(list(ROLES_NEEDED.keys()), num_roles_to_recruit)
            role_strings = []
            for role in recruiting_roles:
                num_needed = random.choice(ROLES_NEEDED[role])
                role_strings.append(f"{role} {num_needed}명")
            my_role = random.choice(["PM", "리드 개발자"])
            desc = f"현재 저희 팀은 {', '.join(role_strings)}을(를) 모집하고 있습니다. 저는 {my_role} 역할을 맡아 프로젝트를 이끌 예정입니다. 함께 성장하며 멋진 서비스를 만들어봐요!"

            # 3. 목표 생성
            duration = random.choice(PROJECT_DURATIONS)
            goal = f"총 프로젝트 기간은 {duration}으로 예상하며, 기간 내 MVP 출시를 목표로 합니다."
            
            # 4. 기술 스택 생성
            req_count = random.randint(2, 5)
            required_ids = random.sample(skill_ids, req_count)
            cur.execute(
                "SELECT name FROM Skills WHERE skill_id IN (" + ",".join(["%s"] * len(required_ids)) + ")",
                required_ids
            )
            names = [name for (name,) in cur.fetchall()]
            tech_stack = ", ".join(names)

            rows.append((creator, title, desc, goal, tech_stack, True, now))

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
        self.stdout.write("Seeding TeamMembers… (팀당 3~6명)")
        rows = []
        now = timezone.now()
        for tid in team_ids:
            members = random.sample(user_ids, random.randint(3, 6))
            for idx, uid in enumerate(members):
                role = TEAM_ROLES[0] if idx == 0 else random.choice(TEAM_ROLES[1:])
                rows.append((tid, uid, role, now))
        executemany(
            cur,
            "INSERT IGNORE INTO TeamMembers (team_id, user_id, role, joined_at) VALUES (%s, %s, %s, %s)",
            rows,
        )

    def _create_match_scores(self, cur, user_ids: List[int], project_ids: List[int]):
        self.stdout.write("Seeding MatchScores… (유저 일부 x 프로젝트 일부)")
        rows = []
        now = timezone.now()
        sample_users = random.sample(user_ids, min(200, len(user_ids)))
        sample_projects = random.sample(project_ids, min(100, len(project_ids)))
        for uid in sample_users:
            targets = random.sample(sample_projects, random.randint(3, min(8, len(sample_projects))))
            for pid in targets:
                score = round(random.uniform(20.0, 98.0), 2)
                rows.append((uid, pid, score, now))
        executemany(
            cur,
            "INSERT INTO MatchScores (user_id, project_id, score, evaluated_at) VALUES (%s, %s, %s, %s)",
            rows,
        )

    def _create_evaluations(self, cur, team_ids: List[int], user_ids: List[int]):
        self.stdout.write("Seeding Evaluations… (팀 내 상호 평가 소량)")
        rows = []
        now = timezone.now()
        pick_teams = random.sample(team_ids, max(1, len(team_ids)//3))
        for tid in pick_teams:
            members = random.sample(user_ids, random.randint(3, 5))
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