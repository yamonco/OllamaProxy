# Ollama On-Demand Proxy

Ollama On-Demand Proxy is a minimal reverse proxy designed specifically for self-hosted Ollama servers. It wakes target machines via Wake-on-LAN when a request arrives and transparently forwards the call to the Ollama API once the host is ready. The proxy checks the server list on every request, so you can add or remove machines without rebuilding containers.

## Key Features
- **Dynamic server configuration** – server information lives in `config/servers.yml` and is reloaded for each request.
- **Wake-on-LAN with health checks** – automatically power on targets and wait until the API responds.
- **Bearer token authentication** – protect the proxy with an optional API token.
- **Maintenance mode** – instantly return a 503 message when the service is offline.
- **Traefik integration** – labels and network settings work out of the box with Traefik reverse proxy.
- **Docker or native execution** – run via Docker Compose or directly with Python 3.

## Advantages
- **Zero rebuilds for config changes** – update `servers.yml` or `.env` and restart only the container.
- **Lightweight** – small codebase with minimal dependencies.
- **Automated startup** – ensures hosts are awake before forwarding requests.
- **Compatible with existing Ollama clients** – acts as a drop-in HTTP endpoint.

## Directory Layout
```
.
├── proxy.py              # application entry point
├── Dockerfile            # container build
├── docker-compose.yml    # sample compose file
├── config/servers.yml    # list of target servers
├── .env.example          # environment template
└── README.md
```

## Getting Started
1. **Clone the repository**
   ```bash
   git clone https://example.com/ollama-proxy.git
   cd ollama-proxy
   ```
2. **Create your environment file**
   ```bash
   cp .env.example .env
   # edit .env to fit your environment
   ```
3. **Edit the server list** in `config/servers.yml` with the MAC address and IP of each machine that runs Ollama.

### Environment Variables
Each option in `.env` customizes proxy behaviour. Important settings include:
- `BIND_ADDRESS` – network interface for the proxy (default `0.0.0.0`).
- `ENABLE_AUTH` and `API_AUTH_TOKEN` – enable and configure bearer token checks.
- `ATTACH_TRAEFIK`, `TRAEFIK_NETWORK` – connect to an external Traefik network.
- `INTERNAL_NETWORK` – Docker bridge network name.
- `OLLAMA_HOST`/`OLLAMA_PORT` – domain and port used by Traefik routing.
- `WOL_RETRY_DELAY`, `WOL_MAX_RETRIES` – how often and how many times to poll the target server.
- `HEALTH_PATH`, `HEALTH_TIMEOUT` – endpoint and timeout for readiness checks.
- `REQUEST_TIMEOUT` – total timeout for proxied requests.
- `MAINTENANCE_MODE`, `MAINTAIN_MSG` – toggle maintenance mode and customize the response message.

Refer to `.env.example` for a complete list and defaults.

## Running the Proxy
### Docker Compose
```bash
docker-compose up -d --build
```
This builds the container and starts the proxy on port 5000. Traefik labels are included so the service can be routed by hostname if Traefik is present.

### Direct Execution
```bash
pip install -r requirements.txt
python proxy.py
```
This starts the Flask app directly for development or lightweight deployments.

## Usage Example
Assuming the proxy listens on `localhost:5000`:
```bash
curl http://localhost:5000/v1/models
```
The proxy will wake the first server in `servers.yml`, wait for the health check to succeed, and then forward the request to the Ollama API.

## License
MIT
