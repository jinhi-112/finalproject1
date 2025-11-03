from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    clear_match_scores,
    LoginView, 
    RegisterView, 
    ProjectListView, 
    UserProfileView, 
    LogoutView, 
    ProjectSearchView, 
    MatchProjectUserView, 
    ProjectDetailView, 
    MatchedProjectListView, 
    ProjectApplyView, 
    RecommendedProjectListView,
    MyProjectListView,
    RecommendTeammatesView,
    ProposeToProjectView,
    NotificationListView,
    NotificationReadView,
    ProjectApplicantsListView,
    UpdateApplicantStatusView # Import
)

router = DefaultRouter()

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-info/', UserProfileView.as_view(), name='user-info'),
    
    # Project related URLs
    path('projects/my/', MyProjectListView.as_view(), name='my-project-list'),
    path('projects/search/', ProjectSearchView.as_view(), name='project-search'),
    path('projects/recommended/', RecommendedProjectListView.as_view(), name='project-recommended-list'),
    path('projects/<int:project_id>/recommend-teammates/', RecommendTeammatesView.as_view(), name='recommend-teammates'),
    path('projects/<int:project_id>/propose/', ProposeToProjectView.as_view(), name='propose-to-project'),
    path('projects/<int:project_id>/applicants/', ProjectApplicantsListView.as_view(), name='project-applicants-list'),
    path('projects/<int:project_id>/apply/', ProjectApplyView.as_view(), name='project-apply'),
    path('projects/<int:project_id>/', ProjectDetailView.as_view(), name='project-detail'),
    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('projects/matched/', MatchedProjectListView.as_view(), name='matched-project-list'),

    # Applicant related URLs
    path('project-applicants/<int:applicant_id>/status/', UpdateApplicantStatusView.as_view(), name='update-applicant-status'),

    # Match related URLs
    path('match/project/<int:project_id>/', MatchProjectUserView.as_view(), name='match-project-user'),

    # Notification related URLs
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:notification_id>/read/', NotificationReadView.as_view(), name='notification-read'),
    path('clear-match-scores/', clear_match_scores, name='clear_match_scores'),
]
