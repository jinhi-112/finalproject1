from django.contrib.auth.backends import BaseBackend
from .models import User
import logging

logger = logging.getLogger(__name__)

class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        logger.info(f"--- 인증 시도: 이메일 = {email} ---")
        if not email:
            logger.warning("이메일이 제공되지 않아 인증을 중단합니다.")
            return None
        try:
            user = User.objects.get(email=email)
            logger.info(f"사용자를 찾았습니다: {user.email}")
            
            if user.check_password(password):
                logger.info(f"비밀번호 일치. {user.email} 사용자가 인증되었습니다.")
                return user
            else:
                logger.warning(f"비밀번호가 일치하지 않습니다: {user.email}")
                return None
        except User.DoesNotExist:
            logger.warning(f"해당 이메일을 가진 사용자가 존재하지 않습니다: {email}")
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None