# Homelab Telemetry + Autonomous Monitoring

A self-hosted, fully containerized telemetry stack for your homelab: collects detailed system metrics, visualizes data, detects anomalies using statistical models, and leverages agentic LLMs for smart alerting and auto-generated weekly reports.

## Features

- **Prometheus:**  
  Gathers real-time system metrics (CPU, memory, disk, network) via `node_exporter`.

- **Grafana:**  
  Presents interactive dashboards for instant insights.

- **Anomaly Detection:**  
  - `monitor.py` collects CPU usage data from Prometheus.
  - Stores time-series in `cpu_data.csv`.
  - Uses a rolling Z-Score model to flag abnormal usage spikes.

- **Autonomous LLM Agents (via Crew AI):**  
  - **Real-time Alerts:** On anomaly detection, an LLM agent interprets the event and crafts a human-friendly alert, instantly emailing the incident report.
  - **Weekly Reports:** Another agent pulls telemetry data, summarizes trends, generates markdown/PDF reports (with generated charts), and emails them automatically each week.

- **Dockerized Deploy:**  
  All components (Prometheus, Grafana, monitor.py, Crew AI agents) run in isolated containers via Docker Compose for easy setup and management.

- **Easy Expansion:**  
  Built to be forked and extended—add nodes, new metrics, or custom agents with minimal changes.

---
