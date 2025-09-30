from rest_framework import serializers
from django.contrib.auth.hashers import make_password # 비밀번호 해싱을 위해 임포트
from .models import Users, Projects 

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=50)

    class Meta:
        model = Users
        fields = ('email', 'password', 'name')

    # def create(self, validated_data):
    #     password = validated_data.pop('password')
    #     validated_data['password_hash'] = make_password(password)
    #     user = Users.objects.create(**validated_data)
    #     return user
    
    # 모델의 비밀번호 필드명이 'password'일 경우
    def create(self, validated_data):
    # validated_data에 있는 'password'를 자동으로 해싱하여 저장
        user = Users.objects.create_user(**validated_data) 
        return user

# (참고: Users 모델의 상세 정보가 필요하다면 UsersSerializer도 정의할 수 있습니다.)
class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        # 프로젝트 생성자의 이름과 ID만 필요하다고 가정
        fields = ['user_id', 'name', 'email']
        read_only_fields = ['user_id', 'name', 'email']


class ProjectSerializer(serializers.ModelSerializer):
    # creator 필드를 UsersSerializer로 중첩하여, 
    # 프로젝트 조회 시 생성자 정보도 함께 보여줍니다.
    creator = UsersSerializer(read_only=True)
    
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
            'tech_stack', 'is_open', 'created_at'
        ]
        # 'creator'는 read_only=True로 설정되어 GET 요청 시에만 상세 정보가 포함됩니다.
        # POST/PUT 요청 시에는 ViewSet에서 creator를 직접 설정하는 것이 일반적입니다.
        read_only_fields = ['project_id', 'created_at']

    def create(self, validated_data):
        # ViewSet에서 request.user를 받아 creator를 설정하므로,
        # validated_data에 creator가 이미 포함되어 있어야 합니다.
        # 예: validated_data['creator'] = self.context['request'].user
        return Projects.objects.create(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            'name', 'birthdate', 'email', 'available_region', 'github_url', 
            'portfolio_url', 'introduction', 'major', 'specialty', 'tech_stack',
            'collaboration_tools', 'experience_level', 'collaboration_style',
            'meeting_frequency', 'belbin_role', 'preferred_team_size',
            'preferred_project_topics', 'availability_period', 'is_profile_complete'
        ]
        read_only_fields = ['email'] # 이메일은 수정 불가

    def update(self, instance, validated_data):
        # 프로필이 한 번이라도 업데이트되면 is_profile_complete를 True로 설정
        validated_data['is_profile_complete'] = True
        return super().update(instance, validated_data)
    