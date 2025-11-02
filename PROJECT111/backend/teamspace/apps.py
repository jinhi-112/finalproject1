from django.apps import AppConfig


class TeamspaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'teamspace'

    def ready(self):
        # Disconnect the update_last_login signal
        from django.contrib.auth.signals import user_logged_in
        from django.contrib.auth.models import update_last_login
        user_logged_in.disconnect(update_last_login)
        import teamspace.signals # signals.py를 로드하여 시그널 핸들러를 등록합니다.
