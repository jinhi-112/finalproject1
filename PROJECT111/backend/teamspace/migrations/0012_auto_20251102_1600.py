from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teamspace', '0011_projects_status_alter_projects_tech_stack'),  # ⚠️ 바로 이전 migration 파일 이름으로 수정!
    ]

    operations = [
        migrations.CreateModel(
            name='Applicants',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tech_match', models.IntegerField(default=0)),
                ('exp_match', models.IntegerField(default=0)),
                ('time_match', models.IntegerField(default=0)),
                ('match_rate', models.IntegerField(default=0)),
                ('motivation', models.TextField()),
                ('status', models.CharField(
                    max_length=20,
                    choices=[
                        ('pending', '검토 대기'),
                        ('reviewed', '검토 완료'),
                        ('accepted', '승인'),
                        ('rejected', '거절'),
                    ],
                    default='pending'
                )),
                ('hours', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='applicants',
                    to='teamspace.projects'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='teamspace.user'
                )),
            ],
            options={
                'db_table': 'Applicants',
            },
        ),
    ]
