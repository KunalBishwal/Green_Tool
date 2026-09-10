"""
Green Metrics Classroom Demo - Application Server
------------------------------------------------
A simple, self-contained Python Flask application designed to demonstrate
software energy and resource consumption metrics using the Green Metrics Tool (GMT).

Key Objectives:
1. Provide a lightweight workload with minimal CPU consumption.
2. Provide a deterministic CPU-intensive workload with measurable resource usage.
3. Expose a standard /health endpoint for Docker & GMT orchestration.
4. Support both human-friendly HTML UI and automated JSON API responses.
"""

import time
import hashlib
import math
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Application Configuration
DEFAULT_LIGHT_ITERATIONS = 2_000
DEFAULT_HEAVY_ITERATIONS = 500_000
MAX_SAFE_ITERATIONS = 2_000_000  # Hard safety cap to prevent resource exhaustion


def is_json_requested():
    """Helper to detect whether the client wants a JSON response (CLI/curl/GMT) or HTML (browser)."""
    if request.args.get("format") == "json":
        return True
    best = request.accept_mimetypes.best_match(["application/json", "text/html"])
    return best == "application/json" and request.accept_mimetypes[best] > request.accept_mimetypes["text/html"]


def run_deterministic_cpu_workload(iterations: int, seed_phrase: str = "GreenSoftwareClassroomDemo") -> dict:
    """
    Executes a deterministic CPU-bound workload using cryptographic hashing (SHA-256)
    and square root calculations. This produces consistent CPU load across repeated runs
    without memory spikes, network calls, or non-deterministic behavior.
    """
    start_time = time.perf_counter()
    
    current_hash = hashlib.sha256(seed_phrase.encode("utf-8")).hexdigest()
    checksum = 0.0

    for i in range(iterations):
        # Deterministic hashing chain
        current_hash = hashlib.sha256((current_hash + str(i)).encode("utf-8")).hexdigest()
        # Light arithmetic to exercise floating-point units deterministically
        checksum += math.sqrt((i % 1000) + 1.0)

    end_time = time.perf_counter()
    duration_ms = round((end_time - start_time) * 1000, 2)
    duration_s = round(end_time - start_time, 4)

    return {
        "iterations": iterations,
        "duration_ms": duration_ms,
        "duration_seconds": duration_s,
        "final_hash_sample": current_hash[:16] + "...",
        "checksum": round(checksum, 4)
    }


@app.route("/")
def index():
    """Home page explaining Green Software concepts and providing workload triggers."""
    return render_template(
        "index.html",
        default_light=DEFAULT_LIGHT_ITERATIONS,
        default_heavy=DEFAULT_HEAVY_ITERATIONS,
        max_safe=MAX_SAFE_ITERATIONS
    )


@app.route("/health", methods=["GET"])
def health():
    """
    Standard Health Check Endpoint.
    Used by Docker healthcheck and GMT ScenarioRunner to verify application readiness.
    """
    return jsonify({
        "status": "healthy",
        "service": "Green Metrics Classroom Demo",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "framework": "Flask"
    }), 200


@app.route("/workload/light", methods=["GET", "POST"])
def workload_light():
    """
    Lightweight Workload Endpoint.
    Performs a small, low-impact computation suitable for baseline comparisons.
    """
    try:
        iterations = int(request.args.get("iterations", DEFAULT_LIGHT_ITERATIONS))
        iterations = min(max(100, iterations), MAX_SAFE_ITERATIONS)
    except (ValueError, TypeError):
        iterations = DEFAULT_LIGHT_ITERATIONS

    result = run_deterministic_cpu_workload(iterations=iterations, seed_phrase="LightweightBaseline")
    result["workload_type"] = "Lightweight Workload"
    result["description"] = "Low CPU impact computation simulating a quick, minimal transaction."
    result["gmt_explanation"] = (
        "During this lightweight phase, the CPU operates near idle frequency. "
        "The Green Metrics Tool's RAPL sensors should record minimal additional energy above the system baseline."
    )

    if is_json_requested():
        return jsonify(result)

    return render_template("result.html", data=result)


@app.route("/workload/heavy", methods=["GET", "POST"])
def workload_heavy():
    """
    CPU Intensive Workload Endpoint.
    Performs a deterministic, bounded calculation producing measurable CPU utilization
    and increased electrical power consumption.
    """
    try:
        iterations = int(request.args.get("iterations", DEFAULT_HEAVY_ITERATIONS))
        # Enforce safety limits
        iterations = min(max(10_000, iterations), MAX_SAFE_ITERATIONS)
    except (ValueError, TypeError):
        iterations = DEFAULT_HEAVY_ITERATIONS

    result = run_deterministic_cpu_workload(iterations=iterations, seed_phrase="HeavyCPUStressTest")
    result["workload_type"] = "CPU Intensive Workload"
    result["description"] = f"Heavy CPU computation performing {iterations:,} iterative rounds of SHA-256 and math operations."
    result["gmt_explanation"] = (
        "During this phase, CPU cores spike in utilization and clock frequency. "
        "The Green Metrics Tool captures this energy increase in Joules via RAPL (Running Average Power Limit) "
        "and tracks container-level cgroup CPU time."
    )

    if is_json_requested():
        return jsonify(result)

    return render_template("result.html", data=result)


if __name__ == "__main__":
    # Run development server listening on all network interfaces
    print("Starting Green Metrics Classroom Demo on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
