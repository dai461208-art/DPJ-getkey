"""
Endpoint cấp key sau khi phiên Link4m được xác minh.
Không được bật cấp key bằng tham số do trình duyệt tự gửi.
Cần tích hợp callback/verification chính thức của Link4m trước khi đưa vào sử dụng.
"""
import json
import os
import re
import secrets
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

def response(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Access-Control-Allow-Origin", os.environ.get("SITE_ORIGIN", "*"))
    handler.end_headers()
    handler.wfile.write(body)

def redis_command(command):
    url = os.environ.get("UPSTASH_REDIS_REST_URL")
    token = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
    if not url or not token:
        raise RuntimeError("Chưa cấu hình Upstash Redis.")
    req = Request(url, data=json.dumps(command).encode(), headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }, method="POST")
    with urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode()).get("result")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        session = parse_qs(urlparse(self.path).query).get("session", [""])[0]
        if not re.fullmatch(r"[A-Za-z0-9_-]{24,80}", session):
            return response(self, 400, {"error": "Mã phiên không hợp lệ."})
        try:
            # Chỉ backend/bot mới được đánh dấu verified sau khi xác minh Link4m.
            status = redis_command(["GET", "dpj:session:" + session])
            if not status:
                return response(self, 403, {"error": "Phiên không tồn tại hoặc đã hết hạn."})
            record = json.loads(status)
            if record.get("status") != "verified":
                return response(self, 403, {"error": "Bạn chưa hoàn thành xác minh Link4m."})
            if record.get("issued"):
                return response(self, 409, {"error": "Phiên này đã nhận key. Hãy tạo link mới từ bot."})
            key = "DPJ_" + secrets.token_urlsafe(8).replace("-", "X").replace("_", "Z")[:11].upper()
            record["issued"] = True
            record["key"] = key
            redis_command(["SET", "dpj:session:" + session, json.dumps(record), "EX", 1800])
            redis_command(["SET", "dpj:key:" + key, json.dumps({
                "telegram_id": str(record["telegram_id"]),
                "used": False,
                "created_at": __import__("time").time()
            }), "EX", 604800])
            return response(self, 200, {"key": key})
        except Exception as exc:
            return response(self, 500, {"error": str(exc)})
