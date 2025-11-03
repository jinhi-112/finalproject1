from django.http import JsonResponse
from django.http import HttpResponse
from .models import MatchScores
from rest_framework.decorators import api_view

@api_view(['GET'])
def clear_match_scores(request):
    count, _ = MatchScores.objects.all().delete()
    return HttpResponse(f"Deleted {count} MatchScores entries.")
from rest_framework.response import Response
from rest_framework import status # Added status
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404, RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Projects, User, ProjectEmbedding, UserEmbedding, MatchScores, ProjectApplicants
from .ai_services import MatchService # Import MatchService
from .ai_services import calculate_similarity, generate_match_explanation, generate_embedding # Added generate_embedding
from .serializers import (
    UsersSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    ProjectSerializer,
    ProjectDetailSerializer,
    RecommendedProjectSerializer,
    NotificationSerializer # Added NotificationSerializer
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

        # Get data from request
        role = request.data.get('role')
        motivation = request.data.get('motivation')
        available_time = request.data.get('available_time')

        # Use update_or_create to handle application and save data
        applicant, created = ProjectApplicants.objects.update_or_create(
            user=user,
            project=project,
            defaults={
                'role': role,
                'motivation': motivation,
                'available_time': available_time,
                'status': '검토 대기' # Set status on new application
            }
        )

        if not created:
            return Response({"message": "지원 정보가 성공적으로 업데이트되었습니다."}, status=status.HTTP_200_OK)

        return Response({"message": "프로젝트에 성공적으로 지원했습니다."}, status=status.HTTP_201_CREATED)


# ----------------------
# 로그인 / 로그아웃 / 회원가입
# ----------------------

from django.contrib.auth import authenticate # Added authenticate
from .tasks import precompute_matches_for_user_task

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # Trigger background task to pre-compute matches
            precompute_matches_for_user_task.delay(user.pk)
            
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

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class MyProjectListView(ListAPIView):
    """
    View to list projects created by the currently authenticated user,
    with custom data structure including a summary.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer # Still useful for base serialization

    def get_queryset(self):
        """
        This view should return a list of all the projects
        for the currently authenticated user.
        """
        user = self.request.user
        return Projects.objects.filter(creator=user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # --- Calculate Summary Data ---
        active_projects = queryset.filter(is_open=True).count()
        # Annotate each project with its applicant count
        projects_with_applicants = queryset.annotate(num_applicants=Count('projectapplicants'))
        total_applicants = sum(p.num_applicants for p in projects_with_applicants)
        
        summary_data = {
            "active_projects": active_projects,
            "total_applicants": total_applicants,
        }

        # --- Prepare Project List Data ---
        projects_data = []
        for project in projects_with_applicants: # Use the annotated queryset
            # Base data from serializer
            serializer = self.get_serializer(project)
            data = serializer.data
            
            # Add missing/custom fields
            data['status'] = 'active' if project.is_open else 'completed'
            data['applicants_count'] = project.num_applicants # Use the annotated count
            data['ai_recommended_count'] = 0 # Mocked
            data['views'] = 0 # Mocked
            
            projects_data.append(data)

        # --- Construct Final Response ---
        response_data = {
            "summary": summary_data,
            "projects": projects_data
        }
        
        return Response(response_data)

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


class ProjectDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Projects.objects.all()
    serializer_class = ProjectDetailSerializer
    lookup_field = 'project_id'

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.is_authenticated:
            MatchService.get_or_create_match_score(user, obj)
        return obj

    def perform_destroy(self, instance):
        if instance.creator != self.request.user:
            raise PermissionDenied("You do not have permission to delete this project.")
        instance.delete()


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


class RecommendedProjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if not user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        # Get recommended projects data from the service
        recommended_projects_data = MatchService.get_recommended_projects(user)

        # Serialize the data
        project_serializer = RecommendedProjectSerializer(recommended_projects_data, many=True, context={'request': request})

        # Get user profile for the response
        user_serializer = UserProfileSerializer(user)

        return Response({
            'user_profile': user_serializer.data,
            'recommended_projects': project_serializer.data
        })



class RecommendTeammatesView(APIView):
    """
    Recommends teammates for a given project based on embedding similarity.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, *args, **kwargs):
        # 1. Get project and verify ownership
        project = get_object_or_404(Projects, pk=project_id)
        if project.creator != request.user:
            return Response(
                {"error": "You are not the creator of this project."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            project_embedding_obj = ProjectEmbedding.objects.get(project=project)
            project_embedding = project_embedding_obj.embedding
        except ProjectEmbedding.DoesNotExist:
            return Response(
                {"error": "Project embedding not found. The project may not have enough information."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Get candidate users (all users except creator and existing applicants)
        existing_applicant_ids = ProjectApplicants.objects.filter(project=project).values_list('user_id', flat=True)
        
        candidate_users = User.objects.exclude(pk=request.user.pk).exclude(pk__in=existing_applicant_ids)
        
        all_user_embeddings = UserEmbedding.objects.filter(user__in=candidate_users).select_related('user')

        # 3. Calculate match scores
        match_results = []
        for user_embedding_obj in all_user_embeddings:
            user = user_embedding_obj.user
            user_embedding = user_embedding_obj.embedding

            if not user_embedding:
                continue

            similarity = calculate_similarity(project_embedding, user_embedding)
            
            # We can add more data to the response if needed
            match_results.append({
                'user': UsersSerializer(user).data,
                'score': similarity * 100 # As percentage
            })

        # 4. Sort and return top 10
        match_results.sort(key=lambda x: x['score'], reverse=True)

        return Response(match_results[:10])

class ProposeToProjectView(APIView):
    """
    Allows a project creator to send a project participation proposal to a user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id, *args, **kwargs):
        # 1. Get project and verify ownership
        project = get_object_or_404(Projects, pk=project_id)
        if project.creator != request.user:
            return Response(
                {"error": "You are not the creator of this project."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 2. Get target user from request body
        target_user_id = request.data.get('user_id')
        if not target_user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        target_user = get_object_or_404(User, pk=target_user_id)

        # 3. Check for duplicate proposals
        existing_notification = Notifications.objects.filter(
            recipient=target_user,
            related_project=project,
            notification_type='PROJECT_INVITE'
        ).exists()

        if existing_notification:
            return Response({"message": "A proposal has already been sent to this user for this project."}, status=status.HTTP_409_CONFLICT)

        # 4. Create notification
        message = f"'{project.creator.name}'님이 '{project.title}' 프로젝트에 참여를 제안했습니다."
        
        Notifications.objects.create(
            recipient=target_user,
            sender=request.user,
            related_project=project,
            notification_type='PROJECT_INVITE',
            message=message
        )

        return Response({"message": "Project proposal sent successfully."}, status=status.HTTP_201_CREATED)

class NotificationListView(ListAPIView):
    """
    Lists all notifications for the currently authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        """
        This view should return a list of all notifications
        for the currently authenticated user.
        """
        return Notifications.objects.filter(recipient=self.request.user)

class NotificationReadView(APIView):
    """
    Marks a specific notification as read.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id, *args, **kwargs):
        notification = get_object_or_404(Notifications, pk=notification_id)

        # Check if the user is the recipient of the notification
        if notification.recipient != request.user:
            return Response(
                {"error": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        notification.is_read = True
        notification.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

class ProjectApplicantsListView(APIView):
    """
    View to list applicants for a given project.
    Only the project creator can access this view.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, *args, **kwargs):
        # 1. Get project and verify ownership
        project = get_object_or_404(Projects, pk=project_id)
        if project.creator != request.user:
            return Response(
                {"error": "You are not the creator of this project."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 2. Get all applicants for the project
        applicants = ProjectApplicants.objects.filter(project=project).select_related('user')

        # 3. Calculate summary
        summary = {
            'pending': applicants.filter(status='검토 대기').count(),
            'reviewed': applicants.filter(status='검토 완료').count(),
            'approved': applicants.filter(status='승인').count(),
            'rejected': applicants.filter(status='거절').count(),
        }

        # 4. Serialize applicant data
        serializer = ProjectApplicantSerializer(applicants, many=True, context={'request': request})
        
        # Manual transformation to match frontend expectations
        serialized_applicants = []
        for item in serializer.data:
            applicant_data = {
                'id': item['id'], # Use the ProjectApplicants PK as the main ID
                'name': item['user']['name'],
                'role': item['role'], # Use real role
                'status': item['status'],
                'date': item['applied_at'],
                'hours': item['available_time'], # Use real available_time
                'motivation': item['motivation'], # Use real motivation
                'skills': item['user']['specialty'], # Mapping specialty to skills
                'match_rate': item['match_scores']['match_rate'],
                'tech_match': item['match_scores']['tech_match'],
                'exp_match': item['match_scores']['exp_match'],
                'time_match': item['match_scores']['time_match'],
            }
            serialized_applicants.append(applicant_data)

        # 5. Construct final response
        response_data = {
            "summary": summary,
            "applicants": serialized_applicants
        }

        return Response(response_data)

class UpdateApplicantStatusView(APIView):
    """
    Updates the status of a project applicant.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, applicant_id, *args, **kwargs):
        # 1. Get the applicant object
        applicant = get_object_or_404(ProjectApplicants, pk=applicant_id)

        # 2. Verify ownership/permission
        if applicant.project.creator != request.user:
            return Response(
                {"error": "You do not have permission to change this applicant's status."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 3. Get and validate new status
        new_status = request.data.get('status')
        valid_statuses = [choice[0] for choice in ProjectApplicants.STATUS_CHOICES]
        if not new_status or new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Must be one of {valid_statuses}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Update and save
        applicant.status = new_status
        applicant.save()

        # 5. Return success response with the updated applicant data
        serializer = ProjectApplicantSerializer(applicant)
        return Response(serializer.data)