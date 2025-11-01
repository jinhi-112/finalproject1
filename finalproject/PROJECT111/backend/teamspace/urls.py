from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, RegisterView, ProjectListView, UserProfileView, LogoutView, ProjectSearchView, MatchProjectUserView, ProjectDetailView, MatchedProjectListView, ProjectApplyView, RecommendedProjectListView # Added ProjectApplyView

router = DefaultRouter()

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-info/', UserProfileView.as_view(), name='user-info'),
    
    # Project related URLs
    path('projects/search/', ProjectSearchView.as_view(), name='project-search'),
    path('projects/recommended/', RecommendedProjectListView.as_view(), name='project-recommended-list'),
    path('projects/<int:project_id>/apply/', ProjectApplyView.as_view(), name='project-apply'),
    path('projects/<int:project_id>/', ProjectDetailView.as_view(), name='project-detail'),
    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('projects/matched/', MatchedProjectListView.as_view(), name='matched-project-list'), # New matched project list endpoint

    # Match related URLs
    path('match/project/<int:project_id>/', MatchProjectUserView.as_view(), name='match-project-user'),
]
