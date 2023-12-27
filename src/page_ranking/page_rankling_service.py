from src.page_ranking.page_rank import run_background_service, get_iteration_count
from multiprocessing import Process, Event
from threading import Thread
from src.database.database import Database
import os
import signal
import time
import pymysql
from flask import current_app
from celery.result import AsyncResult

class PageRankingService:
    def get_active_task():
        try:
            active_tasks = current_app.extensions["celery"].control.inspect().active().get('celery@SEARCH_ENGINE_WORKERS')
        except Exception as e:
            return None, {}


        tasks = [x for x in active_tasks if x.get('name') == 'workers.page_ranking.run']
        
        if len(tasks) == 0:
            return None, {}
        
        task = AsyncResult(tasks[0].get('id'))
        
        return task, task._get_task_meta().get('result') or {}
    
    def is_busy():
        task, info = PageRankingService.get_active_task()
        
        return task is not None

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
        task, info = PageRankingService.get_active_task()
        if task is not None:
            task.revoke(terminate=True, signal='SIGKILL')
        else:
            raise Exception('no process are running rn')

    def status():
        task, info = PageRankingService.get_active_task()
        i = info.get('iterations') or 0
        if task is not None:
            return {'status': 'RUNNING', 'max_iterations': info.get('max_iterations'), 'start_time': info.get('start_time'), 'iteration': i + 1}
        return {'status': 'IDLE'}
    
    def run(options):
        max_iterations = options.get('max_iterations')
        damping_factor = options.get('damping_factor')

        from src.celery.workers import run_page_ranking

        
        run_page_ranking.delay(max_iterations, damping_factor)
        
        return True
