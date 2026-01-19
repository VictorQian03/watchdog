from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(relative_path: str) -> dict:
    path = ROOT / relative_path
    return yaml.safe_load(path.read_text())


def load_json(relative_path: str) -> dict:
    path = ROOT / relative_path
    return json.loads(path.read_text())


def test_docker_compose_services() -> None:
    data = load_yaml("docker-compose.yml")
    services = data.get("services", {})
    assert "prometheus" in services
    assert "grafana" in services


def test_prometheus_scrape_target() -> None:
    data = load_yaml("prometheus/prometheus.yml")
    scrape_configs = data.get("scrape_configs", [])
    job = next((item for item in scrape_configs if item.get("job_name") == "node_exporter"), None)
    assert job is not None
    static_configs = job.get("static_configs", [])
    targets = [t for sc in static_configs for t in sc.get("targets", [])]
    assert "host.docker.internal:9100" in targets


def test_grafana_datasource() -> None:
    data = load_yaml("grafana/provisioning/datasources/datasource.yml")
    datasources = data.get("datasources", [])
    prom = next((item for item in datasources if item.get("type") == "prometheus"), None)
    assert prom is not None
    assert prom.get("url") == "http://prometheus:9090"


def test_dashboard_panels_exist() -> None:
    data = load_json("grafana/dashboards/macos-host.json")
    titles = {panel.get("title") for panel in data.get("panels", [])}
    assert "CPU Usage (%)" in titles
    assert "RAM Available (bytes)" in titles
    assert "Root Filesystem Free (bytes)" in titles
    assert "Disk Free by Mountpoint (bytes)" in titles
    assert "Disk Free by Mountpoint (%)" in titles


def test_dashboard_queries_reference_required_metrics() -> None:
    data = load_json("grafana/dashboards/macos-host.json")
    exprs: list[str] = []
    for panel in data.get("panels", []):
        for target in panel.get("targets", []):
            expr = target.get("expr")
            if expr:
                exprs.append(expr)
    joined = "\n".join(exprs)
    assert "node_cpu_seconds_total" in joined
    assert "node_memory_free_bytes" in joined
    assert "node_memory_inactive_bytes" in joined
    assert "node_filesystem_avail_bytes" in joined
    assert "node_filesystem_size_bytes" in joined
