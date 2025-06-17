# Ollama On-Demand Proxy

A lightweight reverse proxy that wakes target servers on demand and forwards requests to the Ollama API. Server information is read from `config/servers.yml` for every request so updates require no rebuilds.

## Features
- Dynamic server list loaded from YAML
- Wake-on-LAN with health checks
- Optional bearer token authentication
- Maintenance mode responses
- Docker Compose configuration with Traefik labels

## Prerequisites
- Docker and Docker Compose
- Alternatively Python 3.11 if running directly

## Setup
1. Clone this repository.
2. Copy `.env.example` to `.env` and adjust the settings.
3. Edit `config/servers.yml` to list the machines (MAC address, IP and timeout).

## Configuration
### Environment variables
The `.env` file controls proxy behaviour. Key options include:
- `BIND_ADDRESS` – address the proxy listens on
- `ENABLE_AUTH` – enable bearer token authentication
- `API_AUTH_TOKEN` – token checked when auth is enabled
- `ATTACH_TRAEFIK` and `TRAEFIK_NETWORK` – configure Traefik integration
- `INTERNAL_NETWORK` – name of the internal Docker network
- `OLLAMA_HOST`/`OLLAMA_PORT` – host and port for Traefik routing
- `WOL_RETRY_DELAY`/`WOL_MAX_RETRIES` – wake-on-LAN retry settings
- `HEALTH_PATH`/`HEALTH_TIMEOUT` – endpoint and timeout for health checks
- `REQUEST_TIMEOUT` – total request timeout
- `MAINTENANCE_MODE` – return a 503 message for all requests

See `.env.example` for all available variables.

### Server list
`config/servers.yml` contains an array of servers with their MAC address, IP address and an optional timeout. The proxy will attempt each server in order until one responds as healthy.

## Running
### With Docker Compose
```bash
docker-compose up -d --build
```

### Directly with Python
```bash
pip install -r requirements.txt
python proxy.py
```

## Example request
After the proxy is running you can query the Ollama API through it:
```bash
curl http://localhost:5000/v1/models
```

## License
MIT
