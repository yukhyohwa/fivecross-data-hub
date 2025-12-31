from datetime import datetime

def validate_date_format(date_text):
    try:
        datetime.strptime(date_text, '%Y%m%d')
        return True
    except ValueError:
        return False

def validate_datetime_format(date_text):
    try:
        datetime.strptime(date_text, "%H:%M:%S")
        return True
    except ValueError:
        return False

def calculate_date_difference(start_date, end_date):
    if not start_date or not end_date:
        return 0
    start = datetime.strptime(start_date, '%Y%m%d')
    end = datetime.strptime(end_date, '%Y%m%d')
    return (end - start).days
