import sys
import os

sys.path.insert(0, os.path.abspath('../..'))

from src.api.app import run
from celery import shared_task
from src.crawling.crawl import Crawl
from multiprocessing import  Process
from src.document_ranking.service import DocumentRankingService
from src.page_ranking.page_rank import run_background_service
from celery.contrib.abortable import AbortableTask
from celery.signals import task_revoked
import time
from celery.result import AsyncResult
from src.utils import MemoryLogger

MemoryLogger.start()

flask = run()
handle = None

@task_revoked.connect
def on_task_revoked(*args, **kwargs):
    print(str(kwargs))
    t = AsyncResult(kwargs['request'].id)
    print('task_revoked')
    print(t._get_task_meta())


@shared_task(name='workers.document_ranking.run', bind=True)
def run_document_ranking(self, algorithm, options):    
    
    start_time = time.time()

    self.update_state(meta={
        "algorithm": algorithm,
        "start_time": start_time,
        "options": options or dict()
    })

    s = DocumentRankingService(algorithm=algorithm)
    
    s.run(options=options)
    

@shared_task(name='workers.page_ranking.run', bind=True)
def run_page_ranking(self, max_iterations, damping_factor):

    def handle_iteration_change(i):
        self.update_state(meta={
            "iterations": i
        })
    
    start_time = time.time()
    
    self.update_state(meta={
        "max_iterations": max_iterations,
        "damping_factor": damping_factor,
        "start_time": start_time,
    })

    run_background_service({
        "max_iterations": max_iterations,
        "damping_factor": damping_factor,
        "on_iteration_change": handle_iteration_change
    })


@shared_task(name='workers.crawler.run', bind=True)
def run_crawl(self, status, start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword):
    start_time = time.time()
    

    c = Crawl(status, start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword)

    self.update_state(meta={
        "threads": max_threads,
        "duration": bfs_duration_sec + msb_duration_sec,
        "start_time": start_time,
        "end_time": start_time + bfs_duration_sec + msb_duration_sec,
        # "pid": p.pid        
    })
    c.run()
    # p = Process(target=c.run)

    # p.start()



    # self.update_state(meta={
    #   "pid": p.pid
    # })

    # p.join()
    
celery_app = flask.extensions["celery"]

