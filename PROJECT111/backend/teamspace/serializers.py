from rest_framework import serializers
from typing import Optional
from django.contrib.auth.hashers import make_password
from .models import User, Projects, ProjectApplicants, Evaluations

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'name')

    def create(self, validated_data):
        # Use the new custom manager's create_user method which handles hashing
        user = User.objects.create_user(**validated_data)
        return user

# (참고: Users 모델의 상세 정보가 필요하다면 UsersSerializer도 정의할 수 있습니다.)
class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_id', 'name', 'email', 
            'specialty', 'introduction'
        ]


class ProjectSerializer(serializers.ModelSerializer):
    # creator 필드를 UsersSerializer로 중첩하여, 
    # 프로젝트 조회 시 생성자 정보도 함께 보여줍니다.
    creator = UsersSerializer(read_only=True)
    user_matching_rate = serializers.SerializerMethodField() # New field
    
    # 생성/수정 요청 시 creator_id를 받기 위한 필드 (선택 사항)
    # request에서 user를 직접 가져오는 것이 더 안전합니다.
    # creator_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Users.objects.all(), source='creator', write_only=True, required=False
    # )

    class Meta:
        model = Projects
        fields = [
            'project_id', 'creator', 
            'title', 'description', 'goal', 
            'tech_stack', 'recruitment_count', 'start_date', 'end_date', 'application_deadline', 'matching_rate', 'is_open', 'created_at',
            'user_matching_rate' # Include the new field
        ]
        # 'creator'는 read_only=True로 설정되어 GET 요청 시에만 상세 정보가 포함됩니다.
        # POST/PUT 요청 시에는 ViewSet에서 creator를 직접 설정하는 것이 일반적입니다.
        read_only_fields = ['project_id', 'created_at']

    def get_user_matching_rate(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Check if score is already passed in request context (from MatchedProjectListView)
            if hasattr(request, 'user_match_scores') and obj.project_id in request.user_match_scores:
                return round(request.user_match_scores[obj.project_id], 2)
            
            # Fallback: retrieve from MatchScores table
            from .models import MatchScores # Import here to avoid circular dependency
            try:
                match_score = MatchScores.objects.get(user=request.user, project=obj)
                return round(match_score.score, 2)
            except MatchScores.DoesNotExist:
                pass # No match score yet
        return None

    def create(self, validated_data):
        # ViewSet에서 request.user를 받아 creator를 설정하므로,
        # validated_data에 creator가 이미 포함되어 있어야 합니다.
        # 예: validated_data['creator'] = self.context['request'].user
        return Projects.objects.create(**validated_data)


# Define choices at the module level
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

class UserProfileSerializer(serializers.ModelSerializer):
    # Fields that handle list-to-string conversion
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
        """Convert comma-separated strings from model to lists for API output."""
        ret = super().to_representation(instance)
        list_fields = ['available_region', 'specialty', 'tech_stack', 'collaboration_tools', 'preferred_project_topics']
        for field in list_fields:
            value = getattr(instance, field)
            if value:
                ret[field] = value.split(',')
            else:
                ret[field] = []
        return ret

    def update(self, instance, validated_data):
        """Convert lists from API input to comma-separated strings for model."""
        list_fields = ['available_region', 'specialty', 'tech_stack', 'collaboration_tools', 'preferred_project_topics']
        for field in list_fields:
            if field in validated_data:
                setattr(instance, field, ",".join(validated_data.pop(field)))

        # Set profile completion flag
        validated_data['is_profile_complete'] = True
        return super().update(instance, validated_data)


class ProjectDetailSerializer(ProjectSerializer):
    user_match_explanation = serializers.SerializerMethodField()
    user_match_scores = serializers.SerializerMethodField()
    applicant_count = serializers.SerializerMethodField()

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['user_match_explanation', 'user_match_scores', 'applicant_count']

    def get_user_match_explanation(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from .models import MatchScores # Import here to avoid circular dependency
            try:
                match_score = MatchScores.objects.get(user=request.user, project=obj)
                return match_score.explanation
            except MatchScores.DoesNotExist:
                pass
        return None

    def get_user_match_scores(self, obj) -> Optional[dict]:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from .models import MatchScores # Import here to avoid circular dependency
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
