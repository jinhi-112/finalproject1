from rest_framework import serializers
from typing import Optional
from django.contrib.auth.hashers import make_password
from .models import (
    User, 
    Projects, 
    ProjectApplicants, 
    Evaluations, 
    UserEmbedding, 
    MatchScores, 
)
from .ai_services import generate_embedding


# ----------------------------
# 회원가입 (User Registration)
# ----------------------------
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'name')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


# ----------------------------
# 사용자 기본 정보
# ----------------------------
class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_id', 'name', 'email', 
            'specialty', 'introduction',
            'is_profile_complete'
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        value = getattr(instance, 'specialty')
        ret['specialty'] = value.split(',') if value else []
        return ret


# ----------------------------
# 프로젝트 (Projects)
# ----------------------------
class ProjectSerializer(serializers.ModelSerializer):
    creator = UsersSerializer(read_only=True)
    user_matching_rate = serializers.SerializerMethodField()

    class Meta:
        model = Projects
        fields = [
            'project_id', 'creator', 
            'title', 'description', 'goal', 
            'tech_stack', 'recruitment_count', 
            'start_date', 'end_date', 
            'application_deadline', 'matching_rate', 
            'is_open', 'created_at',
            'user_matching_rate'
        ]
        read_only_fields = ['project_id', 'created_at']

    def get_user_matching_rate(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if hasattr(request, 'user_match_scores') and obj.project_id in request.user_match_scores:
                return round(request.user_match_scores[obj.project_id], 2)
            try:
                match_score = MatchScores.objects.get(user=request.user, project=obj)
                return round(match_score.score, 2)
            except MatchScores.DoesNotExist:
                pass
        return None

    def create(self, validated_data):
        return Projects.objects.create(**validated_data)


# ----------------------------
# 선택지 정의
# ----------------------------
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


# ----------------------------
# 사용자 프로필 (User Profile)
# ----------------------------
class UserProfileSerializer(serializers.ModelSerializer):
    available_region = serializers.MultipleChoiceField(
        choices=User.KOREAN_REGIONS, allow_empty=True, required=False
    )
    specialty = serializers.MultipleChoiceField(
        choices=SPECIALTY_CHOICES, allow_empty=True, required=False
    )
    tech_stack = serializers.MultipleChoiceField(
        choices=TECH_STACK_CHOICES, allow_empty=True, required=False
    )
    collaboration_tools = serializers.MultipleChoiceField(
        choices=COLLAB_TOOL_CHOICES, allow_empty=True, required=False
    )
    preferred_project_topics = serializers.MultipleChoiceField(
        choices=PROJECT_TOPIC_CHOICES, allow_empty=True, required=False
    )

    class Meta:
        model = User
        fields = [
            'name', 'birthdate', 'email', 'available_region', 'github_url',
            'portfolio_url', 'introduction', 'major', 'specialty', 'tech_stack',
            'collaboration_tools', 'experience_level', 'collaboration_style',
            'meeting_frequency', 'belbin_role', 'preferred_team_size',
            'preferred_project_topics', 'availability_period', 'is_profile_complete'
        ]
        read_only_fields = ['email']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        list_fields = ['available_region', 'specialty', 'tech_stack', 'collaboration_tools', 'preferred_project_topics']
        for field in list_fields:
            value = getattr(instance, field)
            ret[field] = value.split(',') if value else []
        return ret

    def update(self, instance, validated_data):
        list_fields = ['available_region', 'specialty', 'tech_stack', 'collaboration_tools', 'preferred_project_topics']
        for field in list_fields:
            if field in validated_data:
                validated_data[field] = ",".join(validated_data[field])

        validated_data['is_profile_complete'] = True
        instance = super().update(instance, validated_data)

        # 사용자 임베딩 재계산
        embedding_text = f"""{instance.introduction or ''} 
        전문 분야: {instance.specialty or ''} 
        기술: {instance.tech_stack or ''} 
        전공: {instance.major or ''} 
        경험: {instance.experience_level or ''} 
        협업 스타일: {instance.collaboration_style or ''} 
        선호 프로젝트: {instance.preferred_project_topics or ''}"""

        embedding_vector = generate_embedding(embedding_text)
        if embedding_vector:
            UserEmbedding.objects.update_or_create(
                user=instance,
                defaults={'embedding': embedding_vector}
            )

        # 기존 매칭 점수 삭제
        MatchScores.objects.filter(user=instance).delete()
        return instance


# ----------------------------
# 프로젝트 상세 (Detail View)
# ----------------------------
class ProjectDetailSerializer(ProjectSerializer):
    user_match_explanation = serializers.SerializerMethodField()
    user_match_scores = serializers.SerializerMethodField()
    applicant_count = serializers.SerializerMethodField()

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + [
            'user_match_explanation', 'user_match_scores', 'applicant_count'
        ]

    def get_user_match_explanation(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                match_score = MatchScores.objects.get(user=request.user, project=obj)
                return match_score.explanation
            except MatchScores.DoesNotExist:
                pass
        return None

    def get_user_match_scores(self, obj) -> Optional[dict]:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                match_score = MatchScores.objects.get(user=request.user, project=obj)
                return {
                    "tech": match_score.tech_score,
                    "personality": match_score.personality_score,
                    "experience": match_score.experience_score,
                }
            except MatchScores.DoesNotExist:
                pass
        return None

    def get_applicant_count(self, obj) -> int:
        return ProjectApplicants.objects.filter(project=obj).count()


# ----------------------------
# 지원자 관리 (Applicants)
# ----------------------------
#class ApplicantsSerializer(serializers.ModelSerializer):
    #applicant_name = serializers.CharField(source="user.name", read_only=True)
    #applicant_email = serializers.CharField(source="user.email", read_only=True)

    #class Meta:
        #model = Applicants
        #fields = [
            #"id",
            #"applicant_name",
            #"applicant_email",
            #"tech_match",
            #"exp_match",
            #"time_match",
            #"match_rate",
            #"motivation",
            #"status",
            #"hours",
            #"created_at",
        #]
