from flask import Blueprint, request, current_app
from src.crawling.crawl import Crawl
from src.crawling.crawl import CrawlUtils
from src.domain import Domain
from src.webpage import Webpage
import multiprocessing
import json
from threading import Thread
import time
import os
import multiprocessing
import signal
from celery.result import AsyncResult

bp_crawling = Blueprint("crawling", __name__)
processes = []

IS_CRAWLING_RUNNING = False


def get_active_crawling_task():
    try:
        active_tasks = current_app.extensions["celery"].control.inspect().active().get('celery@SEARCH_ENGINE_WORKERS')
    except Exception as e:
        return None, {}


    tasks = [x for x in active_tasks if x.get('name') == 'workers.crawler.run']
    
    if len(tasks) == 0:
        return None, {}
    task = AsyncResult(tasks[0].get('id'))
    # print(tasks[0].get('args'))
    [_, _, threads, _, _, _] = tasks[0].get('args')
    # print(task.args
    
    # ['resume', ['https://detik.com'], 3, 2222, 0, ''])    
    return task,  {"threads": threads or None}


@bp_crawling.route("stop")
def stop_crawler():
    task, info = get_active_crawling_task()

    if task is None:
        return {
            "message": "crawling service not running yet"
        }
    
    task.revoke(terminate=True, signal='SIGKILL')

    return {
        "message": "ok!"
    }
    
    

@bp_crawling.route('specs')
def get_specs():
    return {
        "available_cpus": multiprocessing.cpu_count() 
    }, 200

@bp_crawling.route("status")
def get_crawling_status():

    task, info = get_active_crawling_task()
    print(task)

    if task is None:
        return {
            "status": "IDLE"
        }
    return {
        "status": "RUNNING",
        "start_time": info.get('start_time'),
        "end_time": info.get('end_time'),
        "duration": info.get('duration'),
        "threads": info.get('threads')        
    }


@bp_crawling.route("metrics")
def get_crawling_info():

    _, total_domains = Domain.find({
        "with_country": False,
        "query": "",
        "limit": 18446744073709551610,
        "start": 0,
        "sort_total_pages": "DESC"
    })
    _, total_webpages, countries = Webpage.find({
        "query": "",
        "limit": 18446744073709551610,
        "start": 0,
        "sort_pagerank_score": "DESC"
    })

    return {        
        "total_domains": total_domains,
        "total_webpages": total_webpages,
        "total_webpages_size": Webpage.get_total_size(),
        "domains_stats": Domain.get_stats(),
        "countries": countries
    }

@bp_crawling.route("start")
def start_crawling():

    task, info = get_active_crawling_task()
    
    if task is not None:
        return {
            "msg": "Service is currently running!"
        }
    
    try:
        crawler_duration_sec = request.args.get("duration", default="", type=str)
        start_urls = os.getenv("CRAWLER_START_URLS").split()
        max_threads = int(request.args.get('threads')) or os.getenv("CRAWLER_MAX_THREADS")
        try:
            msb_keyword = os.getenv("CRAWLER_KEYWORD")
        except:
            msb_keyword = ""

        if msb_keyword != "":
            bfs_duration_sec = int(crawler_duration_sec) // 2
            msb_duration_sec = int(crawler_duration_sec) // 2
        else:
            bfs_duration_sec = int(crawler_duration_sec)
            msb_duration_sec = 0

        from src.celery.workers import run_crawl
        

        process = run_crawl.delay("resume", start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword)

        response = {
            "ok": True,
            "message": "Sukses",
        }

        json_obj = json.dumps(response, indent=4, default=str)
        return json.loads(json_obj), 200

    except Exception as e:
        print(e)
        return {
            "ok": False,
            "message": e
        }, 500



@bp_crawling.route("/pages")
def get_crawled_pages():
    try:
        start = request.args.get("start", default="", type=str)
        length = request.args.get("length", default="", type=str)

        crawl_utils = CrawlUtils()
        if start != "" and length != "":
            data = crawl_utils.get_crawled_pages_api(int(start), int(length))
        else:
            data = crawl_utils.get_crawled_pages_api()

        response = {
            "ok": True,
            "message": "Sukses",
            "data": data,
        }
        json_obj = json.dumps(response, indent=4, default=str)
        return json.loads(json_obj), 200

    except Exception as e:
        return {
            "ok": False,
            "message": e,
        }, 500


@bp_crawling.route("/page_information", methods=["POST"])
def get_page_information():
    try:
        id_pages = request.json["id_pages"]

        crawl_utils = CrawlUtils()
        data = crawl_utils.get_page_information_by_ids(id_pages)

        response = {
            "ok": True,
            "message": "Sukses",
            "data": data,
        }
        json_obj = json.dumps(response, indent=4, default=str)
        return json.loads(json_obj), 200

    except Exception as e:
        return {
            "ok": False,
            "message": e,
        }, 500


@bp_crawling.route("/start_insert", methods=["POST"])
def start_insert_pages():
    try:
        start_urls = request.json["start_urls"]
        keyword = request.json["keyword"]
        duration_crawl = request.json["duration_crawl"]
        crawl_utils = CrawlUtils()

        id_crawling = crawl_utils.start_insert_api(start_urls, keyword, duration_crawl)

        response = {
            "ok": True,
            "message": "Sukses",
            "data": {"id_crawling": id_crawling},
        }
        json_obj = json.dumps(response, indent=4, default=str)
        return json.loads(json_obj), 200
    except Exception as e:
        return {
            "ok": False,
            "message": e,
        }, 500


@bp_crawling.route("/insert_page", methods=["POST"])
def insert_page():
    try:
        page_information = request.json["page_information"]
        page_forms = request.json["page_forms"]
        page_images = request.json["page_images"]
        page_linking = request.json["page_linking"]
        page_list = request.json["page_list"]
        page_scripts = request.json["page_scripts"]
        page_styles = request.json["page_styles"]
        page_tables = request.json["page_tables"]
        crawl_utils = CrawlUtils()

        crawl_utils.insert_page_api(
            page_information, page_forms, page_images, page_linking, page_list, page_scripts, page_styles, page_tables
        )

        response = {
            "ok": True,
            "message": "Sukses",
        }
        json_obj = json.dumps(response, indent=4, default=str)
        return json.loads(json_obj), 200
    except Exception as e:
        return {
            "ok": False,
            "message": e,
        }, 500
