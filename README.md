# Ollama On-Demand Proxy (Final Corrected)

## Overview
Dynamic server list from `config/servers.yml`, no boolean in ports.

## Files
```
ollama_proxy/
├── .env
├── Dockerfile
├── proxy.py
├── requirements.txt
├── config/
│   └── servers.yml
├── docker-compose.yml
└── README.md
```

## .env
```dotenv
BIND_ADDRESS=127.0.0.1       # 0.0.0.0 or 127.0.0.1
ENABLE_AUTH=false
API_AUTH_TOKEN=s3cr3t-t0k3n
ATTACH_TRAEFIK=true
TRAEFIK_NETWORK=web
INTERNAL_NETWORK=bridge
OLLAMA_HOST=ollama.example.com
OLLAMA_PORT=28100
WOL_RETRY_DELAY=2
WOL_MAX_RETRIES=10
HEALTH_PATH=/v1/models
HEALTH_TIMEOUT=1
REQUEST_TIMEOUT=30
LOG_LEVEL=INFO
MAINTENANCE_MODE=false
MAINTAIN_MSG=Under maintenance
```

## config/servers.yml
```yaml
servers:
  - mac: "AA:BB:CC:DD:EE:FF"
    ip: "192.168.0.10"
    timeout: 20
  - mac: "CC:DD:EE:FF:00:11"
    ip: "192.168.0.11"
    timeout: 15
```

## docker-compose.yml
```yaml
version: "3.8"
services:
  ollama-proxy:
    build: .
    env_file: [.env]
    ports:
      - "${BIND_ADDRESS}:5000:5000"
    networks:
      - internal
      - web
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.ollama.rule=Host(`${OLLAMA_HOST}`)"
      - "traefik.http.services.ollama.loadbalancer.server.port=5000"
      - "traefik.http.services.ollama.loadbalancer.healthcheck.path=${HEALTH_PATH}"
      - "traefik.http.services.ollama.loadbalancer.healthcheck.interval=10s"
    volumes:
      - ./config/servers.yml:/app/config/servers.yml:ro
    restart: unless-stopped
networks:
  web:
    external: true
  internal:
    external: true
    name: "${INTERNAL_NETWORK}"
```

## Usage
```
docker-compose up -d --build
```
