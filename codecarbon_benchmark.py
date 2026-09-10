"""
CodeCarbon Green Software Benchmark
-----------------------------------
A standalone benchmarking script that measures and compares the estimated electrical
energy consumption (kWh) and carbon emissions (kg CO2eq) of lightweight vs CPU-intensive
workloads using CodeCarbon.

Key Design Points:
1. Re-uses the deterministic SHA-256 + arithmetic workload from app.py.
2. Uses CodeCarbon's EmissionsTracker in process tracking mode ('process') to isolate
   the energy attributable to this specific benchmark workload.
3. Repeats deterministic batches to create a measurable time window (~5-10s each)
   for CodeCarbon's periodic power sampling mechanism.
4. Exports separate CSV files for each workload and a unified JSON comparison file.
5. Displays a classroom-friendly terminal report with actual measured values.
"""

import os
import json
import time
from datetime import datetime, timezone
from codecarbon import EmissionsTracker
from app import run_deterministic_cpu_workload

# ============================================================
# BENCHMARK CONFIGURATION
# ============================================================
# Base iteration count per workload cycle (matching app.py defaults)
LIGHT_BASE_ITERATIONS = 2_000
HEAVY_BASE_ITERATIONS = 500_000

# Number of repetitions to establish a reliable measurement window
# CodeCarbon samples power periodically (every 1s here). Extremely short
# tasks (< 1s) cannot be reliably sampled. These counts produce a reliable
# window (~7-8s for light, ~35-40s for heavy) to clearly contrast energy draw.
LIGHT_REPETITIONS = 50      # 50 x 2,000 = 100,000 iterations (~7-8s window)
HEAVY_REPETITIONS = 10      # 10 x 500,000 = 5,000,000 iterations (~35-40s window)

# Intermission cooldown (seconds) to allow CPU to return toward idle
INTERMISSION_COOLDOWN_SECONDS = 3

# Output file paths
LIGHT_CSV = "emissions_light.csv"
HEAVY_CSV = "emissions_heavy.csv"
RESULTS_JSON = "codecarbon_results.json"
SUMMARY_TXT = "benchmark_summary.txt"


def run_benchmark():
    print("\n" + "=" * 60)
    print("        CODECARBON GREEN SOFTWARE BENCHMARK")
    print("=" * 60)
    print("Initializing CodeCarbon environment and sensors...")

    # Remove previous CSV outputs if present to ensure clean single-run logs
    for path in [LIGHT_CSV, HEAVY_CSV]:
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass

    # ------------------------------------------------------------
    # 1. LIGHTWEIGHT WORKLOAD PHASE
    # ------------------------------------------------------------
    total_light_iterations = LIGHT_BASE_ITERATIONS * LIGHT_REPETITIONS
    print(f"\n[1/2] Starting Lightweight Workload...")
    print(f"      - Base iterations/cycle : {LIGHT_BASE_ITERATIONS:,}")
    print(f"      - Repetition rounds     : {LIGHT_REPETITIONS:,}")
    print(f"      - Total iterations      : {total_light_iterations:,}")
    print("      Tracking with CodeCarbon (process mode)...")

    light_tracker = EmissionsTracker(
        project_name="Green Metrics - Lightweight Workload",
        measure_power_secs=1,
        tracking_mode="process",
        output_dir=".",
        output_file=LIGHT_CSV,
        save_to_file=True,
        log_level="warning",
        allow_multiple_runs=True,
    )

    light_tracker.start()
    light_start_wall = time.perf_counter()
    for _ in range(LIGHT_REPETITIONS):
        run_deterministic_cpu_workload(LIGHT_BASE_ITERATIONS, seed_phrase="LightweightBaseline")
    light_emissions = light_tracker.stop()
    light_wall_duration = time.perf_counter() - light_start_wall

    # Extract CodeCarbon final emissions telemetry
    light_data = light_tracker.final_emissions_data
    light_energy_kwh = float(light_data.energy_consumed) if light_data and light_data.energy_consumed is not None else 0.0
    light_duration_s = float(light_data.duration) if light_data and light_data.duration is not None else light_wall_duration
    light_emissions_kg = float(light_emissions) if light_emissions is not None else (
        float(light_data.emissions) if light_data and light_data.emissions is not None else 0.0
    )

    print(f"      Lightweight phase completed in {light_duration_s:.2f}s.")

    # ------------------------------------------------------------
    # INTERMISSION COOLDOWN
    # ------------------------------------------------------------
    print(f"\n[Intermission] Cooling down for {INTERMISSION_COOLDOWN_SECONDS}s to stabilize CPU state...")
    time.sleep(INTERMISSION_COOLDOWN_SECONDS)

    # ------------------------------------------------------------
    # 2. CPU INTENSIVE WORKLOAD PHASE
    # ------------------------------------------------------------
    total_heavy_iterations = HEAVY_BASE_ITERATIONS * HEAVY_REPETITIONS
    print(f"\n[2/2] Starting CPU Intensive Workload...")
    print(f"      - Base iterations/cycle : {HEAVY_BASE_ITERATIONS:,}")
    print(f"      - Repetition rounds     : {HEAVY_REPETITIONS:,}")
    print(f"      - Total iterations      : {total_heavy_iterations:,}")
    print("      Tracking with CodeCarbon (process mode)...")

    heavy_tracker = EmissionsTracker(
        project_name="Green Metrics - CPU Intensive Workload",
        measure_power_secs=1,
        tracking_mode="process",
        output_dir=".",
        output_file=HEAVY_CSV,
        save_to_file=True,
        log_level="warning",
        allow_multiple_runs=True,
    )

    heavy_tracker.start()
    heavy_start_wall = time.perf_counter()
    for _ in range(HEAVY_REPETITIONS):
        run_deterministic_cpu_workload(HEAVY_BASE_ITERATIONS, seed_phrase="HeavyCPUStressTest")
    heavy_emissions = heavy_tracker.stop()
    heavy_wall_duration = time.perf_counter() - heavy_start_wall

    # Extract CodeCarbon final emissions telemetry
    heavy_data = heavy_tracker.final_emissions_data
    heavy_energy_kwh = float(heavy_data.energy_consumed) if heavy_data and heavy_data.energy_consumed is not None else 0.0
    heavy_duration_s = float(heavy_data.duration) if heavy_data and heavy_data.duration is not None else heavy_wall_duration
    heavy_emissions_kg = float(heavy_emissions) if heavy_emissions is not None else (
        float(heavy_data.emissions) if heavy_data and heavy_data.emissions is not None else 0.0
    )

    print(f"      CPU intensive phase completed in {heavy_duration_s:.2f}s.")

    # ------------------------------------------------------------
    # RATIO CALCULATIONS (WITH SAFE ZERO HANDLING)
    # ------------------------------------------------------------
    def calc_ratio(heavy_val: float, light_val: float):
        if light_val > 0:
            return round(heavy_val / light_val, 2)
        return None

    energy_ratio = calc_ratio(heavy_energy_kwh, light_energy_kwh)
    emissions_ratio = calc_ratio(heavy_emissions_kg, light_emissions_kg)
    duration_ratio = calc_ratio(heavy_duration_s, light_duration_s)

    def format_ratio(ratio):
        return f"{ratio:.2f}x" if ratio is not None else "N/A"

    # ------------------------------------------------------------
    # SAVE STRUCTURED JSON REPORT
    # ------------------------------------------------------------
    results = {
        "tool": "CodeCarbon",
        "project": "Green Metrics Classroom Demo",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tracking_mode": "process",
        "estimation_note": (
            "CodeCarbon estimates energy and CO2-equivalent emissions using CPU model TDP, "
            "process CPU utilization, and regional grid carbon intensity factors."
        ),
        "light_workload": {
            "iterations": total_light_iterations,
            "base_iterations": LIGHT_BASE_ITERATIONS,
            "repetitions": LIGHT_REPETITIONS,
            "duration_seconds": round(light_duration_s, 4),
            "energy_kwh": light_energy_kwh,
            "emissions_kg_co2eq": light_emissions_kg,
        },
        "heavy_workload": {
            "iterations": total_heavy_iterations,
            "base_iterations": HEAVY_BASE_ITERATIONS,
            "repetitions": HEAVY_REPETITIONS,
            "duration_seconds": round(heavy_duration_s, 4),
            "energy_kwh": heavy_energy_kwh,
            "emissions_kg_co2eq": heavy_emissions_kg,
        },
        "comparison": {
            "energy_ratio": energy_ratio,
            "emissions_ratio": emissions_ratio,
            "duration_ratio": duration_ratio,
        },
    }

    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # ------------------------------------------------------------
    # CLASSROOM PRESENTATION TERMINAL OUTPUT & FILE EXPORT
    # ------------------------------------------------------------
    summary_text = (
        "=" * 60 + "\n"
        "        CODECARBON GREEN SOFTWARE BENCHMARK\n"
        "=" * 60 + "\n\n"
        "Lightweight Workload\n"
        + "-" * 60 + "\n"
        + f"Iterations       : {total_light_iterations:,} ({LIGHT_BASE_ITERATIONS:,} x {LIGHT_REPETITIONS:,} rounds)\n"
        + f"Duration         : {light_duration_s:.4f} seconds\n"
        + f"Energy           : {light_energy_kwh:.8f} kWh ({light_energy_kwh:.3e} kWh)\n"
        + f"CO2 emissions    : {light_emissions_kg:.8f} kg CO2eq ({light_emissions_kg:.3e} kg CO2eq)\n\n"
        + "CPU Intensive Workload\n"
        + "-" * 60 + "\n"
        + f"Iterations       : {total_heavy_iterations:,} ({HEAVY_BASE_ITERATIONS:,} x {HEAVY_REPETITIONS:,} rounds)\n"
        + f"Duration         : {heavy_duration_s:.4f} seconds\n"
        + f"Energy           : {heavy_energy_kwh:.8f} kWh ({heavy_energy_kwh:.3e} kWh)\n"
        + f"CO2 emissions    : {heavy_emissions_kg:.8f} kg CO2eq ({heavy_emissions_kg:.3e} kg CO2eq)\n\n"
        + "Comparison\n"
        + "-" * 60 + "\n"
        + f"Heavy / Light Energy Ratio    : {format_ratio(energy_ratio)}\n"
        + f"Heavy / Light CO2 Ratio       : {format_ratio(emissions_ratio)}\n"
        + f"Heavy / Light Runtime Ratio   : {format_ratio(duration_ratio)}\n\n"
        + "=" * 60 + "\n"
        + "Results saved to:\n"
        + f"- {LIGHT_CSV}\n"
        + f"- {HEAVY_CSV}\n"
        + f"- {RESULTS_JSON}\n"
        + f"- {SUMMARY_TXT}\n"
        + "=" * 60 + "\n"
    )

    print("\n" + summary_text)

    with open(SUMMARY_TXT, "w", encoding="utf-8") as f:
        f.write(summary_text)

    return results


if __name__ == "__main__":
    run_benchmark()
