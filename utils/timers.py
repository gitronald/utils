""" timers : A useful collection of time related functions
"""

import datetime
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

def get_time_range(col):
    start = col.min().strftime('%B %d, %Y')
    end = col.max().strftime('%B %d, %Y')
    window = (col.max() - col.min()).days
    return start, end, window