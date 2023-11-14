from src.page_ranking.page_rank import run_background_service, get_iteration_count
from multiprocessing import Process, Event
from threading import Thread
from src.database.database import Database
import os
import signal
import time
import pymysql

handle = None

class PageRankingService:
    def is_busy():
        return handle is not None

    def get_metrics():
        connection = Database().connect()

        cursor = connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(
            "select sum(size_bytes) as size_bytes from page_information pi2")
        size = cursor.fetchall()[0].get('size_bytes')
        cursor.execute("select count(*) as total from page_information pi2")
        total_nodes = cursor.fetchall()[0].get('total')
        cursor.execute("select count(*) as total from page_linking pl")
        total_linking = cursor.fetchall()[0].get('total')
        connection.close()
        return {
            "size": int(size),
            "total_nodes": total_nodes,
            "total_linking": total_linking
        }

    def stop(pid: str = None):
        global handle
        if PageRankingService.is_busy():
            os.kill(pid or handle.get('pid'), signal.SIGTERM)
            PageRankingService.cleanup()
        else:
            raise Exception('no process are running rn')

    def status():
        if PageRankingService.is_busy():
            return {'pid': handle.get('pid'), 'status': 'RUNNING' if handle is not None else 'IDLE', 'max_iterations': handle.get('max_iterations'), 'start_time': handle.get('start_time'), 'iteration': get_iteration_count() + 1}
        return {'status': 'IDLE'}
    
    def task(event: Event, options: dict):
        run_background_service(options)
        event.set()

    def checker(event: Event):
        event.wait()
        PageRankingService.cleanup()

    def cleanup():
        global handle
        handle = None

    def run(options):
        max_iterations = options.get('max_iterations')
        threads = 0
        damping_factor = options.get('damping_factor')

        event = Event()

        new_process = Process(target=PageRankingService.task, args=(event, {
            'max_iterations': max_iterations,
            'damping_factor': damping_factor
        },))
        process_checker = Thread(
            target=PageRankingService.checker, args=(event,))

        new_process.start()
        
        global handle

        handle = {
            'pid': new_process.pid,
            # time in seconds since the epoch
            'start_time': time.time(),
            'max_iterations': max_iterations
        }

        process_checker.start()

        return True
