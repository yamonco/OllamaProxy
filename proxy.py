#!/usr/bin/env python3
"""Ollama On-Demand Proxy with Dynamic Server Config

Reads 'config/servers.yml' on each request.
Supports maintenance mode, token auth, WOL, health checks, and proxy.
"""

import os, time, logging
from flask import Flask, request, Response, abort
import requests
from wakeonlan import send_magic_packet
import yaml
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Settings from env
BIND_ADDRESS = os.getenv("BIND_ADDRESS", "127.0.0.1")
ENABLE_AUTH = os.getenv("ENABLE_AUTH", "false").lower() == "true"
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "")
ATTACH_TRAEFIK = os.getenv("ATTACH_TRAEFIK", "false").lower() == "true"
TRAEFIK_NETWORK = os.getenv("TRAEFIK_NETWORK", "web")
INTERNAL_NETWORK = os.getenv("INTERNAL_NETWORK", "bridge")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "28100")
WOL_RETRY_DELAY = int(os.getenv("WOL_RETRY_DELAY", "2"))
WOL_MAX_RETRIES = int(os.getenv("WOL_MAX_RETRIES", "10"))
HEALTH_PATH = os.getenv("HEALTH_PATH", "/v1/models")
HEALTH_TIMEOUT = float(os.getenv("HEALTH_TIMEOUT", "1"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30"))
MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
MAINTAIN_MSG = os.getenv("MAINTAIN_MSG", "Service under maintenance")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                    format="[%(asctime)s] %(levelname)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

app = Flask(__name__)

def load_servers():
    with open("config/servers.yml", "r") as f:
        data = yaml.safe_load(f)
    return data.get("servers", [])

def wake_and_wait(mac, ip, timeout):
    send_magic_packet(mac)
    for _ in range(WOL_MAX_RETRIES):
        try:
            url = f"http://{ip}:{OLLAMA_PORT}{HEALTH_PATH}"
            r = requests.get(url, timeout=HEALTH_TIMEOUT)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(WOL_RETRY_DELAY)
    return False

@app.before_request
def before_request():
    if MAINTENANCE_MODE:
        return Response(MAINTAIN_MSG, status=503)
    if ENABLE_AUTH:
        auth = request.headers.get("Authorization", "")
        if auth != f"Bearer {API_AUTH_TOKEN}":
            abort(401)

@app.route('/', defaults={'path': ''}, methods=["GET","POST","PUT","DELETE","PATCH"])
@app.route('/<path:path>', methods=["GET","POST","PUT","DELETE","PATCH"])
def proxy(path):
    servers = load_servers()
    for srv in servers:
        mac = srv.get("mac")
        ip = srv.get("ip")
        timeout = srv.get("timeout", HEALTH_TIMEOUT)
        logging.info(f"Trying {ip}")
        if wake_and_wait(mac, ip, timeout):
            target = f"http://{ip}:{OLLAMA_PORT}/{path}"
            resp = requests.request(request.method, target,
                                     headers={k:v for k,v in request.headers if k!="Host"},
                                     params=request.args, data=request.get_data(),
                                     timeout=REQUEST_TIMEOUT)
            excluded = ['content-encoding','content-length','transfer-encoding','connection']
            headers = [(n,v) for n,v in resp.raw.headers.items() if n.lower() not in excluded]
            return Response(resp.content, resp.status_code, headers)
    logging.error("All servers unavailable")
    return Response("Service Unavailable", status=503)

if __name__ == "__main__":
    app.run(host=BIND_ADDRESS, port=5000)
