from datetime import datetime, timedelta
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


# TAS94 (small business TOU): Peak weekdays 07:00-10:00 & 16:00-21:00,
# Shoulder weekends 07:00-22:00, Off-peak all other times. 2026-27 network
# rates: Peak 19.766, Shoulder 11.643, Off-peak 2.670 c/kWh. rrp=0 isolates
# the network rate. 2026-07-09 is a Thursday (weekday); 2026-07-11 a Saturday.
def _tas94(y, mo, d, h, mi):
    # +5 min so the -5 min offset inside convert() lands on the intended minute.
    t = datetime(y, mo, d, h, mi, tzinfo=ZoneInfo('Australia/Hobart')) + timedelta(minutes=5)
    return convert(t, 'TAS94', 0.0)


def test_tas94_weekday_peak_morning():
    assert abs(_tas94(2026, 7, 9, 8, 30) - 19.766) < 1e-6


def test_tas94_weekday_peak_evening():
    assert abs(_tas94(2026, 7, 9, 18, 30) - 19.766) < 1e-6


def test_tas94_weekday_midday_is_offpeak():
    # 14:30 sits between the two weekday peaks -> Off-peak, not Peak.
    assert abs(_tas94(2026, 7, 9, 14, 30) - 2.670) < 1e-6


def test_tas94_weekday_overnight_is_offpeak():
    # 04:30 on a weekday -> Off-peak, not Shoulder.
    assert abs(_tas94(2026, 7, 9, 4, 30) - 2.670) < 1e-6


def test_tas94_weekend_daytime_is_shoulder():
    # Saturday 14:30 -> Shoulder (weekend 07:00-22:00), never Peak.
    assert abs(_tas94(2026, 7, 11, 14, 30) - 11.643) < 1e-6


def test_tas94_weekend_overnight_is_offpeak():
    # Saturday 04:30 -> Off-peak (before the weekend shoulder window).
    assert abs(_tas94(2026, 7, 11, 4, 30) - 2.670) < 1e-6
