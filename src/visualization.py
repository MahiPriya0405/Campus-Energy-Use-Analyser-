
import matplotlib.pyplot as plt
from pathlib import Path


# Graph output directory
GRAPH_DIR = Path(__file__).resolve().parent.parent / "graphs"


def plot_monthly_energy_trends(monthly_summary):
    """
    Create a line chart showing monthly recorded
    electricity consumption for each building.
    """

    if monthly_summary.empty:
        raise ValueError("Monthly summary contains no data.")

    GRAPH_DIR.mkdir(parents=True, exist_ok=True)

    # Convert monthly data into chart-friendly format
    pivot_data = monthly_summary.pivot(
        index="month",
        columns="building_name",
        values="total_kwh"
    )

    plt.figure(figsize=(12, 6))

    for building in pivot_data.columns:
        plt.plot(
            pivot_data.index,
            pivot_data[building],
            marker="o",
            linewidth=2,
            label=building
        )

    plt.title(
        "Monthly Recorded Electricity Consumption by Building",
        fontsize=14,
        fontweight="bold"
    )

    plt.xlabel("Month")
    plt.ylabel("Recorded Consumption (kWh)")

    plt.xticks(rotation=30)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(title="Campus Buildings")
    plt.tight_layout()

    output_path = GRAPH_DIR / "monthly_energy_trends.png"

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    return output_path


def plot_building_consumption(building_summary):
    """
    Create a bar chart comparing total recorded
    electricity consumption across campus buildings.
    """

    if not building_summary:
        raise ValueError("Building summary contains no data.")

    GRAPH_DIR.mkdir(parents=True, exist_ok=True)

    buildings = list(building_summary.keys())

    consumption = [
        details["total_kwh"]
        for details in building_summary.values()
    ]

    plt.figure(figsize=(11, 6))

    bars = plt.bar(
        buildings,
        consumption,
        edgecolor="black"
    )

    plt.title(
        "Total Recorded Electricity Consumption by Building",
        fontsize=14,
        fontweight="bold"
    )

    plt.xlabel("Campus Buildings")
    plt.ylabel("Recorded Consumption (kWh)")

    plt.xticks(rotation=25, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    # Display consumption values above each bar
    for bar, value in zip(bars, consumption):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=9
        )

    plt.tight_layout()

    output_path = GRAPH_DIR / "building_consumption_comparison.png"

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    return output_path
