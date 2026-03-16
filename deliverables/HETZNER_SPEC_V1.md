# HETZNER PRODUCTION SPEC - v1.0
## OpenClaw "Bulletproof" Instance

### 1. Infrastructure (Hetzner Cloud)
*   **Plan:** CPX31 (4 vCPU, 8GB RAM) or higher.
*   **OS:** Ubuntu 22.04 LTS (Minimal).
*   **Volume:** 50GB NVMe (for high-speed local vector search).

### 2. Service Architecture (Isolated Containers)
We will use **Docker Compose** to treat each part of your system as a separate "Machine."

| Container | Image | Purpose |
| :--- | :--- | :--- |
| **traefik** | `traefik:latest` | Handlers SSL, Subdomains, and permanent routing. |
| **gateway** | `openclaw:latest` | The core "Brain" and sub-agent manager. |
| **backend** | `python:3.11-slim` | The CRM Python API (FastAPI). |
| **frontend** | `node:18-slim` | The React CRM UI. |
| **database** | `postgres:15-alpine` | Unified Postgres for CRM + Chonkie Memory. |
| **clawmetry** | `clawmetry:latest` | Real-time monitoring and log indexing. |

### 3. Permanent URL Mapping (The Traefik Advantage)
No more Rustunnel. We will use a fixed domain (e.g., `vantage.work`).

*   `crm.vantage.work` → **Frontend Container**
*   `api.vantage.work` → **Backend Container**
*   `brain.vantage.work` → **ClawMetry Dashboard**

### 4. Memory Strategy (Local RAG)
*   The `database` container will have a dedicated **`pgvector`** extension enabled.
*   The **all-MiniLM-L6-v2** model will reside on the persistent NVMe volume.
*   Recall will be sub-millisecond across all agents.

### 5. Deployment Lifecycle (GitHub Controlled)
*   **Git Push** → GitHub Action triggers.
*   **Step 1:** Action runs `docker-compose build` on Hetzner.
*   **Step 2:** All containers are restarted in sequence.
*   **Step 3:** Validation script checks all ports before declaring success.

