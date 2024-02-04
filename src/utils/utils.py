from time import perf_counter
from multiprocessing import cpu_count
import os
import sys
import gc
from datetime import datetime
import time
import tracemalloc
import gc
import linecache

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

class MemoryLogger:    
    every = 300
    last_time_called = None
    snapshots = []
    latest_snapshot = None
    
    def __init__(self, every = 300):
        self.every = 300
        pass

    def take_snapshot(self):
        if self.last_time_called is not None:
            if (datetime.now() - self.last_time_called ).seconds < self.every:
                return
        self.last_time_called = datetime.now()
        snapshot = tracemalloc.take_snapshot()        
        self._save_snapshot(snapshot)
        self.latest_snapshot = snapshot

    def _save_snapshot(self, snapshot):
        total_gc = 0
        for obj in gc.get_objects():
            size = sys.getsizeof(obj, 0)
            if hasattr(obj, '__class__'):
                cls = str(obj.__class__)
                total_gc += size
        now = int(time.time())

        report_path = os.path.abspath(f'./MemoryLogReport-{now}.txt')   
        limit = 50             
        file = open(report_path, 'a')
        file.write(f"[!] Memory Log Report ({now}) \n\n\n\n")
        file.write(f"[+] Top {limit} lines \n\n")
        top_stats = snapshot.statistics('traceback')
        for index, stat in enumerate(top_stats[:limit], 1):
            frame = stat.traceback[0]
            file.write("    #%s: %s:%s: %.1f KiB \n" % (index, frame.filename, frame.lineno, stat.size / 1024))
            for line in stat.traceback.format():
                file.write(f'       {line} \n')
            line = linecache.getline(frame.filename, frame.lineno).strip()
            if line:
                file.write('        %s \n' % line)
        other = top_stats[limit:]
        file.write("\n\n")
        if self.latest_snapshot is not None:
            file.write(f"[+] Differences from previous snapshots {limit} lines \n\n")
            differences = snapshot.compare_to(self.latest_snapshot, 'lineno')
            for index, stat in enumerate(differences[:limit]):
                file.write(f"    #{index}: {stat} \n")
        
        file.write("\n\n")

        file.write(f"[+] Summaries \n\n")
        if other:
            size = sum(stat.size for stat in other)
            file.write("Total size of others (%s): %.1f KiB (tracemalloc) \n" % (len(other), size / 1024))        
        total = sum(stat.size for stat in top_stats)
        file.write("Total allocated size: %.1f KiB (tracemalloc) \n" % (total / 1024))        
        file.write("Total allocated size: %.1f KiB (gc) \n" % (total_gc / 1024))     
        file.write(f"\n\n\n\n")   
        file.flush()
        file.close()

    def start():
        tracemalloc.start()
    def stop():
        tracemalloc.stop()


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