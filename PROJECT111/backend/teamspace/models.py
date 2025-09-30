# from django.db import models


# class Users(models.Model):
#     name = models.CharField(max_length=50)
#     birthdate = models.DateField(null=True, blank=True)
#     email = models.EmailField(unique=True)
#     password_hash = models.CharField(max_length=255)
#     introduction = models.TextField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name


# class Skills(models.Model):
#     name = models.CharField(max_length=50)

#     def __str__(self):
#         return self.name


# class UserSkills(models.Model):
#     BEGINNER = 'Beginner'
#     INTERMEDIATE = 'Intermediate'
#     ADVANCED = 'Advanced'
#     PROFICIENCY_CHOICES = [
#         (BEGINNER, 'Beginner'),
#         (INTERMEDIATE, 'Intermediate'),
#         (ADVANCED, 'Advanced'),
#     ]

#     user = models.ForeignKey(Users, on_delete=models.CASCADE)
#     skill = models.ForeignKey(Skills, on_delete=models.CASCADE)
#     proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES)

#     class Meta:
#         unique_together = ('user', 'skill')


# class Projects(models.Model):
#     creator = models.ForeignKey(Users, on_delete=models.CASCADE)
#     title = models.CharField(max_length=100)
#     description = models.TextField(null=True, blank=True)
#     goal = models.TextField(null=True, blank=True)
#     tech_stack = models.TextField(null=True, blank=True)
#     is_open = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title


# class Teams(models.Model):
#     project = models.OneToOneField(Projects, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

# class TeamMembers(models.Model):
#     team = models.ForeignKey(Teams, on_delete=models.CASCADE)
#     user = models.ForeignKey(Users, on_delete=models.CASCADE)
#     role = models.CharField(max_length=50)
#     joined_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('team', 'user')


# class MatchScores(models.Model):
#     user = models.ForeignKey(Users, on_delete=models.CASCADE)
#     project = models.ForeignKey(Projects, on_delete=models.CASCADE)
#     score = models.FloatField()
#     evaluated_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'project')


# class Evaluations(models.Model):
#     evaluator = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='given_evaluations')
#     evaluatee = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='received_evaluations')
#     team = models.ForeignKey(Teams, on_delete=models.CASCADE)
#     score = models.IntegerField()
#     feedback = models.TextField(null=True, blank=True)
#     evaluated_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('evaluator', 'evaluatee', 'team')


# class Portfolios(models.Model):
#     user = models.ForeignKey(Users, on_delete=models.CASCADE)
#     project = models.ForeignKey(Projects, on_delete=models.CASCADE)
#     description = models.TextField(null=True, blank=True)
#     url = models.URLField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'project')


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Users(models.Model):
    user_id = models.AutoField(primary_key=True, db_column='user_id')
    name = models.CharField(max_length=50)
    birthdate = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True) # Django login이 사용하는 필드

    # --- 추가 정보 필드 ---
    # 기본 정보
    REGION_CHOICES = [('SEOUL', '수도권'), ('CHUNGCHEONG', '충청권'), ('YEONGNAM', '영남권'), ('HONAM', '호남권'), ('ETC', '기타')]
    available_region = models.CharField(max_length=20, choices=REGION_CHOICES, null=True, blank=True)
    github_url = models.URLField(max_length=200, null=True, blank=True)
    portfolio_url = models.URLField(max_length=200, null=True, blank=True)
    introduction = models.TextField(max_length=150, null=True, blank=True)

    # 기술 역량 및 경험
    MAJOR_CHOICES = [('CS', '컴퓨터공학'), ('SECURITY', '정보보호'), ('DESIGN', '디자인'), ('BUSINESS', '경영/기타'), ('NON_CS', '비전공자')]
    major = models.CharField(max_length=20, choices=MAJOR_CHOICES, null=True, blank=True)
    specialty = models.CharField(max_length=255, null=True, blank=True) # 복수선택, 쉼표로 구분
    tech_stack = models.CharField(max_length=255, null=True, blank=True) # 복수선택, 쉼표로 구분
    collaboration_tools = models.CharField(max_length=255, null=True, blank=True) # 복수선택, 쉼표로 구분
    EXPERIENCE_CHOICES = [('NONE', '없음'), ('ONCE', '1회'), ('FEW', '2~3회'), ('MANY', '4회 이상')]
    experience_level = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES, null=True, blank=True)

    # 협업 성향 및 방식
    COLLABORATION_STYLE_CHOICES = [('OFFLINE', '오프라인 중심'), ('ONLINE', '온라인 중심'), ('HYBRID', '혼합')]
    collaboration_style = models.CharField(max_length=10, choices=COLLABORATION_STYLE_CHOICES, null=True, blank=True)
    MEETING_FREQUENCY_CHOICES = [('WEEKLY_1', '주 1회'), ('WEEKLY_2_3', '주 2~3회'), ('DAILY', '매일 가능'), ('PROJECT_ONLY', '프로젝트 중심만 가능')]
    meeting_frequency = models.CharField(max_length=20, choices=MEETING_FREQUENCY_CHOICES, null=True, blank=True)
    BELBIN_CHOICES = [('PL', 'PL - 아이디어 뱅크'), ('RI', 'RI - 자원탐색자'), ('CO', 'CO - 조정자'), ('SH', 'SH - 추진자'), ('ME', 'ME - 평가자'), ('TW', 'TW - 팀 워커'), ('IMP', 'IMP - 실행자'), ('CF', 'CF - 완성자'), ('SP', 'SP - 전문가')]
    belbin_role = models.CharField(max_length=3, choices=BELBIN_CHOICES, null=True, blank=True)

    # 프로젝트 관련 선호도
    TEAM_SIZE_CHOICES = [('SMALL', '2~3명'), ('MEDIUM', '4~5명'), ('LARGE', '6명 이상도 가능/기타')]
    preferred_team_size = models.CharField(max_length=10, choices=TEAM_SIZE_CHOICES, null=True, blank=True)
    preferred_project_topics = models.CharField(max_length=255, null=True, blank=True) # 복수선택, 쉼표로 구분
    AVAILABILITY_CHOICES = [('SHORT', '단기: 1달 이내'), ('MEDIUM', '중기: 2~3달'), ('LONG', '장기: 3달 이상/기타')]
    availability_period = models.CharField(max_length=10, choices=AVAILABILITY_CHOICES, null=True, blank=True)

    # 프로필 완성 여부 플래그
    is_profile_complete = models.BooleanField(default=False)

    class Meta:
        db_table = 'Users'
        managed = False  # 기존 테이블 그대로 쓸 때

    def __str__(self):
        return self.name


class Skills(models.Model):
    skill_id = models.AutoField(primary_key=True, db_column='skill_id')
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'Skills'
        managed = False

    def __str__(self):
        return self.name


class UserSkills(models.Model):
    BEGINNER = 'Beginner'
    INTERMEDIATE = 'Intermediate'
    ADVANCED = 'Advanced'
    PROFICIENCY_CHOICES = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='user_id')
    skill = models.ForeignKey(Skills, on_delete=models.CASCADE, db_column='skill_id')
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES)

    class Meta:
        db_table = 'UserSkills'
        managed = False
        unique_together = ('user', 'skill')


class Projects(models.Model):
    project_id = models.AutoField(primary_key=True, db_column='project_id')
    creator = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='creator_id')
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    goal = models.TextField(null=True, blank=True)
    tech_stack = models.TextField(null=True, blank=True)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Projects'
        managed = False

    def __str__(self):
        return self.title


class Teams(models.Model):
    team_id = models.AutoField(primary_key=True, db_column='team_id')
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, db_column='project_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Teams'
        managed = False


class TeamMembers(models.Model):
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, db_column='team_id')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='user_id')
    role = models.CharField(max_length=50)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'TeamMembers'
        managed = False
        unique_together = ('team', 'user')


class MatchScores(models.Model):
    match_id = models.AutoField(primary_key=True, db_column='match_id')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='user_id')
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, db_column='project_id')
    score = models.FloatField()
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'MatchScores'
        managed = False
        unique_together = ('user', 'project')


class Evaluations(models.Model):
    evaluation_id = models.AutoField(primary_key=True, db_column='evaluation_id')
    evaluator = models.ForeignKey(
        Users, on_delete=models.CASCADE, db_column='evaluator_id', related_name='given_evaluations')
    evaluatee = models.ForeignKey(
        Users, on_delete=models.CASCADE, db_column='evaluatee_id', related_name='received_evaluations')
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, db_column='team_id')
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback = models.TextField(null=True, blank=True)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Evaluations'
        managed = False
        unique_together = ('evaluator', 'evaluatee', 'team')


class Portfolios(models.Model):
    portfolio_id = models.AutoField(primary_key=True, db_column='portfolio_id')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='user_id')
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, db_column='project_id')
    description = models.TextField(null=True, blank=True)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Portfolios'
        managed = False
        unique_together = ('user', 'project')


class UserEmbedding(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, db_column='user_id', to_field='user_id', related_name='embedding_profile')
    embedding = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'UserEmbeddings'
        managed = True # Django가 이 테이블을 관리합니다.

class ProjectEmbedding(models.Model):
    project = models.OneToOneField(Projects, on_delete=models.CASCADE, db_column='project_id', to_field='project_id', related_name='embedding_profile')
    embedding = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'ProjectEmbeddings'
        managed = True # Django가 이 테이블을 관리합니다.