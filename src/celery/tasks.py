

import sys

sys.path.insert(0, "C:\\Users\\Aldian\\Desktop\\projects\\search-engine")
from src.api.app import run


celery_app = run().extensions["celery"]
# print(celery_app.tasks)

# @shared_task(ignore_result=False)
# def crawl(status, start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword):
#     c = Crawl(status, start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword)    
#     c.run()

# @shared_task(ignore_result=False)
# def ping():
#     print('pong!')
