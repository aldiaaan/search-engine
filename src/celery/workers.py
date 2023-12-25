import sys
sys.path.insert(0, "C:\\Users\\Aldian\\Desktop\\projects\\search-engine")

from src.api.app import run
from celery import shared_task
from src.crawling.crawl import Crawl
from threading import Thread
from multiprocessing import Event, Process
from celery.contrib.abortable import AbortableTask
from src.document_ranking.service import DocumentRankingService
from src.page_ranking.page_rank import run_background_service, get_iteration_count
import time


app = run()
handle = None


@shared_task(name='workers.document_ranking.run', bind=True, base=AbortableTask)
def run_document_ranking(self, algorithm, options):
    def check_if_aborted():
        # print(f'checking if aborted.... {self.is_aborted()}')
        return self.is_aborted()

    
    start_time = time.time()

    self.update_state(meta={
        "algorithm": algorithm,
        "start_time": start_time,
        "options": options or dict()
    })

    s = DocumentRankingService(algorithm=algorithm, is_aborted=check_if_aborted)
    
    s.run(options=options)
    

@shared_task(name='workers.page_ranking.run', bind=True, base=AbortableTask)
def run_page_ranking(self, max_iterations, damping_factor):
    def check_if_aborted():
        print(f'checking if aborted.... {self.is_aborted()}')
        return self.is_aborted()

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
        "is_aborted": check_if_aborted,
        "on_iteration_change": handle_iteration_change
    })
    

@shared_task(name='workers.crawler.run', bind=True, base=AbortableTask)
def run_crawl(self, status, start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword):
    def check_if_aborted():
        print(f'checking if aborted.... {self.is_aborted()}')
        return self.is_aborted()
    
    start_time = time.time()
    
    self.update_state(meta={
        "threads": max_threads,
        "duration": bfs_duration_sec + msb_duration_sec,
        "start_time": start_time,
        "end_time": start_time + bfs_duration_sec + msb_duration_sec
    })

    c = Crawl(status, start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword, is_aborted=check_if_aborted)

    c.run()


    

celery_app = app.extensions["celery"]

