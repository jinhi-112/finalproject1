# management/commands/recommend_topk.py
import struct, numpy as np
from django.core.management.base import BaseCommand
from django.db import connection

def unpack_vec(b: bytes) -> np.ndarray:
    n = struct.unpack("I", b[:4])[0]
    arr = np.frombuffer(b[4:], dtype=np.float32, count=n)
    # 이미 normalize된 벡터 사용
    return arr

SKILL_SQL = """
WITH U AS (
  SELECT us.skill_id,
         CASE us.proficiency_level
              WHEN 'Beginner' THEN 1
              WHEN 'Intermediate' THEN 2
              WHEN 'Advanced' THEN 3
              ELSE 1 END AS w
  FROM UserSkills us
  WHERE us.user_id = %(USER_ID)s
),
P AS (
  SELECT ps.project_id, ps.skill_id
  FROM ProjectSkills ps
),
I AS (
  SELECT p.project_id, u.skill_id, u.w
  FROM P p JOIN U u ON u.skill_id = p.skill_id
),
NUM AS (
  SELECT project_id, COALESCE(SUM(w),0) AS num
  FROM I GROUP BY project_id
),
DEN AS (
  SELECT p.project_id,
         (SELECT COALESCE(SUM(w),0) FROM U)                                     AS sum_user_w,
         (SELECT COUNT(*) FROM P p2 WHERE p2.project_id = p.project_id)          AS cnt_proj,
         (SELECT COALESCE(SUM(w),0) FROM I i WHERE i.project_id = p.project_id)  AS sum_inter
  FROM P p GROUP BY p.project_id
)
SELECT d.project_id,
       CASE WHEN (sum_user_w + cnt_proj - sum_inter)=0 THEN 0
            ELSE (n.num / (sum_user_w + cnt_proj - sum_inter)) END AS skill_score
FROM DEN d LEFT JOIN NUM n ON n.project_id = d.project_id;
"""

class Command(BaseCommand):
    help = "SBERT 코사인 + 스킬 점수 결합으로 Top-K 추천"

    def add_arguments(self, parser):
        parser.add_argument("--user", type=int, required=True)
        parser.add_argument("--topk", type=int, default=50)

    def handle(self, *args, **opts):
        user_id = opts["user"]; K = opts["topk"]

        with connection.cursor() as cur:
            # user vec
            cur.execute("SELECT vector FROM Embeddings WHERE entity_type='user' AND entity_id=%s", [user_id])
            row = cur.fetchone()
            if not row:
                self.stderr.write("해당 user 임베딩 없음. build_embeddings 먼저 수행.")
                return
            u = unpack_vec(row[0])

            # project vecs
            cur.execute("SELECT entity_id, vector FROM Embeddings WHERE entity_type='project'")
            p_rows = cur.fetchall()
            p_ids = []
            p_mat = []
            for pid, vb in p_rows:
                p_ids.append(pid)
                p_mat.append(unpack_vec(vb))
            if not p_mat:
                self.stderr.write("프로젝트 임베딩 없음.")
                return

            p_mat = np.vstack(p_mat)  # (M, dim)
            sims = p_mat.dot(u)       # normalize되어 있으니 dot=cosine

            # 스킬 점수
            cur.execute(SKILL_SQL, {"USER_ID": user_id})
            skill_map = {pid: float(score) for (pid, score) in cur.fetchall()}

            # 결합: 0.7 * cos + 0.3 * skill
            merged = []
            for pid, cos in zip(p_ids, sims):
                sk = skill_map.get(pid, 0.0)
                pre = 0.7*float(cos) + 0.3*sk
                merged.append((pid, pre, float(cos), sk))

            merged.sort(key=lambda x: x[1], reverse=True)
            top = merged[:K]

        # 콘솔 출력
        for pid, pre, cos, sk in top:
            print(f"project={pid} pre={pre:.3f} (cos={cos:.3f}, skill={sk:.3f})")
