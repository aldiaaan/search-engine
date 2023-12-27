from time import perf_counter
from multiprocessing import cpu_count
import os
import sys
import gc
from datetime import datetime
import time

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

last_time_called = None

def get_memsize():
    global last_time_called
    if last_time_called is not None:
        if (datetime.now() - last_time_called ).seconds < 5:
            return
    last_time_called = datetime.now()
    print(last_time_called)
    print(datetime.now())
    print((datetime.now() - last_time_called).seconds)
    print('----------')
    # print((last_time_called - datetime.now()).seconds)

    path = os.path.abspath('../../memdump.csv')
    file = open(path, 'a')
    # xs = []
    total_size = 0
    for obj in gc.get_objects():
        i = id(obj)
        size = sys.getsizeof(obj, 0)
        #    referrers = [id(o) for o in gc.get_referrers(obj) if hasattr(o, '__class__')]
        referents = [id(o) for o in gc.get_referents(obj) if hasattr(o, '__class__')]
        if hasattr(obj, '__class__'):
            cls = str(obj.__class__)
            total_size += size
            # xs.append({'id': i, 'class': cls, 'size': size, 'referents': referents})            
    file.write(f"{datetime.now()},{total_size}\n")   
    # cPickle.dump(xs, dump)