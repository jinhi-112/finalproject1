from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from django.db.models import Case, When

from .models import (
    Projects, 
    User, 
    ProjectEmbedding, 
    UserEmbedding, 
    MatchScores, 
    ProjectApplicants, 
    Applicants
)
from .ai_services import MatchService, calculate_similarity, generate_match_explanation, generate_embedding
from .serializers import (
    UsersSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    ProjectSerializer,
    ProjectDetailSerializer,
    ApplicantsSerializer
)
from .filters import ProjectFilter
import logging

logger = logging.getLogger(__name__)

# ----------------------
# 지원하기
# ----------------------
class ProjectApplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        project = get_object_or_404(Projects, pk=project_id)
        user = request.user

        applicant, created = ProjectApplicants.objects.get_or_create(
            user=user,
            project=project
        )

        if not created:
            return Response({"message": "이미 이 프로젝트에 지원했습니다."}, status=status.HTTP_409_CONFLICT)

        return Response({"message": "프로젝트에 성공적으로 지원했습니다."}, status=status.HTTP_201_CREATED)


# ----------------------
# 지원자 관리 (NEW)
# ----------------------
class ProjectApplicantsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        """
        프로젝트별 지원자 목록 조회
        """
        try:
            project = Projects.objects.get(project_id=project_id, creator=request.user)
        except Projects.DoesNotExist:
            return Response({"error": "해당 프로젝트를 찾을 수 없거나 접근 권한이 없습니다."}, status=404)

        applicants = Applicants.objects.filter(project=project).select_related("user")
        serializer = ApplicantsSerializer(applicants, many=True)
        return Response(serializer.data, status=200)


# ----------------------
# 로그인 / 로그아웃 / 회원가입
# ----------------------
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            serializer = UsersSerializer(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serializer.data
            })
        else:
            return Response({"error": "아이디나 비밀번호를 다시 확인해주세요"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "성공적으로 로그아웃 되었습니다. 클라이언트에서 토큰을 삭제해주세요."}, status=status.HTTP_200_OK)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------
# 프로젝트 목록 / 검색 / 상세
# ----------------------
class ProjectResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProjectListView(ListCreateAPIView):
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = ProjectResultsPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class ProjectSearchView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProjectFilter
    ordering_fields = ['created_at', 'title', 'recruitment_count']
    pagination_class = ProjectResultsPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        filter = self.filterset_class(self.request.query_params, queryset=queryset)
        return filter.qs


class ProjectDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Projects.objects.all()
    serializer_class = ProjectDetailSerializer
    lookup_field = 'project_id'

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.is_authenticated:
            MatchService.get_or_create_match_score(user, obj)
        return obj


# ----------------------
# 추천 프로젝트 리스트
# ----------------------
class MatchedProjectListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    pagination_class = ProjectResultsPagination

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Projects.objects.none()

        recommended_projects_data = MatchService.get_recommended_projects(user)

        sorted_project_ids = []
        for item in recommended_projects_data:
            sorted_project_ids.append(item['project'].project_id)

        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_project_ids)])
        queryset = Projects.objects.filter(project_id__in=sorted_project_ids).order_by(preserved)
        return queryset


# ----------------------
# 개별 매칭 점수 계산
# ----------------------
class MatchProjectUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        user = request.user
        project = get_object_or_404(Projects, project_id=project_id)

        try:
            user_embedding_obj = UserEmbedding.objects.get(user=user)
            project_embedding_obj = ProjectEmbedding.objects.get(project=project)
        except (UserEmbedding.DoesNotExist, ProjectEmbedding.DoesNotExist):
            return Response({"error": "임베딩을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        user_embedding = user_embedding_obj.embedding
        project_embedding = project_embedding_obj.embedding
        similarity_score = calculate_similarity(user_embedding, project_embedding) * 100

        user_data = {
            "name": user.name,
            "introduction": user.introduction,
            "tech_stack": user.tech_stack,
        }
        project_data = {
            "title": project.title,
            "description": project.description,
            "goal": project.goal,
        }
        explanation = generate_match_explanation(user_data, project_data, similarity_score)

        MatchScores.objects.update_or_create(
            user=user,
            project=project,
            defaults={'score': similarity_score, 'explanation': explanation}
        )

        return Response({
            "user_id": user.user_id,
            "project_id": project.project_id,
            "score": round(similarity_score, 2),
            "explanation": explanation,
        }, status=status.HTTP_200_OK)


# ----------------------
# 사용자 프로필
# ----------------------
class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ----------------------
# 프로젝트에 매칭된 사용자 보기
# ----------------------
@api_view(['GET'])
def match_project_users(request, project_id):
    project = get_object_or_404(Projects, project_id=project_id)

    try:
        project_embedding = ProjectEmbedding.objects.get(project=project).embedding
    except ProjectEmbedding.DoesNotExist:
        return Response({"error": "프로젝트 임베딩을 찾을 수 없습니다."}, status=404)

    all_user_embeddings = UserEmbedding.objects.select_related('user').all()

    match_results = []
    for user_embedding_obj in all_user_embeddings:
        user = user_embedding_obj.user
        if user.user_id == project.creator.user_id:
            continue
        similarity = calculate_similarity(project_embedding, user_embedding_obj.embedding)
        match_results.append({
            'user_id': user.user_id,
            'user_name': user.name,
            'similarity_score': similarity,
        })

    match_results.sort(key=lambda x: x['similarity_score'], reverse=True)
    return Response({'project_id': project_id, 'matches': match_results})


class MyProjectsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """현재 로그인한 사용자가 생성한 프로젝트 목록 + 요약 정보 반환"""
        projects = Projects.objects.filter(creator=request.user).order_by('-created_at')
        serializer = ProjectSerializer(projects, many=True, context={'request': request})

        # 요약 데이터 생성
        summary = {
            "active_projects": projects.filter(status="active").count(),
            "total_applicants": sum(getattr(p, "applicants_count", 0) for p in projects),
            "ai_candidates": sum(getattr(p, "ai_recommended_count", 0) for p in projects),
            "total_views": sum(getattr(p, "views", 0) for p in projects),
        }

        return Response({
            "summary": summary,
            "projects": serializer.data
        })
