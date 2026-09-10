# Green Metrics Classroom Demo

An educational, self-contained Python Flask application demonstrating how software computational workloads affect CPU utilization and energy consumption, tailored for benchmarking with the **Green Metrics Tool (GMT)** and its hosted **ScenarioRunner** at [metrics.green-coding.io](https://metrics.green-coding.io/).

---

### Table of Contents
1. [Project Overview](#project-overview)
2. [Why This Matters for Green Software](#why-this-matters-for-green-software)
3. [Architecture & How It Works](#architecture--how-it-works)
4. [Folder Structure](#folder-structure)
5. [Running Locally (Without Docker)](#running-locally-without-docker)
6. [Running with Docker & Docker Compose](#running-with-docker--docker-compose)
7. [Testing Endpoints & Workloads](#testing-endpoints--workloads)
8. [CodeCarbon Energy & Carbon Measurement](#codecarbon-energy--carbon-measurement)
9. [How GMT ScenarioRunner Uses This Repository](#how-gmt-scenariorunner-uses-this-repository)
10. [Submitting to the Hosted Green Metrics Tool](#submitting-to-the-hosted-green-metrics-tool)
11. [Interpreting Measurement Results](#interpreting-measurement-results)
12. [Classroom Demonstration Walkthrough](#classroom-demonstration-walkthrough)

---

## Project Overview

In traditional software development, code is primarily evaluated by latency, throughput, and functionality. **Green Software Engineering** introduces an essential additional metric: **Energy & Carbon Efficiency**.

This project provides a clean, visual classroom demonstration:
- **Lightweight Workload (`/workload/light`)**: A minimal, low-overhead transaction with near-zero CPU state change.
- **CPU-Intensive Workload (`/workload/heavy`)**: A bounded, deterministic computational task performing hundreds of thousands of SHA-256 rounds and arithmetic operations that drives CPU utilization higher.
- **Health Check Endpoint (`/health`)**: A standard JSON probe allowing Docker and GMT orchestration to confirm the server is ready.
- **CodeCarbon Benchmark (`/codecarbon`)**: Secondary in-process measurement and visualization comparing energy and emissions.
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
                        |          +---> /codecarbon (report)   |
                        +---------------------------------------+
                                           |
                     Hardware RAPL Sensors & cgroup Telemetry Captured
```

---

## Folder Structure

```
green-metrics-classroom-demo/
│
├── app.py                      # Core Flask application with routes and deterministic workloads
├── codecarbon_benchmark.py     # CodeCarbon benchmark script measuring light vs heavy workloads
├── codecarbon_report.py        # Visual comparison chart generator (codecarbon_comparison.png)
├── benchmark_summary.txt       # Saved terminal output comparing Light vs Heavy workloads
├── requirements.txt            # Python dependencies (Flask, Gunicorn, CodeCarbon, Matplotlib)
├── Dockerfile                  # Multi-stage/slim container build with curl healthchecks
├── docker-compose.yml          # Local orchestration for classroom testing
├── usage_scenario.yml          # Official GMT ScenarioRunner specification (phases & flow)
├── .dockerignore               # Keeps Docker build context lean
├── .gitignore                  # Standard Python / IDE / benchmark result exclusions
├── README.md                   # Classroom documentation and submission instructions
│
├── templates/
│   ├── index.html              # Classroom dashboard with workload triggers and telemetry links
│   ├── result.html             # Execution details, timings, and GMT observation notes
│   └── codecarbon.html         # CodeCarbon measurement dashboard with comparison stats & chart
│
└── static/
    └── style.css               # Eco-tech styling, dark slate & emerald palette
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

## CodeCarbon Energy & Carbon Measurement

### 1. What is CodeCarbon?
[CodeCarbon](https://codecarbon.io/) is an open-source Python package developed to estimate the carbon footprint produced by computing workloads. It tracks system resources during program execution and computes the corresponding electricity consumption and greenhouse gas emissions.

### 2. Why Use CodeCarbon as a Secondary Measurement Method?
The primary measurement tool in this project is the **Green Metrics Tool (GMT)**, which measures true physical energy via Linux kernel cgroups and hardware RAPL registers in a specialized container environment.

However, in many classroom or development scenarios:
- Students work on Windows or macOS laptops where Linux RAPL / cgroup counters are inaccessible.
- Hardware permissions or virtualized container layers (WSL2, Docker Desktop) abstract physical power meters.
- Fast local verification is desired without triggering a cloud runner queue.

**CodeCarbon acts as an accessible secondary telemetry tool** that runs directly within Python, allowing students to compare algorithms locally without specialized server hardware.

### 3. Understanding the Metrics & Accuracy Requirements

> [!IMPORTANT]
> **Estimation vs Physical Measurement**: CodeCarbon does **not** directly measure electrical current using physical laboratory ammeters. Instead, it **estimates** electrical energy and carbon emissions based on:
> 1. CPU architecture and known manufacturer **TDP (Thermal Design Power)**.
> 2. Measured **process CPU utilization** (via `psutil`).
> 3. Regional electricity grid **carbon intensity factors** (grams of CO2 per kWh) based on machine IP/location.

Be careful to clearly distinguish physical units in classroom discussions:
- **Power ($W$ or $kW$)**: Instantaneous rate of energy transfer.
- **Energy Consumed ($kWh$ or $J$)**: Total work accumulated over time ($1\text{ kWh} = 3.6 \times 10^6\text{ Joules}$).
- **Carbon Emissions ($kg\text{ CO}_2\text{eq}$)**: Mass of greenhouse gas emissions attributed to generating the consumed energy.

### 4. Running the CodeCarbon Benchmark

Because CodeCarbon samples hardware utilization periodically (configured to 1-second intervals in this demo), extremely short workloads (< 1 second) can produce tiny or unrepresentative measurements. To solve this, `codecarbon_benchmark.py` repeats deterministic workload batches across a ~5–10 second measurement window:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Execute the benchmark
python codecarbon_benchmark.py
```

The script runs:
1. **Lightweight Workload**: 2,000 iterations $\times$ 50 rounds ($100,000$ total iterations).
2. **Intermission Cooldown**: 3 seconds to let CPU frequencies return to baseline.
3. **CPU Intensive Workload**: 500,000 iterations $\times$ 10 rounds ($5,000,000$ total iterations).

Repetition counts can be adjusted via `LIGHT_REPETITIONS` and `HEAVY_REPETITIONS` at the top of `codecarbon_benchmark.py`.

### 5. Benchmark Output Files

The benchmark produces four files in the project root:
- **`emissions_light.csv`**: Raw CodeCarbon telemetry for the lightweight phase (CPU power, GPU power, RAM power, energy consumed, emissions).
- **`emissions_heavy.csv`**: Raw CodeCarbon telemetry for the heavy CPU phase.
- **`codecarbon_results.json`**: Machine-readable JSON summary containing actual measured duration, energy ($kWh$), carbon ($kg\text{ CO}_2\text{eq}$), and comparison ratios.
- **`benchmark_summary.txt`**: Human-readable classroom presentation terminal report.

#### Sample Measured Terminal Output (`benchmark_summary.txt`)
```text
============================================================
        CODECARBON GREEN SOFTWARE BENCHMARK
============================================================

Lightweight Workload
------------------------------------------------------------
Iterations       : 100,000 (2,000 x 50 rounds)
Duration         : 5.8013 seconds
Energy           : 0.00001306 kWh (1.306e-05 kWh)
CO2 emissions    : 0.00000932 kg CO2eq (9.319e-06 kg CO2eq)

CPU Intensive Workload
------------------------------------------------------------
Iterations       : 5,000,000 (500,000 x 10 rounds)
Duration         : 21.3332 seconds
Energy           : 0.00025755 kWh (2.576e-04 kWh)
CO2 emissions    : 0.00041364 kg CO2eq (4.136e-04 kg CO2eq)

Comparison
------------------------------------------------------------
Heavy / Light Energy Ratio    : 19.72x
Heavy / Light CO2 Ratio       : 44.39x
Heavy / Light Runtime Ratio   : 3.68x

============================================================
Results saved to:
- emissions_light.csv
- emissions_heavy.csv
- codecarbon_results.json
- benchmark_summary.txt
============================================================
```

### 6. Generating the Visual Report Chart

To produce a presentation-ready dual-panel bar chart comparing Light vs Heavy workloads:

```bash
python codecarbon_report.py
```

This generates **`codecarbon_comparison.png`**, which visualizes:
- **Energy Consumed (kWh)** for Light vs Heavy workloads with ratio multipliers.
- **Estimated Carbon Emissions (kg CO2eq)** for Light vs Heavy workloads.

### 7. Viewing Results in the Web Application

When the Flask server is running (`python app.py`), navigate to:
- **HTML Dashboard**: [http://localhost:5000/codecarbon](http://localhost:5000/codecarbon)
- **JSON API**: [http://localhost:5000/codecarbon?format=json](http://localhost:5000/codecarbon?format=json)
- **Chart Endpoint**: [http://localhost:5000/codecarbon/chart](http://localhost:5000/codecarbon/chart)

> [!NOTE]
> The `/codecarbon` route strictly reads the pre-computed `codecarbon_results.json` file. It does **not** re-run the benchmark on web requests to keep the web server fast and responsive.

### 8. Architectural Comparison: GMT vs CodeCarbon

| Dimension | Green Metrics Tool (GMT) | CodeCarbon |
|---|---|---|
| **Measurement Level** | System / Kernel / Container | Process / Application |
| **Telemetry Source** | Intel/AMD RAPL hardware registers | CPU TDP $\times$ Process Utilization |
| **Execution Environment** | Isolated Linux containers & cgroups | Any Python host runtime |
| **Energy Metric** | Joules ($J$) | Kilowatt-hours ($kWh$) |
| **Primary Use Case** | Automated reproducible CI/CD benchmarks | Local algorithm exploration & classroom demos |

### 9. Host vs Docker Recommendation
- For GMT benchmarks, **Docker is required** (via `usage_scenario.yml`).
- For CodeCarbon benchmarks, **running directly on the host machine (`python codecarbon_benchmark.py`) is recommended**. Virtualized container runtimes (such as Docker Desktop on Windows/macOS) hide direct CPU hardware model information and host power counters from CodeCarbon.

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
