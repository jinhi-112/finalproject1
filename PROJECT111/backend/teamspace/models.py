
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    birthdate = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # --- 추가 정보 필드 ---
    KOREAN_REGIONS = [
        ('SEOUL', '서울특별시'),
        ('BUSAN', '부산광역시'),
        ('DAEGU', '대구광역시'),
        ('INCHEON', '인천광역시'),
        ('GWANGJU', '광주광역시'),
        ('DAEJEON', '대전광역시'),
        ('ULSAN', '울산광역시'),
        ('SEJONG', '세종특별자치시'),
        ('GYEONGGI', '경기도'),
        ('GANGWON', '강원도'),
        ('CHUNGCHEONGBUK', '충청북도'),
        ('CHUNGCHEONGNAM', '충청남도'),
        ('JEOLLABUK', '전라북도'),
        ('JEOLLANAM', '전라남도'),
        ('GYEONGSANGBUK', '경상북도'),
        ('GYEONGSANGNAM', '경상남도'),
        ('JEJU', '제주특별자치도'),
    ]
    available_region = models.TextField(null=True, blank=True)
    github_url = models.URLField(max_length=200, null=True, blank=True)
    portfolio_url = models.URLField(max_length=200, null=True, blank=True)
    introduction = models.TextField(max_length=150, null=True, blank=True)

    MAJOR_CHOICES = [
        ('PROGRAMMING', '개발/프로그래밍'),
        ('DATA_AI', '데이터/AI'),
        ('SECURITY_NET', '보안/네트워크'),
        ('DESIGN', '디자인/기획'),
        ('NON_MAJOR', '비전공자/기타')
    ]
    major = models.CharField(max_length=20, choices=MAJOR_CHOICES, null=True, blank=True)
    specialty = models.CharField(max_length=255, null=True, blank=True)
    tech_stack = models.CharField(max_length=255, null=True, blank=True)
    collaboration_tools = models.CharField(max_length=255, null=True, blank=True)
    EXPERIENCE_CHOICES = [('NONE', '없음'), ('ONCE', '1회'), ('FEW', '2~3회'), ('MANY', '4회 이상')]
    experience_level = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES, null=True, blank=True)

    COLLABORATION_STYLE_CHOICES = [('OFFLINE', '오프라인 중심'), ('ONLINE', '온라인 중심'), ('HYBRID', '혼합')]
    collaboration_style = models.CharField(max_length=10, choices=COLLABORATION_STYLE_CHOICES, null=True, blank=True)
    MEETING_FREQUENCY_CHOICES = [('WEEKLY_1', '주 1회'), ('WEEKLY_2_3', '주 2~3회'), ('DAILY', '매일 가능'), ('PROJECT_ONLY', '프로젝트 중심만 가능')]
    meeting_frequency = models.CharField(max_length=20, choices=MEETING_FREQUENCY_CHOICES, null=True, blank=True)
    BELBIN_CHOICES = [('PL', 'PL - 아이디어 뱅크'), ('RI', 'RI - 자원탐색자'), ('CO', 'CO - 조정자'), ('SH', 'SH - 추진자'), ('ME', 'ME - 평가자'), ('TW', 'TW - 팀 워커'), ('IMP', 'IMP - 실행자'), ('CF', 'CF - 완성자'), ('SP', 'SP - 전문가')]
    belbin_role = models.CharField(max_length=3, choices=BELBIN_CHOICES, null=True, blank=True)

    TEAM_SIZE_CHOICES = [('SMALL', '2~3명'), ('MEDIUM', '4~5명'), ('LARGE', '6명 이상도 가능/기타')]
    preferred_team_size = models.CharField(max_length=10, choices=TEAM_SIZE_CHOICES, null=True, blank=True)
    preferred_project_topics = models.CharField(max_length=255, null=True, blank=True)
    AVAILABILITY_CHOICES = [('SHORT', '단기: 1달 이내'), ('MEDIUM', '중기: 2~3달'), ('LONG', '장기: 3달 이상/기타')]
    availability_period = models.CharField(max_length=10, choices=AVAILABILITY_CHOICES, null=True, blank=True)

    is_profile_complete = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    class Meta:
        db_table = 'Users'
        managed = True

    def __str__(self):
        return self.email

class Skills(models.Model):
    skill_id = models.AutoField(primary_key=True, db_column='skill_id')
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'Skills'
        managed = True

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

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    skill = models.ForeignKey(Skills, on_delete=models.CASCADE, db_column='skill_id')
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES)

    class Meta:
        db_table = 'UserSkills'
        managed = True
        unique_together = ('user', 'skill')


class Projects(models.Model):
    project_id = models.AutoField(primary_key=True, db_column='project_id')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, db_column='creator_id')
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    goal = models.TextField(null=True, blank=True)
    tech_stack = models.TextField(null=True, blank=True)
    recruitment_count = models.IntegerField(default=0)  # 모집인원
    start_date = models.DateField(null=True, blank=True)  # 기간 (시작)
    end_date = models.DateField(null=True, blank=True)  # 기간 (종료)
    application_deadline = models.DateField(null=True, blank=True) # 지원 마감일
    matching_rate = models.FloatField(null=True, blank=True)  # 매칭률
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Projects'
        managed = True

    def __str__(self):
        return self.title


class Teams(models.Model):
    team_id = models.AutoField(primary_key=True, db_column='team_id')
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, db_column='project_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Teams'
        managed = True


class TeamMembers(models.Model):
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, db_column='team_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    role = models.CharField(max_length=50)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'TeamMembers'
        managed = True
        unique_together = ('team', 'user')


class MatchScores(models.Model):
    match_id = models.AutoField(primary_key=True, db_column='match_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, db_column='project_id')
    score = models.FloatField()
    tech_score = models.IntegerField(default=0)
    personality_score = models.IntegerField(default=0)
    experience_score = models.IntegerField(default=0)
    explanation = models.TextField(null=True, blank=True) # New field for GPT explanation
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'MatchScores'
        managed = True
        unique_together = ('user', 'project')


class Evaluations(models.Model):
    evaluation_id = models.AutoField(primary_key=True, db_column='evaluation_id')
    evaluator = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column='evaluator_id', related_name='given_evaluations')
    evaluatee = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column='evaluatee_id', related_name='received_evaluations')
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, db_column='team_id')
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback = models.TextField(null=True, blank=True)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Evaluations'
        managed = True
        unique_together = ('evaluator', 'evaluatee', 'team')


class Portfolios(models.Model):
    portfolio_id = models.AutoField(primary_key=True, db_column='portfolio_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, db_column='project_id')
    description = models.TextField(null=True, blank=True)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Portfolios'
        managed = True
        unique_together = ('user', 'project')


class UserEmbedding(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user_id', to_field='user_id', related_name='embedding_profile')
    embedding = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'UserEmbeddings'
        managed = True 

class ProjectEmbedding(models.Model):
    project = models.OneToOneField(Projects, on_delete=models.CASCADE, db_column='project_id', to_field='project_id', related_name='embedding_profile')
    embedding = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'ProjectEmbeddings'
        managed = True


class ProjectApplicants(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ProjectApplicants'
        unique_together = ('user', 'project')
