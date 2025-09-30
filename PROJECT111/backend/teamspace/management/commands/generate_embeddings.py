from django.core.management.base import BaseCommand
from teamspace.models import Users, Projects, UserEmbedding, ProjectEmbedding
from teamspace.ai_services import generate_embedding

class Command(BaseCommand):
    help = 'Generates and saves embeddings for existing Users and Projects.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting embedding generation for Users...'))
        users = Users.objects.all()
        for user in users:
            text_to_embed = user.introduction if user.introduction else user.name
            if text_to_embed:
                embedding = generate_embedding(text_to_embed)
                if embedding:
                    UserEmbedding.objects.update_or_create(
                        user=user,
                        defaults={'embedding': embedding}
                    )
                    self.stdout.write(self.style.SUCCESS(f'Generated embedding for User: {user.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Could not generate embedding for User: {user.name} (no embedding returned)'))
            else:
                self.stdout.write(self.style.WARNING(f'Skipping User: {user.name} (no text to embed)'))

        self.stdout.write(self.style.SUCCESS('Starting embedding generation for Projects...'))
        projects = Projects.objects.all()
        for project in projects:
            text_to_embed = f"{project.title} {project.description} {project.goal} {project.tech_stack}"
            if text_to_embed.strip():
                embedding = generate_embedding(text_to_embed)
                if embedding:
                    ProjectEmbedding.objects.update_or_create(
                        project=project,
                        defaults={'embedding': embedding}
                    )
                    self.stdout.write(self.style.SUCCESS(f'Generated embedding for Project: {project.title}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Could not generate embedding for Project: {project.title} (no embedding returned)'))
            else:
                self.stdout.write(self.style.WARNING(f'Skipping Project: {project.title} (no text to embed)'))

        self.stdout.write(self.style.SUCCESS('Embedding generation complete.'))
