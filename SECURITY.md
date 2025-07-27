# Security Policy

This document outlines the security and operational guidelines for the **Homelab Telemetry + Autonomous Monitoring** stack.

---

## Threat Model

The stack is intended for private, self-hosted use (homelab, internal servers), but security best practices should be followed at all times—especially if exposed to wider networks.

---

## Key Security Features

- **Container Isolation:**  
  All services (Prometheus, Grafana, monitor.py, Crew AI agents) run in isolated Docker containers, limiting the blast radius of any single component.

- **Minimal Permissions:**  
  Containers are run with only the permissions necessary for operation. Avoid running as root where not required.

- **Network Controls:**  
  Prometheus and node_exporter endpoints should only be accessible to trusted systems or via your internal network. Avoid exposing them to the internet.

- **Secrets Management:**  
  API keys, email credentials, and other secrets should be managed with Docker environment variables or Docker secrets—not hardcoded in code or configs.

- **Regular Updates:**  
  Always keep base images, dependencies, and this stack's code up to date to avoid known vulnerabilities.

- **Authentication & Authorization:**
  - **Grafana:**  
    Enable authentication (username/password, SSO) and restrict dashboard sharing as needed.
  - **Prometheus, Node Exporter:**  
    On networks where possible exposure exists, secure endpoints using firewall rules or reverse proxies with authentication.
    
---

## Recommended Practices

- **Firewall:**  
  Use host-based firewalls (e.g., UFW) to restrict access to only trusted management IPs.
- **TLS/HTTPS:**  
  Terminate external access with a reverse proxy and TLS (e.g., Traefik, Nginx) if you must access dashboards or APIs remotely.
- **Database Exposure:**  
  Avoid exposing container storage or Prometheus data directories outside the stack.

---

## Reporting Vulnerabilities

If you discover a security issue or have concerns, please open an issue with the label `security` in your project repository or privately communicate concerns as appropriate.

---

## Disclaimer

This stack is provided as-is and designed for homelab and non-production usage. For production/enterprise contexts, enforce strict authentication controls and audit all operational dependencies.

---

*Stay secure and monitor responsibly!*
