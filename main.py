
from datetime import datetime

from src.models import MeterRecord

from src.data_manager import (
    load_records,
    add_record,
    search_records,
    update_record,
    delete_record
)

from src.validation import (
    validate_records,
    flag_abnormal_readings
)

from src.analysis import (
    calculate_total_consumption,
    calculate_building_consumption,
    calculate_moving_averages,
    create_monthly_summary,
    export_json_report
)

from src.visualization import (
    plot_monthly_energy_trends,
    plot_building_consumption
)


# Available campus buildings
BUILDINGS = {
    "1": ("B001", "Academic Block A", "MTR001"),
    "2": ("B002", "Central Library", "MTR002"),
    "3": ("B003", "Computer Lab Block", "MTR003"),
    "4": ("B004", "Administration Block", "MTR004"),
    "5": ("B005", "Boys Hostel", "MTR005"),
    "6": ("B006", "Auditorium", "MTR006")
}


def load_project_data():
    """Load and validate the latest CSV records."""

    records = load_records()
    valid_records, issues = validate_records(records)

    return records, valid_records, issues


def print_record(record):
    """Display one meter record."""

    print("\nRecord ID       :", record.record_id)
    print("Building ID     :", record.building_id)
    print("Building Name   :", record.building_name)
    print("Meter ID        :", record.meter_id)
    print("Reading Date    :", record.reading_date)
    print("Consumption     :", record.consumption_kwh, "kWh")


def generate_record_id(records):
    """Generate the next available record ID."""

    numbers = []

    for record in records:
        record_id = record.record_id

        if record_id.startswith("R") and record_id[1:].isdigit():
            numbers.append(int(record_id[1:]))

    next_number = max(numbers, default=0) + 1

    while any(
        record.record_id == f"R{next_number:03d}"
        for record in records
    ):
        next_number += 1

    return f"R{next_number:03d}"


def choose_building():
    """Ask the user to select a campus building."""

    print("\nAVAILABLE CAMPUS BUILDINGS")

    for key, details in BUILDINGS.items():
        print(f"{key}. {details[1]}")

    choice = input("Select building (1-6): ").strip()

    if choice not in BUILDINGS:
        raise ValueError("Invalid building selection.")

    return BUILDINGS[choice]


# --------------------------------------------------
# DATA ANALYSIS
# --------------------------------------------------

def display_dataset_summary():
    records, valid_records, issues = load_project_data()

    total = calculate_total_consumption(valid_records)

    print("\n========== DATASET SUMMARY ==========")
    print("Total records       :", len(records))
    print("Valid records       :", len(valid_records))
    print("Invalid records     :", len(issues))
    print("Total consumption   :", total, "kWh")


def display_building_analysis():
    _, valid_records, _ = load_project_data()

    summary = calculate_building_consumption(valid_records)

    print("\n========== BUILDING CONSUMPTION ==========")

    for building, details in summary.items():
        print("\nBuilding:", building)
        print("Total consumption :", details["total_kwh"], "kWh")
        print("Average reading   :", details["average_kwh"], "kWh")
        print("Maximum reading   :", details["maximum_kwh"], "kWh")
        print("Minimum reading   :", details["minimum_kwh"], "kWh")


def display_abnormal_readings():
    _, valid_records, _ = load_project_data()

    abnormal = flag_abnormal_readings(valid_records)

    print("\n========== ABNORMAL READING ANALYSIS ==========")

    if not abnormal:
        print("No potentially abnormal readings detected.")
        return

    for item in abnormal:
        print("\nRecord ID:", item["record_id"])
        print("Building:", item["building_name"])
        print("Reading date:", item["reading_date"])
        print("Consumption:", item["consumption_kwh"], "kWh")
        print("Previous average:", item["previous_average"], "kWh")
        print("Reason:", item["reason"])

    print("\nTotal potentially abnormal readings:", len(abnormal))
    print("Note: Unusual readings require investigation.")
    print("They are not automatically confirmed faults.")


def display_monthly_analysis():
    _, valid_records, _ = load_project_data()

    monthly_summary = create_monthly_summary(valid_records)

    print("\n========== MONTHLY ENERGY SUMMARY ==========")

    if monthly_summary.empty:
        print("No monthly data available.")
    else:
        print(monthly_summary.to_string(index=False))


def display_moving_averages():
    _, valid_records, _ = load_project_data()

    averages = calculate_moving_averages(
        valid_records,
        window=3
    )

    print("\n========== MOVING AVERAGE ANALYSIS ==========")

    for item in averages:
        print(
            item["building_name"],
            "|",
            item["reading_date"],
            "| Average:",
            item["moving_average_kwh"],
            "kWh"
        )

    print("\nTotal moving average observations:", len(averages))


# --------------------------------------------------
# RECORD MANAGEMENT
# --------------------------------------------------

def add_new_meter_record():
    """Collect, validate and save a new meter record."""

    records = load_records()

    record_id = generate_record_id(records)

    print("\n========== ADD NEW METER RECORD ==========")
    print("Generated Record ID:", record_id)

    building_id, building_name, meter_id = choose_building()

    reading_date = input(
        "Enter reading date (YYYY-MM-DD): "
    ).strip()

    consumption = input(
        "Enter electricity consumption (kWh): "
    ).strip()

    record = MeterRecord(
        record_id,
        building_id,
        building_name,
        meter_id,
        reading_date,
        consumption
    )

    add_record(record)

    print("\nNew meter record added successfully!")
    print_record(record)


def search_meter_record():
    """Search records using record ID or building name."""

    print("\n========== SEARCH METER RECORD ==========")

    search_value = input(
        "Enter Record ID or Building Name: "
    ).strip()

    results = search_records(search_value)

    if not results:
        print("\nNo matching records found.")
        return

    print("\nMatching records:", len(results))

    for record in results:
        print_record(record)


def update_meter_record():
    """Update selected fields of an existing record."""

    print("\n========== UPDATE METER RECORD ==========")

    record_id = input("Enter Record ID to update: ").strip()

    matches = search_records(record_id)

    record = next(
        (item for item in matches
         if item.record_id.casefold() == record_id.casefold()),
        None
    )

    if record is None:
        print("\nRecord not found.")
        return

    print_record(record)

    print("\nSELECT FIELD TO UPDATE")
    print("1. Building")
    print("2. Reading Date")
    print("3. Consumption")
    print("4. Cancel")

    choice = input("Enter choice (1-4): ").strip()

    if choice == "1":
        building_id, building_name, meter_id = choose_building()

        updates = {
            "building_id": building_id,
            "building_name": building_name,
            "meter_id": meter_id
        }

    elif choice == "2":
        new_date = input(
            "Enter new date (YYYY-MM-DD): "
        ).strip()

        updates = {"reading_date": new_date}

    elif choice == "3":
        new_consumption = input(
            "Enter new consumption (kWh): "
        ).strip()

        updates = {"consumption_kwh": new_consumption}

    elif choice == "4":
        print("Update cancelled.")
        return

    else:
        print("Invalid selection.")
        return

    updated_record = update_record(record_id, updates)

    if updated_record:
        print("\nRecord updated successfully!")
        print_record(updated_record)
    else:
        print("\nRecord not found.")


def delete_meter_record():
    """Delete a record after user confirmation."""

    print("\n========== DELETE METER RECORD ==========")

    record_id = input("Enter Record ID to delete: ").strip()

    matches = search_records(record_id)

    record = next(
        (item for item in matches
         if item.record_id.casefold() == record_id.casefold()),
        None
    )

    if record is None:
        print("\nRecord not found.")
        return

    print_record(record)

    confirmation = input(
        "\nAre you sure you want to delete this record? (yes/no): "
    ).strip().casefold()

    if confirmation == "yes":
        deleted_record = delete_record(record_id)

        if deleted_record:
            print("\nRecord deleted successfully.")
        else:
            print("\nRecord could not be deleted.")

    else:
        print("\nDeletion cancelled.")


# --------------------------------------------------
# REPORTS AND VISUALIZATION
# --------------------------------------------------

def generate_graphs():
    _, valid_records, _ = load_project_data()

    building_summary = calculate_building_consumption(valid_records)
    monthly_summary = create_monthly_summary(valid_records)

    monthly_graph = plot_monthly_energy_trends(monthly_summary)
    building_graph = plot_building_consumption(building_summary)

    print("\n========== GRAPH GENERATION ==========")
    print("Monthly graph:", monthly_graph)
    print("Building graph:", building_graph)
    print("\nBoth graphs generated successfully.")


def generate_json_report():
    _, valid_records, _ = load_project_data()

    building_summary = calculate_building_consumption(valid_records)
    monthly_summary = create_monthly_summary(valid_records)

    export_json_report(
        valid_records,
        building_summary,
        monthly_summary,
        "reports/energy_analysis_report.json"
    )

    print("\nJSON report generated successfully.")
    print("Location: reports/energy_analysis_report.json")


def run_complete_analysis():
    """Run all analysis and reporting operations."""

    display_dataset_summary()
    display_building_analysis()
    display_abnormal_readings()
    display_monthly_analysis()
    display_moving_averages()
    generate_graphs()
    generate_json_report()

    print("\nComplete analysis finished successfully!")


# --------------------------------------------------
# MAIN MENU
# --------------------------------------------------

def display_menu():
    print("\n" + "=" * 58)
    print("              CAMPUS ENERGY-USE ANALYSER")
    print("       Electricity Monitoring & Analytics System")
    print("=" * 58)

    print("\n                    [ MAIN MENU ]")

    print("\n" + "-" * 58)
    print("                    DATA ANALYSIS")
    print("-" * 58)
    print("  1. View Dataset Summary")
    print("  2. View Building Consumption")
    print("  3. View Abnormal Readings")
    print("  4. View Monthly Energy Summary")

    print("\n" + "-" * 58)
    print("                   RECORD MANAGEMENT")
    print("-" * 58)
    print("  5. Add New Meter Record")
    print("  6. Search Meter Record")
    print("  7. Update Meter Record")
    print("  8. Delete Meter Record")

    print("\n" + "-" * 58)
    print("               REPORTS & VISUALIZATION")
    print("-" * 58)
    print("  9. Generate Electricity Usage Graphs")
    print(" 10. Export JSON Report")
    print(" 11. Run Complete Analysis")

    print("\n" + "-" * 58)
    print(" 12. Exit")
    print("=" * 58)


def main():
    """Start the Campus Energy-Use Analyser application."""

    print("\nLoading Campus Energy-Use Analyser...")

    try:
        records, valid_records, issues = load_project_data()

        print("Dataset loaded successfully.")
        print("Total records:", len(records))
        print("Valid records:", len(valid_records))
        print("Invalid records:", len(issues))

    except (FileNotFoundError, PermissionError, ValueError, OSError) as error:
        print("\nUnable to load project dataset:", error)
        return

    while True:
        display_menu()

        choice = input("\nEnter your choice (1-12): ").strip()

        operations = {
            "1": display_dataset_summary,
            "2": display_building_analysis,
            "3": display_abnormal_readings,
            "4": display_monthly_analysis,
            "5": add_new_meter_record,
            "6": search_meter_record,
            "7": update_meter_record,
            "8": delete_meter_record,
            "9": generate_graphs,
            "10": generate_json_report,
            "11": run_complete_analysis
        }

        if choice == "12":
            print("\nThank you for using Campus Energy-Use Analyser.")
            print("Application closed successfully.")
            break

        elif choice in operations:
            try:
                operations[choice]()

            except (ValueError, TypeError, KeyError, OSError) as error:
                print("\nOperation could not be completed:", error)

        else:
            print("\nInvalid choice. Please enter a number from 1 to 12.")


if __name__ == "__main__":
    main()
