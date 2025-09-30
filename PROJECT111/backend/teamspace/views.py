from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.generics import ListAPIView
from .models import Projects
from .serializers import ProjectSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotAuthenticated

from .models import Projects, Users, ProjectEmbedding, UserEmbedding
from .ai_services import calculate_similarity
from .serializers import (
    UsersSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)
import logging

logger = logging.getLogger(__name__)

# ----------------------
# CSRF
# ----------------------
@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'success': 'CSRF cookie set'})

# ----------------------
# 로그인 / 로그아웃 / 회원가입
# ----------------------

@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            serializer = UsersSerializer(user)
            return Response({
                "message": "Login successful",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "아이디나 비밀번호를 다시 확인해주세요"}, status=status.HTTP_400_BAD_REQUEST)


# LogoutView 수정 제안
class LogoutView(APIView):
    def post(self, request):
        logout(request)
        # 메시지를 로그아웃 성공으로 변경
        return Response({"message": "성공적으로 로그아웃 되었습니다."}, status=status.HTTP_200_OK)

class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 프로젝트 목록을 보여주는 API 뷰
class ProjectListView(ListAPIView):
    queryset = Projects.objects.all() # 데이터베이스에서 모든 프로젝트를 가져옵니다.
    serializer_class = ProjectSerializer # ProjectSerializer를 사용해 JSON으로 변환합니다.


# UserProfileView 수정 제안
@method_decorator(ensure_csrf_cookie, name='dispatch') # <--- 이 줄이 핵심입니다.
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

