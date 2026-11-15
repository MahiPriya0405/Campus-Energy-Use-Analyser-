
import unittest
import tempfile

from pathlib import Path

from src.models import MeterRecord
from src.data_manager import (
    load_records,
    save_records,
    add_record,
    search_records,
    update_record,
    delete_record
)


class TestRecordManagement(unittest.TestCase):

    def setUp(self):
        """Prepare an isolated temporary CSV dataset."""

        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.file_path = Path(self.temp_dir.name) / "test_records.csv"

        self.records = [
            MeterRecord(
                "R001", "B001", "Academic Block A",
                "MTR001", "2026-08-01", 100
            ),
            MeterRecord(
                "R002", "B002", "Central Library",
                "MTR002", "2026-08-07", 150
            )
        ]

        save_records(self.records, self.file_path)

    def test_add_record(self):
        """Check that a new record is added successfully."""

        new_record = MeterRecord(
            "R003", "B001", "Academic Block A",
            "MTR001", "2026-08-13", 200
        )

        result = add_record(new_record, self.file_path)
        records = load_records(self.file_path)

        self.assertTrue(result)
        self.assertEqual(len(records), 3)

    def test_duplicate_record_rejected(self):
        """Check that duplicate record IDs are rejected."""

        duplicate = MeterRecord(
            "R001", "B001", "Academic Block A",
            "MTR001", "2026-08-13", 200
        )

        with self.assertRaises(ValueError):
            add_record(duplicate, self.file_path)

        self.assertEqual(len(load_records(self.file_path)), 2)

    def test_negative_record_rejected(self):
        """Check that negative consumption cannot be added."""

        invalid_record = MeterRecord(
            "R003", "B001", "Academic Block A",
            "MTR001", "2026-08-13", -50
        )

        with self.assertRaises(ValueError):
            add_record(invalid_record, self.file_path)

        self.assertEqual(len(load_records(self.file_path)), 2)

    def test_search_by_record_id(self):
        """Check searching using a record ID."""

        results = search_records("R001", self.file_path)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].record_id, "R001")

    def test_search_by_building_name(self):
        """Check searching using a building name."""

        results = search_records("Library", self.file_path)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].building_name, "Central Library")

    def test_update_record(self):
        """Check updating an existing electricity reading."""

        updated = update_record(
            "R001",
            {"consumption_kwh": 250},
            self.file_path
        )

        records = load_records(self.file_path)

        self.assertIsNotNone(updated)
        self.assertEqual(records[0].consumption_kwh, 250.0)

    def test_update_invalid_consumption(self):
        """Check that an invalid update is rejected."""

        with self.assertRaises(ValueError):
            update_record(
                "R001",
                {"consumption_kwh": -100},
                self.file_path
            )

        records = load_records(self.file_path)

        self.assertEqual(records[0].consumption_kwh, 100.0)

    def test_delete_record(self):
        """Check deleting an existing record."""

        deleted = delete_record("R001", self.file_path)

        records = load_records(self.file_path)

        self.assertIsNotNone(deleted)
        self.assertEqual(deleted.record_id, "R001")
        self.assertEqual(len(records), 1)

    def test_delete_nonexistent_record(self):
        """Check that a nonexistent record is not deleted."""

        deleted = delete_record("R999", self.file_path)

        self.assertIsNone(deleted)
        self.assertEqual(len(load_records(self.file_path)), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
