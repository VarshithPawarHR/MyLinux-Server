# 📡 Homelab Telemetry + Autonomous Monitoring

A self-hosted telemetry monitoring stack that collects system metrics, visualizes them, detects anomalies with a simple ML model, and will soon use an LLM agentic layer for smart alerting and auto-generated weekly reports.

---

## ✅ Current Features

* **Prometheus**: Collects system metrics (CPU usage, etc.) using node_exporter.
* **Grafana**: Visualizes real-time telemetry data in beautiful dashboards.
* **Dockerized**: Runs all components (Prometheus, Grafana, monitor.py) in isolated containers.
* **Anomaly Detection**:
  * monitor.py collects CPU usage from Prometheus.
  * Appends data to cpu_data.csv.
  * Uses a simple Z-Score model to flag usage spikes.
  * Runs automatically every hour (or inside container loop).

---

## ⚙️ Planned LLM Integration

* **Crew AI for Real-time Alerts**
  - When monitor.py detects an outlier, it triggers a Crew AI agent that:
    * Interprets the alert.
    * Crafts a human-readable message.
    * Emails you immediately.
* **Crew AI for Weekly Reports**
  - A separate agent will:
    * Pull the CSV telemetry data.
    * Generate summaries, graphs, and trends.
    * Write an easy-to-read markdown or PDF report.
    * Email it automatically every week.

---

## 🐳 Run Locally

```bash
# Navigate to the telemetry directory
cd telemetry-llm

# Start everything
docker compose up -d

# Check logs
docker compose logs -f telemetry_monitor
```

---

## 📂 Project Structure

```
MyLinux-Server/
 ├─ telemetry-llm/
 │   ├─ docker-compose.yml
 │   ├─ Dockerfile
 │   ├─ prometheus.yml
 │   ├─ monitor.py
 │   ├─ cpu_data.csv
 │   ├─ requirements.txt
 │   ├─ README.md
 │   └─ main.py
 └─ README.md
```

---

## ⚡ How It Works

1. **Prometheus + node_exporter** → scrapes CPU metrics.
2. **Grafana** → dashboards.
3. **monitor.py** → pulls CPU usage, checks for outliers.
4. **Coming Soon**:
   * Crew AI watches anomalies → sends alert.
   * Crew AI generates weekly insights → sends report.

---

## 🚀 Next Up

* [ ] Wire up Crew AI to monitor.py
* [ ] Build weekly reporting agent
* [ ] Auto-email flow
* [ ] More metrics: memory, disk, network
* [ ] Push all configs, dashboards to GitHub

---

## 📬 Contact

**Built by:** Varshith Pawar  
**Email:** varshithpawarhr@gmail.com

---

**Feel free to copy, fork, or build your own!**

---