import pytest
from datetime import datetime, timezone, timedelta
from app.core.sla import add_business_minutes

def test_add_business_minutes_same_day():
    # Tuesday, 10 AM
    start = datetime(2023, 10, 10, 10, 0, tzinfo=timezone.utc)
    result = add_business_minutes(start, 60)
    # Should be Tuesday, 11 AM
    assert result == datetime(2023, 10, 10, 11, 0, tzinfo=timezone.utc)

def test_add_business_minutes_next_day():
    # Tuesday, 4:30 PM
    start = datetime(2023, 10, 10, 16, 30, tzinfo=timezone.utc)
    # Add 60 minutes. 30 mins left today, 30 mins tomorrow
    result = add_business_minutes(start, 60)
    # Should be Wednesday, 9:30 AM
    assert result == datetime(2023, 10, 11, 9, 30, tzinfo=timezone.utc)

def test_add_business_minutes_over_weekend():
    # Friday, 4 PM
    start = datetime(2023, 10, 13, 16, 0, tzinfo=timezone.utc)
    # Add 120 minutes (2 hours). 1 hour left today, 1 hour on Monday
    result = add_business_minutes(start, 120)
    # Should be Monday, 10:00 AM
    assert result == datetime(2023, 10, 16, 10, 0, tzinfo=timezone.utc)

def test_add_business_minutes_start_on_weekend():
    # Saturday, 12 PM (noon)
    start = datetime(2023, 10, 14, 12, 0, tzinfo=timezone.utc)
    # Add 60 minutes.
    result = add_business_minutes(start, 60)
    # Should be Monday, 10:00 AM
    assert result == datetime(2023, 10, 16, 10, 0, tzinfo=timezone.utc)

def test_add_business_minutes_start_after_hours():
    # Tuesday, 6 PM
    start = datetime(2023, 10, 10, 18, 0, tzinfo=timezone.utc)
    result = add_business_minutes(start, 30)
    # Should be Wednesday, 9:30 AM
    assert result == datetime(2023, 10, 11, 9, 30, tzinfo=timezone.utc)

def test_add_business_minutes_start_before_hours():
    # Tuesday, 7 AM
    start = datetime(2023, 10, 10, 7, 0, tzinfo=timezone.utc)
    result = add_business_minutes(start, 30)
    # Should be Tuesday, 9:30 AM
    assert result == datetime(2023, 10, 10, 9, 30, tzinfo=timezone.utc)

def test_add_business_minutes_multiple_days():
    # Monday 10 AM
    start = datetime(2023, 10, 9, 10, 0, tzinfo=timezone.utc)
    # Add 24 hours (1440 minutes). Each business day is 8 hours (480 mins).
    # 1440 / 480 = 3 full days. So it should land on Thursday 10 AM.
    result = add_business_minutes(start, 1440)
    assert result == datetime(2023, 10, 12, 10, 0, tzinfo=timezone.utc)
