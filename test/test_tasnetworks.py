from datetime import datetime
from zoneinfo import ZoneInfo

from aemo_to_tariff.tasnetworks import convert


def test_convert_tasnetworks():
    # Add test cases for the convert() function
    pass


def test_tas93_2026_27_peak():
    # Post-1-Jul-2026 TAS93 peak: 17.229 → 19.860 c/kWh
    interval_time = datetime(2026, 7, 15, 18, 0, tzinfo=ZoneInfo('Australia/Hobart'))
    price = convert(interval_time, 'TAS93', 100.0)
    assert abs(price - (10.0 + 19.860)) < 0.01, f"got {price}"
