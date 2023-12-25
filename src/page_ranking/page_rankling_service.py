from src.page_ranking.page_rank import run_background_service, get_iteration_count
from multiprocessing import Process, Event
from threading import Thread
from src.database.database import Database
from flask import current_app
import os
import signal
import time
import pymysql
from celery.contrib.abortable import AbortableAsyncResult

handle = None


def get_crawling_task():
    tasks = [x for x in current_app.extensions["celery"].control.inspect().active(
    ).get('celery@SEARCH_ENGINE_WORKERS') if x.get('name') == 'workers.page_ranking.run']
    print(tasks)
    if len(tasks) == 0:
        return None
    task = AbortableAsyncResult(tasks[0].get('id'))
    return task

class PageRankingService:
    def is_busy():
        if get_crawling_task() is None:
            return False
        return True

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
            t = get_crawling_task()
            t.abort()
            # os.kill(pid or handle.get('pid'), signal.SIGTERM)
            # PageRankingService.cleanup()
        else:
            raise Exception('no process are running rn')

    def status():
        t = get_crawling_task()
        if PageRankingService.is_busy():
            return {'status': 'RUNNING', 'max_iterations': t.info.get('max_iterations'), 'start_time': t.info.get('start_time'), 'iteration': t.info.get('iterations')}
        return {'status': 'IDLE'}
    
    def task(event: Event, options: dict):
        
        run_background_service(options)
        event.set()

    def checker(event: Event):
        
        print('waiting...')
        event.wait()
        PageRankingService.cleanup()

    def cleanup():
        global handle
        handle = None

    def run(options):
        
        max_iterations = options.get('max_iterations')
        threads = 0
        damping_factor = options.get('damping_factor')
        from src.celery.workers import run_page_ranking
        run_page_ranking.delay(max_iterations=max_iterations, damping_factor=damping_factor)
        return True

    def run2(options):
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
