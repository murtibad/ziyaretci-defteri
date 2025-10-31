from flask import Flask, render_template_string, request, redirect
import requests
import os

app = Flask(__name__)

# Render'da API_URL ortam değişkeninden gelecek
API_URL = os.getenv("API_URL", "http://127.0.0.1:5000")

HTML = """
<!doctype html>
<html>
<head>
  <title>Ziyaretçi Defteri</title>
  <style>
    body { font-family: Arial; text-align: center; background: #eef2f3; padding: 40px; }
    h1 { color: #333; }
    input { padding: 10px; margin: 5px; font-size: 15px; border-radius: 5px; border: 1px solid #ccc; }
    button { padding: 10px 15px; background: #4CAF50; color: white; border: none; border-radius: 6px; cursor: pointer; }
    ul { list-style-type: none; padding: 0; }
    li { background: white; margin: 8px auto; width: 300px; padding: 10px; border-radius: 6px; }
  </style>
</head>
<body>
  <h1>Ziyaretçi Defteri</h1>
  <p>Adını ve yaşadığın şehri yaz 👇</p>
  <form method="POST">
    <input type="text" name="isim" placeholder="Adın" required>
    <input type="text" name="sehir" placeholder="Şehrin" required>
    <button type="submit">Gönder</button>
  </form>

  <h3>Ziyaretçiler:</h3>
  <ul>
  {% for kisi in isimler %}
    <li>{{ kisi.isim }} ({{ kisi.sehir }})</li>
  {% endfor %}
  </ul>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        isim = request.form.get("isim")
        sehir = request.form.get("sehir")
        try:
            requests.post(f"{API_URL}/ziyaretciler", json={"isim": isim, "sehir": sehir})
        except Exception as e:
            print("POST hatası:", e)
        return redirect("/")

    try:
        resp = requests.get(f"{API_URL}/ziyaretciler")
        isimler = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        print("GET hatası:", e)
        isimler = []
    return render_template_string(HTML, isimler=isimler)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
