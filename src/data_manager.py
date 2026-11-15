
import csv
import math

from datetime import datetime
from pathlib import Path

from src.models import MeterRecord


# Project dataset location
DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "campus_energy_records.csv"
)

# CSV column names
CSV_FIELDS = [
    "record_id",
    "building_id",
    "building_name",
    "meter_id",
    "reading_date",
    "consumption_kwh"
]


def check_record(record):
    """Check the basic validity of a meter record."""

    required_fields = {
        "record_id": record.record_id,
        "building_id": record.building_id,
        "building_name": record.building_name,
        "meter_id": record.meter_id,
        "reading_date": record.reading_date
    }

    for field, value in required_fields.items():
        if not value or not str(value).strip():
            raise ValueError(f"{field} cannot be empty.")

    try:
        datetime.strptime(record.reading_date, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValueError("Date must use YYYY-MM-DD format.")

    try:
        consumption = float(record.consumption_kwh)
    except (ValueError, TypeError):
        raise ValueError("Consumption must be numeric.")

    if not math.isfinite(consumption):
        raise ValueError("Consumption must be a finite number.")

    if consumption < 0:
        raise ValueError("Consumption cannot be negative.")


def load_records(file_path=DATA_FILE):
    """Load CSV records into a list of MeterRecord objects."""

    records = []

    try:
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError("CSV file is empty or has no header.")

            missing_fields = [
                field for field in CSV_FIELDS
                if field not in reader.fieldnames
            ]

            if missing_fields:
                raise ValueError(f"Missing CSV columns: {missing_fields}")

            for row_number, row in enumerate(reader, start=2):
                try:
                    record = MeterRecord(
                        record_id=row["record_id"],
                        building_id=row["building_id"],
                        building_name=row["building_name"],
                        meter_id=row["meter_id"],
                        reading_date=row["reading_date"],
                        consumption_kwh=row["consumption_kwh"]
                    )

                    records.append(record)

                except (ValueError, TypeError, KeyError) as error:
                    raise ValueError(
                        f"Invalid data at CSV row {row_number}: {error}"
                    ) from error

    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset not found: {file_path}") from None

    except PermissionError:
        raise PermissionError(
            f"Permission denied while reading: {file_path}"
        ) from None

    except csv.Error as error:
        raise ValueError(f"CSV reading error: {error}") from error

    return records


def save_records(records, file_path=DATA_FILE):
    """Save MeterRecord objects into a CSV file."""

    file_path = Path(file_path)

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)

            writer.writeheader()

            for record in records:
                writer.writerow(record.to_dict())

        return True

    except PermissionError:
        raise PermissionError(
            f"Permission denied while saving: {file_path}"
        ) from None

    except OSError as error:
        raise OSError(f"Unable to save CSV file: {error}") from error


def add_record(record, file_path=DATA_FILE):
    """Add a new meter record if its ID is unique and data is valid."""

    check_record(record)

    records = load_records(file_path)

    for existing in records:
        if existing.record_id.strip().casefold() == record.record_id.strip().casefold():
            raise ValueError("This record ID already exists.")

    records.append(record)
    save_records(records, file_path)

    return True


def search_records(search_value, file_path=DATA_FILE):
    """Search records by record ID or building name."""

    if not search_value or not search_value.strip():
        raise ValueError("Search value cannot be empty.")

    records = load_records(file_path)
    search_value = search_value.strip().casefold()

    results = []

    for record in records:
        if (
            search_value in record.record_id.casefold()
            or search_value in record.building_name.casefold()
        ):
            results.append(record)

    return results


def update_record(record_id, updates, file_path=DATA_FILE):
    """Update an existing record using its record ID."""

    records = load_records(file_path)

    allowed_fields = {
        "building_id",
        "building_name",
        "meter_id",
        "reading_date",
        "consumption_kwh"
    }

    if not updates:
        raise ValueError("No updates were provided.")

    for field in updates:
        if field not in allowed_fields:
            raise ValueError(f"Field cannot be updated: {field}")

    for index, record in enumerate(records):

        if record.record_id.casefold() == record_id.strip().casefold():

            updated_values = record.to_dict()

            updated_values.update(updates)

            updated_record = MeterRecord(**updated_values)

            check_record(updated_record)

            records[index] = updated_record

            save_records(records, file_path)

            return updated_record

    return None


def delete_record(record_id, file_path=DATA_FILE):
    """Delete an existing record using its record ID."""

    records = load_records(file_path)

    for index, record in enumerate(records):

        if record.record_id.casefold() == record_id.strip().casefold():

            deleted_record = records.pop(index)

            save_records(records, file_path)

            return deleted_record

    return None
