from django.core.management.base import BaseCommand
from teamspace.models import User, Projects
from django.db import transaction

class Command(BaseCommand):
    help = "Generates embeddings for all existing Users and Projects by calling their save() method."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting embedding generation for Users..."))
        users_updated = 0
        for user in User.objects.all():
            user.save() # This will trigger the post_save signal for UserEmbedding
            users_updated += 1
        self.stdout.write(self.style.SUCCESS(f"Successfully generated embeddings for {users_updated} Users."))

        self.stdout.write(self.style.NOTICE("Starting embedding generation for Projects..."))
        projects_updated = 0
        for project in Projects.objects.all():
            project.save() # This will trigger the post_save signal for ProjectEmbedding
            projects_updated += 1
        self.stdout.write(self.style.SUCCESS(f"Successfully generated embeddings for {projects_updated} Projects."))

        self.stdout.write(self.style.SUCCESS("Embedding generation complete."))