
import os
import django
import datetime

# Django 환경 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from teamspace.models import User, Projects, ProjectEmbedding
from teamspace.ai_services import generate_embedding # ai_services에서 임베딩 생성 함수 가져오기

def seed_database():
    # 기존 사용자를 가져오거나 없으면 새로 생성
    user, created = User.objects.get_or_create(
        email='testuser@example.com',
        defaults={
            'name': 'Test User',
            'password': 'password123'  # 실제 사용 시에는 해시된 비밀번호를 사용해야 합니다.
        }
    )

    if created:
        user.set_password('password123')
        user.save()
        print(f"사용자 '{user.name}' 생성됨")
    else:
        print(f"기존 사용자 '{user.name}' 사용")

    # 샘플 프로젝트 데이터
    projects_to_create = [
        {
            'creator': user,
            'title': 'AI 기반 추천 시스템 개발',
            'description': '사용자 맞춤형 상품을 추천하는 AI 모델을 개발하고 서비스에 적용합니다.',
            'goal': '추천 정확도 85% 달성',
            'tech_stack': 'Python, TensorFlow, Django, React',
            'recruitment_count': 3,
            'start_date': datetime.date(2024, 8, 1),
            'end_date': datetime.date(2024, 12, 31),
            'is_open': True,
        },
        {
            'creator': user,
            'title': '실시간 채팅 애플리케이션',
            'description': 'WebSocket을 이용한 실시간 채팅 기능을 구현하는 프로젝트입니다.',
            'goal': '동시 접속자 100명 처리 가능한 안정적인 채팅 서버 구축',
            'tech_stack': 'Node.js, Socket.IO, Express, Vue.js',
            'recruitment_count': 2,
            'start_date': datetime.date(2024, 9, 15),
            'end_date': datetime.date(2024, 11, 30),
            'is_open': True,
        }
    ]

    # 프로젝트 생성
    for project_data in projects_to_create:
        project, created = Projects.objects.get_or_create(
            title=project_data['title'],
            defaults=project_data
        )
        if created:
            print(f"프로젝트 '{project.title}' 생성됨")

            # 임베딩 생성을 위한 텍스트 데이터 조합
            embedding_text = f"{project.title} {project.description} {project.goal} {project.tech_stack}"
            
            # 임베딩 생성
            project_embedding_vector = generate_embedding(embedding_text)
            
            # ProjectEmbedding 객체 생성 및 저장
            if project_embedding_vector:
                ProjectEmbedding.objects.create(
                    project=project,
                    embedding=project_embedding_vector
                )
                print(f"  - 임베딩 생성 완료: '{project.title}'")
        else:
            print(f"프로젝트 '{project.title}' 이미 존재함")

if __name__ == '__main__':
    seed_database()
    print("데이터베이스 시딩 완료.")
