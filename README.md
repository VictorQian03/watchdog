# MacOS Host Health Dashboard

Local MacOS host monitoring with Prometheus, Grafana, and node_exporter. The stack runs Prometheus and Grafana in Docker, and node_exporter on the MacOS host for accurate host metrics.

## Requirements
- Docker Desktop
- Homebrew (recommended for installing node_exporter)
- Python 3.10+ and uv (for test/lint tooling)

## Install node_exporter on MacOS
```bash
brew install node_exporter
brew services start node_exporter
```
Verify the endpoint:
```bash
curl http://localhost:9100/metrics | head
```

## Start the monitoring stack
Create a local `.env` file with Grafana credentials:
```bash
cp .env.example .env
# Edit .env and set a strong password
```
Do not commit `.env`.

```bash
docker compose up -d
```

Grafana: http://localhost:3000 (user/password from `.env`)
Prometheus: http://localhost:9090

## Dashboard
A pre-provisioned dashboard named **MacOS Host Health** is installed under the **MacOS Host** folder. It includes:
- CPU usage (%)
- Available RAM (bytes)
- Root filesystem free (bytes)
- Per-disk free space (bytes and %)

### Metric meanings and purpose
- **CPU usage (%)**: Percentage of CPU time spent doing work (non-idle). Purpose: spot sustained CPU pressure, runaway processes, or spikes that can slow the system.
- **Available RAM (bytes)**: Estimated memory readily available without heavy swapping. On macOS this is approximated as `node_memory_free_bytes + node_memory_inactive_bytes`. Purpose: detect memory pressure and avoid performance drops from swapping.
- **Root filesystem free (bytes)**: Free space on the root volume. Purpose: prevent system instability or app failures caused by low disk space.
- **Per-disk free space (bytes and %)**: Free space per mountpoint. Purpose: identify which disks or volumes are running out of space, especially external drives or separate partitions.

## Tests and linting (uv)
Create a venv and install dev dependencies:
```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```
Run tests and linting:
```bash
pytest
ruff check .
ruff format --check .
```

## Troubleshooting
- If Prometheus cannot reach node_exporter, replace `host.docker.internal:9100` in `prometheus/prometheus.yml` with your MacOS host IP.
- If per-disk panels show pseudo filesystems, adjust the `fstype` filter in `grafana/dashboards/macos-host.json`.
- RAM uses a macOS-friendly query: `node_memory_free_bytes + node_memory_inactive_bytes`. You can confirm available memory metrics in Prometheus with `node_memory_.*` and adjust if your node_exporter build uses different names.
- Data persistence: Grafana and Prometheus use named volumes. `docker compose down` keeps data, `docker compose down -v` removes it.
