from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import ProjectViewSet, login_view, RegisterView, match_project_users
from .views import login_view, RegisterView, match_project_users, UserProfileView # 변경

router = DefaultRouter()
# router.register(r'projects', ProjectViewSet, basename='project') # 주석 처리

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('user-info/', UserProfileView.as_view(), name='user-info'), # 추가
    path('internal-api/match/projects/<int:project_id>/', match_project_users, name='match_project_users'),
    # path('', include(router.urls)), # 주석 처리
]
