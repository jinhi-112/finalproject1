from celery import shared_task
from .models import User, Projects
from .ai_services import MatchService
import logging

logger = logging.getLogger(__name__)

@shared_task
def precompute_matches_for_user_task(user_id):
    try:
        user = User.objects.get(pk=user_id)
        logger.info(f"Starting pre-computation task for user {user.email} (ID: {user_id})")
        all_projects = Projects.objects.filter(is_open=True)
        for project in all_projects:
            try:
                MatchService.get_or_create_match_score(user, project)
            except Exception as e:
                logger.error(f"Error pre-computing match for user {user.email} and project {project.title}: {e}")
        logger.info(f"Finished pre-computation task for user {user.email} (ID: {user_id})")
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist. Cannot run pre-computation task.")

@shared_task
def precompute_matches_for_project_task(project_id):
    try:
        project = Projects.objects.get(pk=project_id)
        logger.info(f"Starting pre-computation task for project {project.title} (ID: {project_id})")
        all_users = User.objects.filter(is_active=True)
        for user in all_users:
            try:
                MatchService.get_or_create_match_score(user, project)
            except Exception as e:
                logger.error(f"Error pre-computing match for project {project.title} and user {user.email}: {e}")
        logger.info(f"Finished pre-computation task for project {project.title} (ID: {project_id})")
    except Projects.DoesNotExist:
        logger.error(f"Project with ID {project_id} does not exist. Cannot run pre-computation task.")

@shared_task
def calculate_single_match_score_task(user_id, project_id):
    try:
        user = User.objects.get(pk=user_id)
        project = Projects.objects.get(pk=project_id)
        logger.info(f"Starting single match calculation for user {user.email} and project {project.title}")
        MatchService.get_or_create_match_score(user, project)
        logger.info(f"Finished single match calculation for user {user.email} and project {project.title}")
    except (User.DoesNotExist, Projects.DoesNotExist) as e:
        logger.error(f"Cannot calculate single match score: {e}")
