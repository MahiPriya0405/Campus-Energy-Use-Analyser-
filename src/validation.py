
from datetime import datetime
from collections import Counter


def validate_records(records):
    """
    Validate meter records and identify invalid data.
    Returns valid records and a list of validation issues.
    """

    valid_records = []
    issues = []

    record_ids = [
        record.record_id for record in records
    ]

    duplicate_ids = {
        record_id
        for record_id, count in Counter(record_ids).items()
        if count > 1
    }

    for record in records:

        errors = []

        # Check missing fields
        required_fields = {
            "record_id": record.record_id,
            "building_id": record.building_id,
            "building_name": record.building_name,
            "meter_id": record.meter_id,
            "reading_date": record.reading_date
        }

        for field, value in required_fields.items():
            if not value or not str(value).strip():
                errors.append(f"Missing {field}")

        # Check duplicate record IDs
        if record.record_id in duplicate_ids:
            errors.append("Duplicate record ID")

        # Check reading date format
        try:
            datetime.strptime(record.reading_date, "%Y-%m-%d")
        except (ValueError, TypeError):
            errors.append("Invalid reading date")

        # Check negative consumption
        if record.consumption_kwh < 0:
            errors.append("Negative electricity reading")

        # Store validation result
        if errors:
            issues.append({
                "record_id": record.record_id,
                "errors": errors
            })
        else:
            valid_records.append(record)

    return valid_records, issues


def flag_abnormal_readings(records):
    """
    Flag unusually high readings using the
    previous three observations for each building.

    A reading is flagged when it is greater than
    1.5 times the average of the previous three readings.
    """

    building_records = {}

    for record in records:
        building_records.setdefault(
            record.building_id, []
        ).append(record)

    abnormal_records = []

    for building_id, building_data in building_records.items():

        # Sort readings chronologically
        building_data.sort(
            key=lambda record: record.reading_date
        )

        previous_readings = []

        for record in building_data:

            # Compare only after three previous observations
            if len(previous_readings) >= 3:

                average = (
                    sum(previous_readings[-3:]) / 3
                )

                if record.consumption_kwh > average * 1.5:
                    abnormal_records.append({
                        "record_id": record.record_id,
                        "building_id": building_id,
                        "building_name": record.building_name,
                        "reading_date": record.reading_date,
                        "consumption_kwh": record.consumption_kwh,
                        "previous_average": round(average, 2),
                        "reason": "Consumption exceeds 1.5 times the previous three-reading average"
                    })

            previous_readings.append(
                record.consumption_kwh
            )

    return abnormal_records
