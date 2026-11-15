
import unittest
import tempfile
import json

from pathlib import Path

from src.models import MeterRecord
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


class TestCampusEnergyAnalyser(unittest.TestCase):

    def setUp(self):
        """Create sample meter records for testing."""

        self.records = [
            MeterRecord("R001", "B001", "Academic Block A",
                        "MTR001", "2026-08-01", 100),

            MeterRecord("R002", "B001", "Academic Block A",
                        "MTR001", "2026-08-07", 120),

            MeterRecord("R003", "B001", "Academic Block A",
                        "MTR001", "2026-08-13", 110),

            MeterRecord("R004", "B001", "Academic Block A",
                        "MTR001", "2026-08-19", 300)
        ]

    def test_valid_records(self):
        """Check that valid records pass validation."""

        valid, issues = validate_records(self.records)

        self.assertEqual(len(valid), 4)
        self.assertEqual(len(issues), 0)

    def test_negative_reading(self):
        """Check that negative consumption is rejected."""

        record = MeterRecord(
            "R005", "B001", "Academic Block A",
            "MTR001", "2026-08-25", -50
        )

        valid, issues = validate_records([record])

        self.assertEqual(len(valid), 0)
        self.assertEqual(len(issues), 1)

        self.assertIn(
            "Negative electricity reading",
            issues[0]["errors"]
        )

    def test_duplicate_record_id(self):
        """Check detection of duplicate record IDs."""

        duplicate = MeterRecord(
            "R001", "B001", "Academic Block A",
            "MTR001", "2026-08-25", 150
        )

        valid, issues = validate_records(
            self.records + [duplicate]
        )

        self.assertEqual(len(valid), 3)
        self.assertEqual(len(issues), 2)

    def test_invalid_date(self):
        """Check detection of invalid reading dates."""

        record = MeterRecord(
            "R006", "B001", "Academic Block A",
            "MTR001", "25-08-2026", 100
        )

        valid, issues = validate_records([record])

        self.assertEqual(len(valid), 0)

        self.assertIn(
            "Invalid reading date",
            issues[0]["errors"]
        )

    def test_missing_building_name(self):
        """Check detection of missing building names."""

        record = MeterRecord(
            "R007", "B001", "",
            "MTR001", "2026-08-25", 100
        )

        valid, issues = validate_records([record])

        self.assertEqual(len(valid), 0)

        self.assertIn(
            "Missing building_name",
            issues[0]["errors"]
        )

    def test_total_consumption(self):
        """Check NumPy total calculation."""

        total = calculate_total_consumption(self.records)

        self.assertEqual(total, 630.0)

    def test_building_consumption(self):
        """Check building-wise consumption calculation."""

        summary = calculate_building_consumption(self.records)

        self.assertEqual(
            summary["Academic Block A"]["total_kwh"],
            630.0
        )

    def test_moving_average(self):
        """Check three-observation moving average."""

        averages = calculate_moving_averages(
            self.records, window=3
        )

        self.assertEqual(len(averages), 2)

        self.assertEqual(
            averages[0]["moving_average_kwh"],
            110.0
        )

    def test_abnormal_reading(self):
        """Check detection of an unusual reading."""

        abnormal = flag_abnormal_readings(self.records)

        self.assertEqual(len(abnormal), 1)
        self.assertEqual(abnormal[0]["record_id"], "R004")

    def test_monthly_summary(self):
        """Check Pandas monthly summary."""

        summary = create_monthly_summary(self.records)

        self.assertEqual(len(summary), 1)
        self.assertEqual(
            summary.iloc[0]["record_count"],
            4
        )
        self.assertEqual(
            summary.iloc[0]["total_kwh"],
            630.0
        )

    def test_json_export(self):
        """Check JSON report generation."""

        building_summary = calculate_building_consumption(
            self.records
        )

        monthly_summary = create_monthly_summary(
            self.records
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            output_file = Path(temp_dir) / "test_report.json"

            export_json_report(
                self.records,
                building_summary,
                monthly_summary,
                output_file
            )

            self.assertTrue(output_file.exists())

            with open(output_file, "r", encoding="utf-8") as file:
                report = json.load(file)

            self.assertEqual(report["total_records"], 4)
            self.assertEqual(
                report["total_consumption_kwh"],
                630.0
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
