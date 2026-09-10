# Green Metrics Classroom Demo

An educational, self-contained Python Flask application demonstrating how software computational workloads affect CPU utilization and energy consumption, tailored for benchmarking with the **Green Metrics Tool (GMT)** and its hosted **ScenarioRunner** at [metrics.green-coding.io](https://metrics.green-coding.io/).

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Why This Matters for Green Software](#why-this-matters-for-green-software)
3. [Architecture & How It Works](#architecture--how-it-works)
4. [Folder Structure](#folder-structure)
5. [Running Locally (Without Docker)](#running-locally-without-docker)
6. [Running with Docker & Docker Compose](#running-with-docker--docker-compose)
7. [Testing Endpoints & Workloads](#testing-endpoints--workloads)
8. [How GMT ScenarioRunner Uses This Repository](#how-gmt-scenariorunner-uses-this-repository)
9. [Submitting to the Hosted Green Metrics Tool](#submitting-to-the-hosted-green-metrics-tool)
10. [Interpreting Measurement Results](#interpreting-measurement-results)
11. [Classroom Demonstration Walkthrough](#classroom-demonstration-walkthrough)

---

## Project Overview

In traditional software development, code is primarily evaluated by latency, throughput, and functionality. **Green Software Engineering** introduces an essential additional metric: **Energy & Carbon Efficiency**.

This project provides a clean, visual classroom demonstration:
- **Lightweight Workload (`/workload/light`)**: A minimal, low-overhead transaction with near-zero CPU state change.
- **CPU-Intensive Workload (`/workload/heavy`)**: A bounded, deterministic computational task performing hundreds of thousands of SHA-256 rounds and arithmetic operations that drives CPU utilization higher.
- **Health Check Endpoint (`/health`)**: A standard JSON probe allowing Docker and GMT orchestration to confirm the server is ready.
- **Educational UI & JSON API**: Accessible via any web browser or automated CLI/`curl` requests.

---

## Why This Matters for Green Software

1. **Hardware Power Scaling**: Modern CPUs transition through dynamic frequency and power states (P-states and C-states). Idle or lightweight code draws minimal baseline power, whereas CPU-intensive operations draw significantly more electrical power (Watts).
2. **Deterministic Profiling**: By using fixed mathematical iterations rather than random loops, repeated measurements in GMT show consistent, reproducible energy profiles.
3. **Observability via External Telemetry**: The application does not guess its own power draw; instead, GMT attaches external hardware monitors (such as Intel/AMD RAPL sensors and Linux cgroups) to record real physical energy in Joules.

---

## Architecture & How It Works

```
                        +---------------------------------------+
                        |       Green Metrics Tool (GMT)       |
                        |      Hosted Runner / runner.py        |
                        +---------------------------------------+
                                           |
                               Reads usage_scenario.yml
                                           |
                        +---------------------------------------+
                        |          Docker Container             |
                        |      (classroom-demo-app:5000)        |
                        |                                       |
                        |  +-------------+  +----------------+  |
                        |  | Gunicorn/WSGI|  | Flask App      |  |
                        |  +-------------+  +----------------+  |
                        |          |                |           |
                        |          +---> /health    |           |
                        |          +---> /workload/light        |
                        |          +---> /workload/heavy        |
                        +---------------------------------------+
                                           |
                    Hardware RAPL Sensors & cgroup Telemetry Captured
```

---

## Folder Structure

```
green-metrics-classroom-demo/
│
├── app.py                 # Core Flask application with routes and deterministic workloads
├── requirements.txt       # Minimal Python dependencies (Flask, Gunicorn)
├── Dockerfile             # Multi-stage/slim container build with curl healthchecks
├── docker-compose.yml     # Local orchestration for classroom testing
├── usage_scenario.yml     # Official GMT ScenarioRunner specification (phases & flow)
├── .dockerignore          # Keeps Docker build context lean
├── .gitignore             # Standard Python / IDE exclusions
├── README.md              # Classroom documentation and submission instructions
│
├── templates/
│   ├── index.html         # Classroom dashboard with workload triggers and explanation
│   └── result.html        # Execution details, timings, and GMT observation notes
│
└── static/
    └── style.css          # Eco-tech styling, dark slate & emerald palette
```

---

## Running Locally (Without Docker)

### 1. Prerequisites
- Python 3.10+ installed on your machine.

### 2. Setup Virtual Environment
```bash
# Create a virtual environment
python -m venv .venv

# Activate on Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Activate on macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Application
```bash
python app.py
```
Open your browser and visit: **http://localhost:5000**

---

## Running with Docker & Docker Compose

### Option A: Using Docker Compose (Recommended)
```bash
# Build image and start container
docker compose up --build

# Run in background (detached mode)
docker compose up -d --build

# Stop the container
docker compose down
```

### Option B: Using Standalone Docker CLI
```bash
# 1. Build the Docker image
docker build -t green-metrics-classroom-demo:latest .

# 2. Run the container on port 5000
docker run -d --name classroom-demo-app -p 5000:5000 green-metrics-classroom-demo:latest

# 3. Check logs
docker logs -f classroom-demo-app

# 4. Stop and remove container
docker stop classroom-demo-app && docker rm classroom-demo-app
```

---

## Testing Endpoints & Workloads

### 1. Health Endpoint
```bash
# Test health check (returns HTTP 200 JSON)
curl -i http://localhost:5000/health
```

### 2. Lightweight Workload
```bash
# Browser: http://localhost:5000/workload/light
# CLI (JSON):
curl -s "http://localhost:5000/workload/light?format=json"
```

### 3. CPU Intensive Workload
```bash
# Browser: http://localhost:5000/workload/heavy
# CLI (JSON with custom iterations):
curl -s "http://localhost:5000/workload/heavy?iterations=500000&format=json"
```

---

## How GMT ScenarioRunner Uses This Repository

The Green Metrics Tool looks for **`usage_scenario.yml`** in the root of the repository. When executed by GMT, it carries out the following automated phases:

| Phase | GMT Step Name | Action | Educational Purpose |
|---|---|---|---|
| **1** | `01 - Service Readiness & Health Check` | `curl /health` | Validates container startup before measuring. |
| **2** | `02 - Baseline System Idle (5s)` | `sleep 5` | Establishes the baseline idle power consumption of the host machine. |
| **3** | `03 - Lightweight Workload Phase` | `curl /workload/light` | Measures energy during minimal CPU execution. |
| **4** | `04 - Intermission Cooldown (3s)` | `sleep 3` | Allows CPU frequency to stabilize. |
| **5** | `05 - CPU Intensive Workload Phase` | `curl /workload/heavy` | Measures energy spike during heavy CPU computation. |
| **6** | `06 - Post-Workload Cooldown (3s)` | `sleep 3` | Records the descent back to baseline power. |

---

## Submitting to the Hosted Green Metrics Tool

The Green Metrics Tool hosted cluster at [metrics.green-coding.io](https://metrics.green-coding.io/) allows you to run reproducible benchmarks on dedicated reference hardware without requiring local Linux kernel measurement privileges.

### Step 1: Push Code to a Public GitHub Repository
> [!IMPORTANT]
> The hosted GMT ScenarioRunner requires the repository to be **public** so its runner cluster can clone and build the Docker image.
> Do **not** commit passwords, secrets, or local environment files.

```bash
git init
git add .
git commit -m "Initial commit: Green Metrics Classroom Demo"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/green-metrics-classroom-demo.git
git push -u origin main
```

### Step 2: Open the ScenarioRunner Submission Page
Navigate to: **[https://metrics.green-coding.io/](https://metrics.green-coding.io/)** (or the **Request Measurement** tab).

### Step 3: Complete the Submission Form

| Form Field | Value to Enter | Explanation |
|---|---|---|
| **Repository URL** | `https://github.com/YOUR_USERNAME/green-metrics-classroom-demo` | Public URL of your GitHub repository. |
| **Branch / Tag** | `main` (or your branch name) | The Git reference to checkout and test. |
| **Usage Scenario Path** | `usage_scenario.yml` (default) | Path to the scenario file in the repository root. |
| **Machine / Runner** | Select available reference runner | Dedicated hardware with RAPL sensors enabled. |

### Step 4: Submit and Monitor
1. Click **Submit** / **Request Measurement**.
2. GMT will queue your benchmark, clone the repository, build the Docker container, and run all 6 phases defined in `usage_scenario.yml`.
3. Once finished, a detailed interactive dashboard link is generated.

---

## Interpreting Measurement Results

When opening the measurement dashboard on `metrics.green-coding.io`, look for:

1. **RAPL CPU Energy (Joules)**:
   - Notice the step-by-step energy profile.
   - During Phase 3 (Lightweight), energy consumption remains close to baseline.
   - During Phase 5 (CPU Intensive), energy consumption increases noticeably in proportion to CPU work.
2. **cgroup CPU Utilization (%)**:
   - Container-level CPU metric showing the CPU percentage attributed directly to `classroom-demo-app`.
3. **Timeline & Annotations**:
   - The chart includes notes corresponding to each phase name in `usage_scenario.yml`, enabling you to point to exact moments of workload injection during a lecture.

---

## Classroom Demonstration Walkthrough

1. **Introduction (2 mins)**:
   - Present the Home page (`http://localhost:5000`).
   - Explain that software commands consume physical energy in the processor.
2. **Interactive Live Run (3 mins)**:
   - Click **Execute Lightweight Workload** and note execution time (~0.01s).
   - Click **Execute CPU Intensive Workload** and note execution time (~1.0–2.0s).
3. **ScenarioRunner Submission (3 mins)**:
   - Show your GitHub repo and submit it on [metrics.green-coding.io](https://metrics.green-coding.io/).
4. **Analysis & Discussion (5 mins)**:
   - Review the resulting graphs together.
   - Compare the Joules consumed across phases and discuss algorithmic optimization for sustainability.
