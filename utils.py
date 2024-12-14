from datetime import datetime, timedelta

def gen_date_range(initial_date):
    """
    Returns a tuple of start and end timestamps 30 days apart.
    Adjusts the end timestamp if it exceeds the current time.
    """
    start_date = datetime.fromtimestamp(initial_date)
    
    end_date = start_date + timedelta(days=29)
    
    start_timestamp = initial_date
    end_timestamp = int(end_date.timestamp())
    
    done = False
    now_timestamp = int(datetime.now().timestamp())
    if end_timestamp > now_timestamp:
        done = True
        end_timestamp = now_timestamp
    
    return (start_timestamp, end_timestamp, done)