from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework.generics import ListAPIView
from .models import Projects
from .serializers import ProjectSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, get_object_or_404, RetrieveAPIView # Added RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Projects, User, ProjectEmbedding, UserEmbedding, MatchScores, ProjectApplicants
from .ai_services import MatchService # Import MatchService
from .ai_services import calculate_similarity, generate_match_explanation, generate_embedding # Added generate_embedding
from .serializers import (
    UsersSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    ProjectDetailSerializer, # Added ProjectDetailSerializer
)
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

        # 이미 지원했는지 확인
        applicant, created = ProjectApplicants.objects.get_or_create(
            user=user,
            project=project
        )

        if not created:
            return Response({"message": "이미 이 프로젝트에 지원했습니다." }, status=status.HTTP_409_CONFLICT)

        return Response({"message": "프로젝트에 성공적으로 지원했습니다."}, status=status.HTTP_201_CREATED)


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
        # For stateless JWT, logout is handled client-side by deleting tokens.
        # Optionally, you can implement token blacklisting here if needed.
        return Response({"message": "성공적으로 로그아웃 되었습니다. 클라이언트에서 토큰을 삭제해주세요."}, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 프로젝트 목록을 보여주는 API 뷰
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter # Added OrderingFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination # Import PageNumberPagination
from .filters import ProjectFilter # Import ProjectFilter

# ... other imports ...

class ProjectResultsPagination(PageNumberPagination):
    page_size = 10 # Number of projects per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProjectListView(ListCreateAPIView):
    # permission_classes = [IsAuthenticated] # Remove this line
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = ProjectResultsPagination # Add pagination

    def get_permissions(self): # Added get_permissions method
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class ProjectSearchView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Projects.objects.all() # This will be the base queryset
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter] # Keep these for ordering
    filterset_class = ProjectFilter
    ordering_fields = ['created_at', 'title', 'recruitment_count']
    pagination_class = ProjectResultsPagination

    def get_queryset(self):
        queryset = super().get_queryset() # Get the base queryset (Projects.objects.all())
        filter = self.filterset_class(self.request.query_params, queryset=queryset)
        return filter.qs


class ProjectDetailView(RetrieveAPIView):
    permission_classes = [AllowAny] # Allow anyone to view project details
    queryset = Projects.objects.all()
    serializer_class = ProjectDetailSerializer # Changed to ProjectDetailSerializer
    lookup_field = 'project_id' # Use project_id from URL as lookup field

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.is_authenticated:
            # Ensure match score and explanation are generated/updated
            MatchService.get_or_create_match_score(user, obj)
        return obj


from .ai_services import MatchService # Import MatchService

class MatchedProjectListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    pagination_class = ProjectResultsPagination

    def get_queryset(self):
        user = self.request.user
        logger.info(f"MatchedProjectListView: Fetching projects for user {user.email}")
        if not user.is_authenticated:
            logger.warning("MatchedProjectListView: User not authenticated, returning empty queryset.")
            return Projects.objects.none()

        # Use MatchService to get recommended projects
        recommended_projects_data = MatchService.get_recommended_projects(user)
        logger.info(f"MatchedProjectListView: MatchService returned {len(recommended_projects_data)} projects for user {user.email}")
        
        # Extract sorted projects and prepare context for serializer
        sorted_project_ids = []
        user_match_scores = {}
        for item in recommended_projects_data:
            project = item['project']
            score = item['score']
            sorted_project_ids.append(project.project_id)
            user_match_scores[project.project_id] = score
        
        # Pass the calculated scores to the serializer context
        self.request.user_match_scores = user_match_scores

        # Fetch projects in the correct order
        from django.db.models import Case, When
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_project_ids)])
        queryset = Projects.objects.filter(project_id__in=sorted_project_ids).order_by(preserved)
        
        logger.info(f"MatchedProjectListView: Returning {queryset.count()} projects after sorting.")
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Ensure user_match_scores is passed to the serializer
        context['request'] = self.request # Pass request to serializer context
        return context


class MatchProjectUserView(APIView):
    permission_classes = [IsAuthenticated] # Only authenticated users can request a match

    def get(self, request, project_id):
        user = request.user
        project = get_object_or_404(Projects, project_id=project_id)

        # 1. Retrieve Embeddings
        try:
            user_embedding_obj = UserEmbedding.objects.get(user=user)
            project_embedding_obj = ProjectEmbedding.objects.get(project=project)
        except (UserEmbedding.DoesNotExist, ProjectEmbedding.DoesNotExist):
            return Response(
                {"error": "사용자 또는 프로젝트 임베딩을 찾을 수 없습니다. 프로필/프로젝트 정보가 충분한지 확인해주세요."},
                status=status.HTTP_404_NOT_FOUND
            )

        user_embedding = user_embedding_obj.embedding
        project_embedding = project_embedding_obj.embedding

        if not user_embedding or not project_embedding:
            return Response(
                {"error": "임베딩 데이터가 유효하지 않습니다. 임베딩 생성에 문제가 있을 수 있습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Calculate Similarity
        similarity_score = calculate_similarity(user_embedding, project_embedding) * 100 # Convert to percentage

        # 3. Generate Explanation using GPT
        # Prepare data for GPT prompt
        user_data = {
            "name": user.name,
            "introduction": user.introduction,
            "tech_stack": user.tech_stack,
            "major": user.major,
            "experience_level": user.experience_level,
            "collaboration_style": user.collaboration_style,
            "preferred_project_topics": user.preferred_project_topics,
        }
        project_data = {
            "title": project.title,
            "description": project.description,
            "goal": project.goal,
            "tech_stack": project.tech_stack,
            "recruitment_count": project.recruitment_count,
        }
        explanation = generate_match_explanation(user_data, project_data, similarity_score)

        # 4. Save Match Score and Explanation
        match_score_obj, created = MatchScores.objects.update_or_create(
            user=user,
            project=project,
            defaults={'score': similarity_score, 'explanation': explanation}
        )

        return Response({
            "user_id": user.user_id,
            "project_id": project.project_id,
            "score": round(similarity_score, 2),
            "explanation": explanation,
            "status": "매칭 점수 및 설명이 성공적으로 생성/업데이트되었습니다." if created else "매칭 점수 및 설명이 업데이트되었습니다."
        }, status=status.HTTP_200_OK)




# UserProfileView 수정 제안
class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # 이 로직은 permission_classes가 이미 처리해주므로 삭제 가능
        # if not self.request.user.is_authenticated:
        #     raise NotAuthenticated()
        return self.request.user
# ----------------------
# 프로젝트-사용자 매칭
# ----------------------

# match_project_users 성능 개선 제안
@api_view(['GET'])
def match_project_users(request, project_id):
    # ... (프로젝트 조회 로직은 동일) ...

    # 모든 UserEmbedding을 가져오면서 user 정보도 함께 로드 (DB 조회 1번)
    all_user_embeddings = UserEmbedding.objects.select_related('user').all()

    match_results = []
    for user_embedding_obj in all_user_embeddings:
        user = user_embedding_obj.user
        user_embedding = user_embedding_obj.embedding

        if user.user_id == project.creator.user_id:
            continue
        if not user_embedding:
            continue

        similarity = calculate_similarity(project_embedding, user_embedding)
        match_results.append({
            'user_id': user.user_id,
            'user_name': user.name,
            'similarity_score': similarity,
        })

    match_results.sort(key=lambda x: x['similarity_score'], reverse=True)

    # DRF의 Response 객체를 사용하는 것이 일관성에 좋습니다.
    return Response({'project_id': project_id, 'matches': match_results})

# ----------------------
# 내 프로젝트 관리 페이지용 API
# ----------------------
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_projects(request):
    user = request.user
    projects = Projects.objects.filter(creator=user).order_by('-created_at')

    data = []
    for p in projects:
        data.append({
            "project_id": p.project_id,
            "title": p.title,
            "description": p.description,
            "tech_stack": p.tech_stack,
            "recruitment_count": p.recruitment_count,
            "status": p.status,
            "views": p.views if hasattr(p, "views") else 0,
            "applicants_count": p.projectapplicants_set.count() if hasattr(p, "projectapplicants_set") else 0,
            "ai_recommended_count": MatchScores.objects.filter(project=p).count(),
        })

    summary = {
        "active_projects": projects.filter(status="active").count(),
        "total_applicants": sum([d["applicants_count"] for d in data]),
        "ai_candidates": sum([d["ai_recommended_count"] for d in data]),
        "total_views": sum([d["views"] for d in data]),
    }

    return Response({
        "summary": summary,
        "projects": data
    })



