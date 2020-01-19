import datetime
import time

LONG_TIME_AGO = -99999999999


def get_epoch_from_date(date):
    # Handle multi-tagged dates
    if isinstance(date, list):
        date = date[0]

    if type(date) == int:
        return date

    if date.isnumeric():
        year = int(date)
        if year < 1 or year > 9999:
            year = 1
        epoch = datetime.datetime(year, 1, 1)
    else:
        split_char: str
        if '-' in date:
            split_char = '-'
        elif '.' in date:
            split_char = '.'

        date_list = date.split(split_char)

        while len(date_list) < 3:
            date_list.append(1)

        # Very basic date validation and correction
        year = int(date_list[0])
        month = int(date_list[1])
        day = int(date_list[2])
        if year < 1 or year > 9999:
            year = 1
        if month < 1 or month > 12:
            month = 1
        if day < 1 or day > 31:
            day = 1

        try:
            epoch = datetime.datetime(year, month, day)
        except ValueError:
            return LONG_TIME_AGO

    return int(epoch.replace(tzinfo=datetime.timezone.utc).timestamp())


def get_epoch_as_year(epoch: int):
    if epoch == LONG_TIME_AGO:  # If album is missing year
        return 0
    return time.strftime('%Y', time.localtime(epoch))
