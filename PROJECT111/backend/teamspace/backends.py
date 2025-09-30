from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import Users

class CustomUserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Users.objects.get(email=username) # Use email as the username
            if check_password(password, user.password_hash):
                # Django의 인증 시스템이 기대하는 속성들을 Users 객체에 동적으로 추가
                user.is_authenticated = True
                user.is_active = True # 사용자가 활성 상태라고 가정
                user.pk = user.user_id # Django는 pk 속성을 기대합니다.
                user.get_session_auth_hash = lambda: user.password_hash # 세션 해시를 위한 간단한 구현
                return user
        except Users.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            user = Users.objects.get(pk=user_id)
            # get_user에서도 필수 속성들을 추가
            user.is_authenticated = True
            user.is_active = True
            user.pk = user.user_id
            user.get_session_auth_hash = lambda: user.password_hash
            return user
        except Users.DoesNotExist:
            return None