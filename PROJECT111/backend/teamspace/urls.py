from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, RegisterView, ProjectListView, UserProfileView, LogoutView, ProjectSearchView, MatchProjectUserView, ProjectDetailView, MatchedProjectListView, ProjectApplyView # Added ProjectApplyView
from . import views

router = DefaultRouter()

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-info/', UserProfileView.as_view(), name='user-info'),
    
    # Project related URLs
    path('projects/search/', ProjectSearchView.as_view(), name='project-search'),
    path('projects/<int:project_id>/apply/', ProjectApplyView.as_view(), name='project-apply'),
    path('projects/<int:project_id>/', ProjectDetailView.as_view(), name='project-detail'),
    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('projects/matched/', MatchedProjectListView.as_view(), name='matched-project-list'), # New matched project list endpoint
    path('projects/my/', views.my_projects, name='my_projects'),

    # Match related URLs
    path('match/project/<int:project_id>/', MatchProjectUserView.as_view(), name='match-project-user'),
]

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import ProjectSerializer
from .models import Projects

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_projects(request):
    user = request.user
    projects = Projects.objects.filter(creator=user)

    summary = {
        "active_projects": projects.filter(status="active").count(),
        "total_applicants": sum([p.projectapplicants_set.count() for p in projects]),
        "ai_candidates": 0,
        "total_views": sum([p.views for p in projects]),
    }

    serializer = ProjectSerializer(projects, many=True)
    return Response({"summary": summary, "projects": serializer.data})
