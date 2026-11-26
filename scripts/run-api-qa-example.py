#!/usr/bin/env python3
"""Execute the synthetic health endpoint on loopback using pinned Newman."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import secrets
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/"templates/api-qa.example"
class Handler(BaseHTTPRequestHandler):
    def respond(self,status,body,headers=None):
        raw=json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(raw)))
        for key,value in (headers or {}).items():
            self.send_header(key,value)
        self.end_headers()
        self.wfile.write(raw)
    def role(self):
        return self.server.tokens.get(self.headers.get("Authorization","").removeprefix("Bearer "))
    def do_GET(self):
        if self.path=="/health":
            return self.respond(200,{"status":"ok"})
        if self.path.startswith("/items/"):
            if not self.role():
                return self.respond(401,{"error":"unauthorized"})
            item=self.server.items.get(self.path.rsplit("/",1)[1])
            return self.respond(200,item) if item else self.respond(404,{"error":"not_found"})
        return self.respond(404,{"error":"not_found"})
    def do_POST(self):
        try:
            body=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))))
        except (ValueError,TypeError):
            return self.respond(400,{"error":"invalid_json"})
        if self.path=="/auth/login":
            user=body.get("username")
            if user not in self.server.passwords or body.get("password")!=self.server.passwords[user]:
                return self.respond(401,{"error":"unauthorized"})
            token=secrets.token_hex(16)
            self.server.tokens[token]=user
            return self.respond(200,{"token":token})
        if self.path!="/items":
            return self.respond(404,{"error":"not_found"})
        role=self.role()
        if not role:
            return self.respond(401,{"error":"unauthorized"})
        if role!="admin":
            return self.respond(403,{"error":"forbidden"})
        key=self.headers.get("Idempotency-Key")
        if not key:
            return self.respond(400,{"error":"missing_key"})
        if not isinstance(body.get("name"),str) or not body["name"].strip():
            return self.respond(422,{"error":"invalid_name"})
        if key in self.server.replays:
            original,item=self.server.replays[key]
            if original!=body:
                return self.respond(409,{"error":"conflict"})
            return self.respond(201,item,{"X-Idempotent-Replay":"true"})
        item={"id":secrets.token_hex(8),"name":body["name"]}
        self.server.items[item["id"]]=item
        self.server.replays[key]=(body,item)
        return self.respond(201,item)
    def log_message(self,*args):
        pass

def main():
    npx=shutil.which("npx")
    if not npx:
        raise RuntimeError("Node/npm npx required")
    if os.name == "posix" and str(Path(npx).resolve()).startswith("/mnt/"):
        raise RuntimeError("Use native Linux Node/npm in WSL; Windows npx cannot consume POSIX paths")
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    server.passwords={role:secrets.token_hex(16) for role in ("admin","user")}
    server.tokens={}
    server.items={}
    server.replays={}
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            raw=Path(tmp)/"newman.json"
            cmd=[npx,"--yes","--package","newman@6.2.1","newman","run",
                 str(PACKAGE/"postman_collection.json"),"-e",str(PACKAGE/"postman_environment.local.json"),
                 "--env-var",f"baseUrl=http://127.0.0.1:{server.server_port}",
                 "--env-var","adminPassword="+server.passwords["admin"],
                 "--env-var","userPassword="+server.passwords["user"],
                 "--reporters","json","--reporter-json-export",str(raw)]
            subprocess.run(cmd,check=True,timeout=120)
            report=json.loads(raw.read_text(encoding="utf-8"))["run"]
            stats=report["stats"]
            summary={"runner":"newman@6.2.1","scope":"synthetic_loopback_only",
                     "requests":stats["requests"]["total"],"assertions":stats["assertions"]["total"],
                     "failures":len(report["failures"])}
            assert summary["requests"]==12 and summary["assertions"]==19 and summary["failures"]==0,summary
            print(json.dumps(summary))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
if __name__=="__main__":
    main()
