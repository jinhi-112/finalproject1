from django.core.management.base import BaseCommand
from teamspace.models import User, Projects, UserEmbedding, ProjectEmbedding
from teamspace.ai_services import generate_embedding

class Command(BaseCommand):
    help = 'Populates SBERT embeddings for existing Users and Projects.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate embeddings...'))

        # Populate User Embeddings
        users = User.objects.all()
        self.stdout.write(f'Processing {users.count()} users...')
        for user in users:
            user_skills_text = " ".join([user_skill.skill.name for user_skill in user.userskills_set.all()])
            text_to_embed = f"{user.introduction or ''} {user_skills_text}".strip()
            if text_to_embed:
                embedding = generate_embedding(text_to_embed)
                if embedding:
                    user_embedding, created = UserEmbedding.objects.get_or_create(user=user)
                    user_embedding.embedding = embedding
                    user_embedding.save()
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created embedding for user: {user.name}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Updated embedding for user: {user.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Could not generate embedding for user: {user.name} (empty text or model error)'))
            else:
                self.stdout.write(self.style.WARNING(f'Skipping user {user.name}: no introduction or skills to embed.'))

        # Populate Project Embeddings
        projects = Projects.objects.all()
        self.stdout.write(f'Processing {projects.count()} projects...')
        for project in projects:
            text_to_embed = f"{project.description or ''} {project.tech_stack or ''}".strip()
            if text_to_embed:
                embedding = generate_embedding(text_to_embed)
                if embedding:
                    project_embedding, created = ProjectEmbedding.objects.get_or_create(project=project)
                    project_embedding.embedding = embedding
                    project_embedding.save()
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created embedding for project: {project.title}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Updated embedding for project: {project.title}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Could not generate embedding for project: {project.title} (empty text or model error)'))
            else:
                self.stdout.write(self.style.WARNING(f'Skipping project {project.title}: no description or tech stack to embed.'))

        self.stdout.write(self.style.SUCCESS('Finished populating embeddings.'))
