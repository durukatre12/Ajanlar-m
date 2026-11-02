#!/usr/bin/env python3
"""Gmail yetkisi — bir kez, elle çalıştırılır (ajan çalıştırmaz).

Ön koşul: Google Cloud'da bir "Desktop app" OAuth istemcisi (bkz. KURULUM.md · Gmail) ve
`.env`'de GMAIL_CLIENT_ID + GMAIL_CLIENT_SECRET.

    python3 bin/gmail_yetki.py

Tarayıcıda açılan Google sayfasında hesabını seçip izin ver. Betik `GMAIL_REFRESH_TOKEN=...`
satırını ekrana basar; o satırı `.env`'e yapıştır. İzin kapsamı `gmail.compose`: taslak açma ve
gönderme — gelen kutunu okuyamaz.
"""
import http.server
import os
import secrets
import sys
import urllib.parse
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ayar  # noqa: E402
import posta  # noqa: E402

KAPSAM = "https://www.googleapis.com/auth/gmail.compose"
YETKI_URL = "https://accounts.google.com/o/oauth2/v2/auth"


def main():
    ayar.ortam_yukle()
    istemci = os.environ.get("GMAIL_CLIENT_ID")
    sir = os.environ.get("GMAIL_CLIENT_SECRET")
    if not istemci or not sir:
        print("Önce .env'e GMAIL_CLIENT_ID ve GMAIL_CLIENT_SECRET yaz (KURULUM.md · Gmail).")
        return 1
    durum = secrets.token_urlsafe(16)
    gelen = {}

    class Yakala(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            sorgu = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            gelen.update({k: v[0] for k, v in sorgu.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("Tamam — bu sekmeyi kapatıp terminale dönebilirsin.".encode())

        def log_message(self, *_):
            pass

    sunucu = http.server.HTTPServer(("127.0.0.1", 0), Yakala)
    donus = f"http://127.0.0.1:{sunucu.server_port}"
    url = YETKI_URL + "?" + urllib.parse.urlencode({
        "client_id": istemci, "redirect_uri": donus, "response_type": "code", "scope": KAPSAM,
        "access_type": "offline", "prompt": "consent", "state": durum})
    print("Bu adresi tarayıcıda aç (otomatik açılmazsa kopyala):\n\n" + url + "\n")
    webbrowser.open(url)
    while "code" not in gelen and "error" not in gelen:
        sunucu.handle_request()
    if gelen.get("state") != durum or "code" not in gelen:
        print(f"İzin alınamadı: {gelen.get('error', 'durum eşleşmedi')}")
        return 1
    yanit = posta._http("POST", posta.TOKEN_URL, {
        "code": gelen["code"], "client_id": istemci, "client_secret": sir,
        "redirect_uri": donus, "grant_type": "authorization_code"}, form=True)
    jeton = yanit.get("refresh_token")
    if not jeton:
        print("Google yenileme jetonu vermedi. myaccount.google.com/permissions'tan uygulamanın "
              "erişimini kaldırıp yeniden dene.")
        return 1
    print("İzin alındı. Şu satırı .env'e ekle (kimseyle paylaşma):\n")
    print(f"GMAIL_REFRESH_TOKEN={jeton}\n")
    print("Sonra dene: python3 bin/posta.py taslaklar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
