""" timers : A useful collection of time related functions
"""

import datetime
import pandas as pd
from timeit import default_timer

def isostamp():
    return datetime.datetime.utcnow().isoformat()

def now(fmt="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.now().strftime(fmt)

def start_timer():
    return default_timer()

def stop_timer(start, v=False):
    stop = default_timer()
    total_time = stop - start
    mins, secs = divmod(total_time, 60)
    hours, mins = divmod(mins, 60)
    runtime = f'{int(hours)}:{int(mins)}:{secs}'
    if v: print(f"Run time:\t{runtime}\n")
    return f'{runtime}'

def get_diff_days(start, end):
    """Get difference between datetimes in days with decimal

    Args:
        start (pd.Series): an array of datetime strings
        end (pd.Series): an array of datetime strings

    Returns:
        pd.Series: The difference as a float
    """
    tdelta = pd.to_datetime(end) - pd.to_datetime(start)
    total_days = tdelta.dt.round(freq='d').dt.days
    return total_days + tdelta.dt.seconds / 60 / 60 / 24

def get_time_range(col):
    start = col.min().strftime('%B %d, %Y')
    end = col.max().strftime('%B %d, %Y')
    window = (col.max() - col.min()).days
    return start, end, window

def seconds_to_clock(secs):
    """ Convert time in seconds to "HH:MM:SS" clock format
    
    Arguments:
        secs {float} -- Time in seconds
    
    Returns:
        str -- The clock formatted version of the seconds input
    """
    return f"{str(datetime.timedelta(seconds=secs))}"
