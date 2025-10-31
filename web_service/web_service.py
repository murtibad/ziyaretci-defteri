import os
import requests
from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# API servisinin adresi Render'da ENV'den gelecek
API_URL = os.getenv("API_URL", "http://127.0.0.1:5000")

HTML = """
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <title>Ziyaretçi Defteri</title>
  <style>
    body { font-family: Arial; text-align:center; background:#eef2f3; padding:40px; }
    h1 { color:#333; }
    input { padding:10px; margin:5px; border:1px solid #ccc; border-radius:6px; }
    button { padding:10px 14px; background:#4CAF50; color:#fff; border:0; border-radius:6px; cursor:pointer; }
    ul { list-style:none; padding:0; }
    li { background:#fff; margin:8px auto; width:320px; padding:10px; border-radius:6px; }
    .flash { margin:8px auto; width:320px; padding:10px; border-radius:6px; }
    .error { background:#ffe0e0; }
    .success { background:#e7ffe7; }
    small { color:#666; }
  </style>
</head>
<body>
  <h1>Ziyaretçi Defteri</h1>

  {% with msgs = get_flashed_messages(with_categories=true) %}
    {% if msgs %}
      {% for cat, m in msgs %}
        <div class="flash {{cat}}">{{ m }}</div>
      {% endfor %}
    {% endif %}
  {% endwith %}

  <form method="post" action="{{ url_for('submit') }}">
    <input type="text" name="isim"  placeholder="Adın"   required>
    <input type="text" name="sehir" placeholder="Şehrin" required>
    <button type="submit">Gönder</button>
  </form>

  <p><small>API: {{ api_url }}</small></p>

  <h3>Ziyaretçiler</h3>
  <ul>
    {% for z in ziyaretciler %}
      <li>{{ z.isim }} ({{ z.sehir }})<br><small>{{ z.created_at }}</small></li>
    {% endfor %}
    {% if not ziyaretciler %}<li>Henüz kayıt yok.</li>{% endif %}
  </ul>
</body>
</html>
"""

@app.get("/")
def home():
    try:
        r = requests.get(f"{API_URL}/ziyaretciler", timeout=10)
        r.raise_for_status()
        ziyaretciler = r.json()
    except Exception as e:
        ziyaretciler = []
        flash(f"API okuma hatası: {e}", "error")
    return render_template_string(HTML, ziyaretciler=ziyaretciler, api_url=API_URL)

@app.post("/submit")
def submit():
    isim  = (request.form.get("isim")  or "").strip()
    sehir = (request.form.get("sehir") or "").strip()
    if not isim:
        flash("İsim zorunlu", "error")
        return redirect(url_for("home"))
    try:
        r = requests.post(f"{API_URL}/ziyaretciler", json={"isim": isim, "sehir": sehir}, timeout=10)
        r.raise_for_status()
        flash("Kaydedildi!", "success")
    except Exception as e:
        flash(f"Kaydetme hatası: {e}", "error")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
