from datetime import datetime, timedelta

# Simple business hours config: Mon-Fri, 9am to 5pm (17:00)
BUSINESS_START_HOUR = 9
BUSINESS_END_HOUR = 17
BUSINESS_DAYS = [0, 1, 2, 3, 4]  # Monday to Friday

def add_business_minutes(start_time: datetime, minutes: int) -> datetime:
    """
    Adds business minutes to a given start_time, skipping weekends and off-hours.
    Assumes start_time is timezone-aware.
    """
    current_time = start_time
    minutes_remaining = minutes

    while minutes_remaining > 0:
        # If current_time is outside business hours, advance it to the next business start time
        if current_time.weekday() not in BUSINESS_DAYS or current_time.hour >= BUSINESS_END_HOUR:
            # Move to the next day's start time
            days_to_add = 1
            while (current_time + timedelta(days=days_to_add)).weekday() not in BUSINESS_DAYS:
                days_to_add += 1
            
            current_time = current_time.replace(hour=BUSINESS_START_HOUR, minute=0, second=0, microsecond=0) + timedelta(days=days_to_add)
            continue
        elif current_time.hour < BUSINESS_START_HOUR:
            # Move to today's start time
            current_time = current_time.replace(hour=BUSINESS_START_HOUR, minute=0, second=0, microsecond=0)
            continue

        # Calculate time remaining in the current business day
        end_of_day = current_time.replace(hour=BUSINESS_END_HOUR, minute=0, second=0, microsecond=0)
        minutes_to_end_of_day = int((end_of_day - current_time).total_seconds() / 60)

        if minutes_remaining <= minutes_to_end_of_day:
            # We can finish within the current business day
            current_time += timedelta(minutes=minutes_remaining)
            minutes_remaining = 0
        else:
            # Consume the rest of the day and advance
            minutes_remaining -= minutes_to_end_of_day
            current_time = end_of_day # The next loop iteration will advance it to the next morning

    return current_time
