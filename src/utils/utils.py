from time import perf_counter
from multiprocessing import cpu_count

def log_execution_time(func=None, args=dict(), fn_name= None):
    if (func is not None):
        t1 = perf_counter()
        result = func(*args)
        t2 = perf_counter()
        print(f"{fn_name or func.__name__} with args {str(args)} took {t2-t1} seconds!")
        return result
    return None

def get_available_threads():
    return cpu_count()
