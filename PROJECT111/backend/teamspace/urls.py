from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import ProjectViewSet, login_view, RegisterView, match_project_users
from .views import LoginView, RegisterView, match_project_users, ProjectListView, UserProfileView, LogoutView, GetCSRFToken

router = DefaultRouter()

urlpatterns = [
    path('csrf/', GetCSRFToken.as_view(), name='csrf'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('user-info/', UserProfileView.as_view(), name='user-info'),
    
    # path('internal-api/match/projects/<int:project_id>/', match_project_users, name='match_project_users'),
    # path('api/projects/', ProjectListView.as_view(), name='project-list'),
    path('projects/', ProjectListView.as_view(), name='project-list'),

]
