# management/commands/migrate_project_skills.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Projects.tech_stack 문자열을 분해해 ProjectSkills에 적재"

    def handle(self, *args, **kwargs):
        with connection.cursor() as cur:
            # Skills 맵
            cur.execute("SELECT skill_id, name FROM Skills")
            name_to_id = {name.strip().lower(): sid for (sid, name) in cur.fetchall()}

            cur.execute("SELECT project_id, tech_stack FROM Projects")
            rows = cur.fetchall()
            insert_rows = []
            for pid, stack in rows:
                if not stack: continue
                names = [s.strip().lower() for s in stack.split(",")]
                for nm in names:
                    sid = name_to_id.get(nm)
                    if sid:
                        insert_rows.append((pid, sid))
            if insert_rows:
                cur.executemany(
                    "INSERT IGNORE INTO ProjectSkills (project_id, skill_id) VALUES (%s, %s)",
                    insert_rows
                )
        self.stdout.write(self.style.SUCCESS(f"OK: {len(insert_rows)} rows inserted"))
