from flask import Blueprint, request
from src.crawling.crawl import Crawl
from src.crawling.crawl import CrawlUtils
from src.domain import Domain
from src.webpage import Webpage
import multiprocessing
import json
from threading import Thread
import time
import os
import signal

bp_crawling = Blueprint("crawling", __name__)
processes = []

IS_CRAWLING_RUNNING = False

def crawling_task_checker(event, kill_event):
    
    print("[checker thread] waiting for crawling task finished...")
    event.wait()
    print("[checker thread] crawling task done, clearing...")
    processes.clear()
    kill_event.set()
    print("[checker thread] all done, processes cleared!")

def start_crawling_task(event, status, start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword):
    c = Crawl(status, start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword)
    
    print("starting running crawling task")
    c.run()
    event.set()


@bp_crawling.route("stop")
def stop_crawler():
    if len(processes) > 0:
        os.kill(processes[0].get("pid"), signal.SIGTERM)
        processes.clear()
        print("process stopped")
        return {
            "message": "stopped"
        }
    return {
        "message": "crawling service not running yet"
    }

@bp_crawling.route("status")
def get_crawling_status():

    return {
        "status": "RUNNING" if len(processes) > 0 else "IDLE",
        "start_time": processes[0]["start_time"] if len(processes) > 0 else -1,
        "end_time": processes[0]["end_time"] if len(processes) > 0 else -1,
        "duration": processes[0]["duration"] if len(processes) > 0 else -1,        
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
    _, total_webpages = Webpage.find({
        "query": "",
        "limit": 18446744073709551610,
        "start": 0,
        "sort_pagerank_score": "DESC"
    })

    return {        
        "total_domains": total_domains,
        "total_webpages": total_webpages,
        "total_webpages_size": Webpage.get_total_size()
    }

@bp_crawling.route("/start")
def start_crawling():
    
    if len(processes) > 0:
        return {
            "msg": "Service is currently running!"
        }
    
    try:
        crawler_duration_sec = request.args.get("duration", default="", type=str)
        start_urls = os.getenv("CRAWLER_START_URLS").split()
        max_threads = os.getenv("CRAWLER_MAX_THREADS")
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

        event = multiprocessing.Event()
        kill_event = multiprocessing.Event()
        

        process = multiprocessing.Process(
            target=start_crawling_task,
            args=(event, "resume", start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword),
        )

        checker_thread = Thread(target=crawling_task_checker, args=(event, kill_event))
        checker_thread.start()
        process.start()
        start_time = time.time()
        processes.append({
            "task": "crawling",
            "start_time": start_time,
            "end_time": start_time + int(crawler_duration_sec),
            "duration": crawler_duration_sec,
            "pid": process.pid
        })

        response = {
            "ok": True,
            "message": "Sukses",
        }
        json_obj = json.dumps(response, indent=4, default=str)
        return json.loads(json_obj), 200

    except Exception as e:
        print(e)
        return {
            "ok": False
        }, 500


@bp_crawling.route("/stop")
def stop_crawling():
    try:
        for process in processes:
            process.terminate()
            process.join()

        processes.clear()

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
