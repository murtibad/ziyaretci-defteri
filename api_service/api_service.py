import os
import psycopg
from flask import Flask, request, jsonify

app = Flask(__name__)

# DATABASE_URL KODDA YOK; ENV'DEN OKUNUR
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")

# Render/managed PG için sslmode genelde gerekir
if "sslmode" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

def get_conn():
    return psycopg.connect(DATABASE_URL)

# İlk açılışta tabloyu oluştur
with get_conn() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ziyaretciler (
                id SERIAL PRIMARY KEY,
                isim  TEXT NOT NULL,
                sehir TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        conn.commit()

@app.get("/")
def health():
    return jsonify({"service": "api", "status": "ok"})

@app.get("/ziyaretciler")
def list_ziyaretciler():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT isim, sehir, created_at FROM ziyaretciler ORDER BY id DESC;")
            rows = cur.fetchall()
    data = [{"isim": r[0], "sehir": r[1], "created_at": r[2].isoformat()} for r in rows]
    return jsonify(data), 200

@app.post("/ziyaretciler")
def add_ziyaretci():
    payload = request.get_json(silent=True) or {}
    isim = (payload.get("isim") or "").strip()
    sehir = (payload.get("sehir") or "").strip()
    if not isim:
        return jsonify({"hata": "isim zorunlu"}), 400
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ziyaretciler (isim, sehir) VALUES (%s, %s) RETURNING id;",
                (isim, sehir)
            )
            conn.commit()
    return jsonify({"mesaj": f"Merhaba {isim} ({sehir}) kaydedildi"}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
