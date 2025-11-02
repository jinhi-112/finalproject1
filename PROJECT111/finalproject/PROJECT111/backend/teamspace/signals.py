from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Projects, UserEmbedding, ProjectEmbedding
from .ai_services import generate_embedding



@receiver(post_save, sender=Projects)
def create_or_update_project_embedding(sender, instance, created, **kwargs):
    # Always use get_or_create to ensure the embedding object exists
    project_embedding, _ = ProjectEmbedding.objects.get_or_create(project=instance)

    # 프로젝트 정보(예: description, title, goal, tech_stack)를 기반으로 임베딩 생성
    text_to_embed = f"{instance.title} {instance.description} {instance.goal} {instance.tech_stack}"
    if text_to_embed.strip(): # 빈 문자열이 아닌 경우에만 임베딩 생성
        embedding = generate_embedding(text_to_embed)
        if embedding:
            project_embedding.embedding = embedding
            project_embedding.save()

@receiver(post_save, sender=User)
def create_or_update_user_embedding(sender, instance, created, **kwargs):
    # Always use get_or_create to ensure the embedding object exists
    user_embedding, _ = UserEmbedding.objects.get_or_create(user=instance)

    # 사용자 정보(예: introduction)를 기반으로 임베딩 생성
    text_to_embed_parts = []
    if instance.introduction:
        text_to_embed_parts.append(instance.introduction)
    if instance.major:
        text_to_embed_parts.append(f"주 전공: {instance.major}")
    if instance.specialty:
        text_to_embed_parts.append(f"특기: {instance.specialty}")
    if instance.tech_stack:
        text_to_embed_parts.append(f"기술 스택: {instance.tech_stack}")
    if instance.experience_level:
        text_to_embed_parts.append(f"경험 수준: {instance.experience_level}")
    if instance.collaboration_style:
        text_to_embed_parts.append(f"협업 스타일: {instance.collaboration_style}")
    if instance.preferred_project_topics:
        text_to_embed_parts.append(f"선호 프로젝트 주제: {instance.preferred_project_topics}")
    if instance.belbin_role:
        text_to_embed_parts.append(f"Belbin 역할: {instance.belbin_role}")

    if instance.available_region:
        # 콤마로 구분된 문자열을 리스트로 분리하여 임베딩 텍스트에 추가
        regions = [region.strip() for region in instance.available_region.split(',') if region.strip()]
        if regions:
            text_to_embed_parts.append(f"활동 가능 지역: {', '.join(regions)}")

    text_to_embed = " ".join(text_to_embed_parts)
    if not text_to_embed and instance.name: # Fallback to name if all other fields are empty
        text_to_embed = instance.name
    if text_to_embed:
        embedding = generate_embedding(text_to_embed)
        if embedding:
            user_embedding.embedding = embedding
            user_embedding.save()