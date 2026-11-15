
import json
from pathlib import Path

import numpy as np
import pandas as pd


def calculate_total_consumption(records):
    """
    Calculate total electricity consumption using NumPy.
    """

    consumption = np.array(
        [record.consumption_kwh for record in records],
        dtype=float
    )

    return round(float(np.sum(consumption)), 2)


def calculate_building_consumption(records):
    """
    Calculate total and average consumption for each building.
    """

    building_data = {}

    for record in records:
        building_data.setdefault(
            record.building_name, []
        ).append(record.consumption_kwh)

    summary = {}

    for building, readings in building_data.items():

        values = np.array(readings, dtype=float)

        summary[building] = {
            "total_kwh": round(float(np.sum(values)), 2),
            "average_kwh": round(float(np.mean(values)), 2),
            "maximum_kwh": round(float(np.max(values)), 2),
            "minimum_kwh": round(float(np.min(values)), 2)
        }

    return summary


def calculate_moving_averages(records, window=3):
    """
    Calculate moving averages using NumPy.
    Uses the previous three observations for each building.
    """

    if window < 1:
        raise ValueError("Window must be at least 1.")

    building_data = {}

    for record in records:
        building_data.setdefault(
            record.building_id, []
        ).append(record)

    results = []

    for building_id, building_records in building_data.items():

        building_records.sort(
            key=lambda record: record.reading_date
        )

        values = np.array(
            [record.consumption_kwh for record in building_records],
            dtype=float
        )

        if len(values) < window:
            continue

        averages = np.convolve(
            values,
            np.ones(window) / window,
            mode="valid"
        )

        for index, average in enumerate(averages):

            results.append({
                "building_id": building_id,
                "building_name": building_records[index + window - 1].building_name,
                "reading_date": building_records[index + window - 1].reading_date,
                "moving_average_kwh": round(float(average), 2)
            })

    return results


def create_monthly_summary(records):
    """
    Create monthly electricity consumption summaries using Pandas.
    """

    data = [
        {
            "building_name": record.building_name,
            "reading_date": record.reading_date,
            "consumption_kwh": record.consumption_kwh
        }
        for record in records
    ]

    df = pd.DataFrame(data)

    if df.empty:
        return pd.DataFrame(
            columns=[
                "month",
                "building_name",
                "total_kwh",
                "average_kwh",
                "record_count"
            ]
        )

    df["reading_date"] = pd.to_datetime(
        df["reading_date"],
        errors="raise"
    )

    df["month"] = df["reading_date"].dt.to_period("M").astype(str)

    monthly_summary = (
        df.groupby(["month", "building_name"])
        .agg(
            total_kwh=("consumption_kwh", "sum"),
            average_kwh=("consumption_kwh", "mean"),
            record_count=("consumption_kwh", "count")
        )
        .reset_index()
    )

    monthly_summary["total_kwh"] = monthly_summary["total_kwh"].round(2)
    monthly_summary["average_kwh"] = monthly_summary["average_kwh"].round(2)

    return monthly_summary


def export_json_report(records, building_summary, monthly_summary, output_file):
    """
    Export energy analysis results into a JSON report.
    """

    report = {
        "total_records": len(records),
        "total_consumption_kwh": calculate_total_consumption(records),
        "building_summary": building_summary,
        "monthly_summary": monthly_summary.to_dict(orient="records"),
        "meter_records": [record.to_dict() for record in records]
    }

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    return report
