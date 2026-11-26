#!/usr/bin/env python3
"""Execute the synthetic health endpoint on loopback using pinned Newman."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/"templates/api-qa.example"
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status=200 if self.path=="/health" else 404
        body=json.dumps({"status":"ok" if status==200 else "not_found"}).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self,*args):
        pass

def main():
    npx=shutil.which("npx")
    if not npx:
        raise RuntimeError("Node/npm npx required")
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            raw=Path(tmp)/"newman.json"
            cmd=[npx,"--yes","--package","newman@6.2.1","newman","run",
                 str(PACKAGE/"postman_collection.json"),"-e",str(PACKAGE/"postman_environment.local.json"),
                 "--env-var",f"baseUrl=http://127.0.0.1:{server.server_port}",
                 "--reporters","json","--reporter-json-export",str(raw)]
            subprocess.run(cmd,check=True,timeout=120)
            report=json.loads(raw.read_text(encoding="utf-8"))["run"]
            stats=report["stats"]
            summary={"runner":"newman@6.2.1","scope":"synthetic_loopback_only",
                     "requests":stats["requests"]["total"],"assertions":stats["assertions"]["total"],
                     "failures":len(report["failures"])}
            assert summary["requests"]==1 and summary["assertions"]==2 and summary["failures"]==0,summary
            print(json.dumps(summary))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
if __name__=="__main__":
    main()
