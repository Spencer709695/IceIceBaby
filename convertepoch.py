import datetime

def convert(epoch_time):
    """
    Converts an epoch timestamp to a human-readable date format (YYYY-MM-DD).
    
    :param epoch_time: The epoch timestamp (Unix time in seconds)
    :return: Formatted date string (YYYY-MM-DD)
    """
    return datetime.datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d')
