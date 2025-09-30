from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import Projects, Users, ProjectEmbedding, UserEmbedding
from .ai_services import calculate_similarity, generate_match_explanation
from rest_framework.views import APIView

from django.contrib.auth import authenticate, login
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import UserProfileSerializer, UsersSerializer # UsersSerializer 추가

@api_view(['POST'])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        # UsersSerializer를 사용해 응답 데이터 생성
        serializer = UsersSerializer(user)
        return Response({
            "message": "Login successful",
            "user": serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

from .serializers import UserRegistrationSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def match_project_users(request, project_id):
    try:
        project = Projects.objects.get(project_id=project_id)
    except Projects.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        project_embedding_obj = ProjectEmbedding.objects.get(project=project)
        project_embedding = project_embedding_obj.embedding
    except ProjectEmbedding.DoesNotExist:
        return JsonResponse({'error': 'Project embedding not found'}, status=status.HTTP_404_NOT_FOUND)

    if not project_embedding:
        return JsonResponse({'error': 'Project embedding is empty'}, status=status.HTTP_400_BAD_REQUEST)

    all_users = Users.objects.all()
    match_results = []

    for user in all_users:
        if user.user_id == project.creator.user_id: # 프로젝트 생성자는 매칭에서 제외
            continue

        try:
            user_embedding_obj = UserEmbedding.objects.get(user=user)
            user_embedding = user_embedding_obj.embedding
        except UserEmbedding.DoesNotExist:
            continue # 임베딩이 없는 사용자는 건너뜀

        if not user_embedding:
            continue # 임베딩이 비어있는 사용자는 건너뜀

        similarity = calculate_similarity(project_embedding, user_embedding)

        match_results.append({
            'user_id': user.user_id,
            'user_name': user.name,
            'similarity_score': similarity,
        })

    match_results.sort(key=lambda x: x['similarity_score'], reverse=True)

    return JsonResponse({'project_id': project_id, 'matches': match_results})