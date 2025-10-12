from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework.generics import ListAPIView
from .models import Projects
from .serializers import ProjectSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Projects, User, ProjectEmbedding, UserEmbedding
from .ai_services import calculate_similarity
from .serializers import (
    UsersSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)
import logging

logger = logging.getLogger(__name__)

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
class ProjectListView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Projects.objects.all() # 데이터베이스에서 모든 프로젝트를 가져옵니다.
    serializer_class = ProjectSerializer # ProjectSerializer를 사용해 JSON으로 변환합니다.


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

