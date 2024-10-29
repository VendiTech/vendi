from datetime import datetime


def is_time_provided(dt: datetime) -> bool:
    """
    Checks if a specific time was provided in a datetime object.

    :param dt: The datetime object to check.
    :return: True if a time other than 00:00:00 was provided, False otherwise.
    """
    return not (dt.hour == 0 and dt.minute == 0 and dt.second == 0)


def set_end_of_day_time(dt: datetime) -> datetime:
    """
    Sets the time of a datetime object to the end of the day (23:59:59) if no specific time was provided.

    :param dt: The datetime object to modify.
    :return: The modified datetime object with the time set to 23:59:59 if no specific time was provided.
    """
    if not is_time_provided(dt):
        return dt.replace(hour=23, minute=59, second=59)

    return dt
