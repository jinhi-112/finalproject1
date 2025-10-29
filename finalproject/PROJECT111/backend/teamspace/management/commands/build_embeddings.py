# management/commands/build_embeddings.py
import io, struct, numpy as np
from django.core.management.base import BaseCommand
from django.db import connection
from sentence_transformers import SentenceTransformer

def pack_vec(vec: np.ndarray) -> bytes:
    # float32 bytes (길이 + 데이터)
    vec = vec.astype(np.float32)
    return struct.pack("I", vec.size) + vec.tobytes()

class Command(BaseCommand):
    help = "Users/Projects 임베딩 생성하여 Embeddings 테이블에 저장"

    def add_arguments(self, parser):
        parser.add_argument("--model", type=str, default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        parser.add_argument("--rebuild", action="store_true", help="기존 임베딩 무시 후 재생성")

    def handle(self, *args, **opts):
        model_name = opts["model"]
        rebuild = opts["rebuild"]
        model = SentenceTransformer(model_name)

        with connection.cursor() as cur:
            # Users
            cur.execute("""
                SELECT user_id, COALESCE(introduction,''), COALESCE(preferred_project_topics,''), COALESCE(tech_stack,'')
                FROM Users
            """)
            users = cur.fetchall()
            user_texts = []
            for uid, intro, topics, stack in users:
                text = " ".join([t for t in [intro, topics, stack] if t])
                user_texts.append((uid, text))
            u_ids, u_corpus = zip(*user_texts) if user_texts else ([],[])
            u_vecs = model.encode(list(u_corpus), normalize_embeddings=True) if u_corpus else []

            # Projects
            cur.execute("""
                SELECT project_id, COALESCE(title,''), COALESCE(description,''), COALESCE(goal,''), COALESCE(tech_stack,'')
                FROM Projects
            """)
            projs = cur.fetchall()
            p_texts = []
            for pid, t, d, g, s in projs:
                text = " ".join([x for x in [t,d,g,s] if x])
                p_texts.append((pid, text))
            p_ids, p_corpus = zip(*p_texts) if p_texts else ([],[])
            p_vecs = model.encode(list(p_corpus), normalize_embeddings=True) if p_corpus else []

            # 저장
            if rebuild:
                cur.execute("DELETE FROM Embeddings")

            # upsert
            def upsert_many(kind: str, ids, vecs):
                rows = []
                now = timezone.now()
                for i, vid in enumerate(ids):
                    rows.append((kind, vid, pack_vec(np.array(vecs[i])), now))
                cur.executemany("""
                    INSERT INTO Embeddings (entity_type, entity_id, vector, updated_at)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE vector=VALUES(vector), updated_at=VALUES(updated_at)
                """, rows)

            upsert_many("user", u_ids, u_vecs)
            upsert_many("project", p_ids, p_vecs)

        self.stdout.write(self.style.SUCCESS(f"Embeddings built: users={len(u_vecs)} projects={len(p_vecs)}"))
