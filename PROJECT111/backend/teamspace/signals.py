from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Users, Projects, UserEmbedding, ProjectEmbedding
from .ai_services import generate_embedding

@receiver(post_save, sender=Users)
def create_or_update_user_embedding(sender, instance, created, **kwargs):
    if created:
        user_embedding, _ = UserEmbedding.objects.get_or_create(user=instance)
    else:
        user_embedding = UserEmbedding.objects.get(user=instance)
    
    # 사용자 정보(예: introduction)를 기반으로 임베딩 생성
    text_to_embed = instance.introduction if instance.introduction else instance.name
    if text_to_embed:
        embedding = generate_embedding(text_to_embed)
        if embedding:
            user_embedding.embedding = embedding
            user_embedding.save()

@receiver(post_save, sender=Projects)
def create_or_update_project_embedding(sender, instance, created, **kwargs):
    if created:
        project_embedding, _ = ProjectEmbedding.objects.get_or_create(project=instance)
    else:
        project_embedding = ProjectEmbedding.objects.get(project=instance)

    # 프로젝트 정보(예: description, title, goal, tech_stack)를 기반으로 임베딩 생성
    text_to_embed = f"{instance.title} {instance.description} {instance.goal} {instance.tech_stack}"
    if text_to_embed.strip(): # 빈 문자열이 아닌 경우에만 임베딩 생성
        embedding = generate_embedding(text_to_embed)
        if embedding:
            project_embedding.embedding = embedding
            project_embedding.save()