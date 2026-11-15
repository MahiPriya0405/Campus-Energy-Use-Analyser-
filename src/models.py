
class MeterRecord:
    """
    Represents one electricity meter reading
    for a campus building.
    """

    def __init__(
        self,
        record_id,
        building_id,
        building_name,
        meter_id,
        reading_date,
        consumption_kwh
    ):
        self.record_id = record_id
        self.building_id = building_id
        self.building_name = building_name
        self.meter_id = meter_id
        self.reading_date = reading_date
        self.consumption_kwh = float(consumption_kwh)

    def __str__(self):
        return (
            f"Record ID: {self.record_id} | "
            f"Building: {self.building_name} | "
            f"Date: {self.reading_date} | "
            f"Consumption: {self.consumption_kwh:.2f} kWh"
        )

    def to_dict(self):
        """Convert the meter record into a dictionary."""
        return {
            "record_id": self.record_id,
            "building_id": self.building_id,
            "building_name": self.building_name,
            "meter_id": self.meter_id,
            "reading_date": self.reading_date,
            "consumption_kwh": self.consumption_kwh
        }
