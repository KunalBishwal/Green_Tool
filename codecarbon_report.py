"""
CodeCarbon Visual Comparison Report Generator
----------------------------------------------
Reads `codecarbon_results.json` and generates a clean, presentation-ready
comparison chart (`codecarbon_comparison.png`) comparing:
- Energy Consumed (kWh)
- Carbon Emissions (kg CO2eq)
"""

import os
import sys
import json
import matplotlib.pyplot as plt

RESULTS_JSON = "codecarbon_results.json"
OUTPUT_IMAGE = "codecarbon_comparison.png"


def generate_report():
    if not os.path.exists(RESULTS_JSON):
        print(f"Error: '{RESULTS_JSON}' not found.")
        print("Please run 'python codecarbon_benchmark.py' first to produce benchmark measurements.")
        sys.exit(1)

    with open(RESULTS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    light = data["light_workload"]
    heavy = data["heavy_workload"]
    comparison = data.get("comparison", {})

    workload_labels = ["Lightweight\nWorkload", "CPU Intensive\nWorkload"]
    energy_values = [light["energy_kwh"], heavy["energy_kwh"]]
    emissions_values = [light["emissions_kg_co2eq"], heavy["emissions_kg_co2eq"]]

    # Dark modern theme styling matching project UI
    bg_color = "#0b0f19"
    card_color = "#111827"
    text_primary = "#f9fafb"
    text_secondary = "#9ca3af"
    grid_color = "#1f2937"
    emerald_color = "#10b981"
    amber_color = "#f59e0b"

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5))
    fig.patch.set_facecolor(bg_color)

    bar_colors = [emerald_color, amber_color]

    # ------------------------------------------------------------
    # Panel 1: Energy Consumption (kWh)
    # ------------------------------------------------------------
    ax1.set_facecolor(card_color)
    bars1 = ax1.bar(workload_labels, energy_values, color=bar_colors, width=0.45, edgecolor="#374151", linewidth=1.2)
    ax1.set_title("Estimated Energy Consumed\n(kWh)", fontsize=13, fontweight="bold", color=text_primary, pad=12)
    ax1.set_ylabel("Energy (kWh)", fontsize=11, color=text_secondary)
    ax1.tick_params(colors=text_primary, labelsize=10)
    ax1.grid(axis="y", color=grid_color, linestyle="--", alpha=0.7)
    for spine in ax1.spines.values():
        spine.set_color("#374151")

    # Annotate bar values
    max_energy = max(energy_values) if max(energy_values) > 0 else 1.0
    ax1.set_ylim(0, max_energy * 1.25)
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(
            f"{height:.2e}\nkWh",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=9.5, fontweight="600",
            color=text_primary
        )

    energy_ratio = comparison.get("energy_ratio")
    if energy_ratio is not None:
        ax1.text(
            0.5, 0.92, f"Heavy / Light: {energy_ratio:.2f}x Energy",
            transform=ax1.transAxes, ha="center", va="top",
            fontsize=10, fontweight="bold", color=amber_color,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#1f2937", edgecolor="#4b5563", alpha=0.8)
        )

    # ------------------------------------------------------------
    # Panel 2: Carbon Emissions (kg CO2eq)
    # ------------------------------------------------------------
    ax2.set_facecolor(card_color)
    bars2 = ax2.bar(workload_labels, emissions_values, color=bar_colors, width=0.45, edgecolor="#374151", linewidth=1.2)
    ax2.set_title("Estimated Carbon Emissions\n(kg CO2eq)", fontsize=13, fontweight="bold", color=text_primary, pad=12)
    ax2.set_ylabel("Emissions (kg CO2eq)", fontsize=11, color=text_secondary)
    ax2.tick_params(colors=text_primary, labelsize=10)
    ax2.grid(axis="y", color=grid_color, linestyle="--", alpha=0.7)
    for spine in ax2.spines.values():
        spine.set_color("#374151")

    max_emissions = max(emissions_values) if max(emissions_values) > 0 else 1.0
    ax2.set_ylim(0, max_emissions * 1.25)
    for bar in bars2:
        height = bar.get_height()
        ax2.annotate(
            f"{height:.2e}\nkg CO2eq",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=9.5, fontweight="600",
            color=text_primary
        )

    emissions_ratio = comparison.get("emissions_ratio")
    if emissions_ratio is not None:
        ax2.text(
            0.5, 0.92, f"Heavy / Light: {emissions_ratio:.2f}x CO2eq",
            transform=ax2.transAxes, ha="center", va="top",
            fontsize=10, fontweight="bold", color=amber_color,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#1f2937", edgecolor="#4b5563", alpha=0.8)
        )

    # Supertitle & note
    plt.suptitle("CodeCarbon Green Software Benchmark - Workload Comparison", fontsize=15, fontweight="bold", color=text_primary, y=0.98)
    fig.text(
        0.5, 0.02,
        "Note: CodeCarbon estimates consumption using CPU model TDP, process utilization, and regional emission factors.",
        ha="center", fontsize=8.5, color=text_secondary
    )

    plt.tight_layout(rect=[0.02, 0.05, 0.98, 0.94])
    plt.savefig(OUTPUT_IMAGE, dpi=180, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()

    print(f"\n[Visual Report] Comparison chart successfully saved to: {OUTPUT_IMAGE}")


if __name__ == "__main__":
    generate_report()
