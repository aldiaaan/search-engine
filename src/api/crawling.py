from flask import Blueprint, request
from src.crawling.crawl import Crawl
from src.crawling.crawl import CrawlUtils
import multiprocessing
import json
import os

bp_crawling = Blueprint("crawling", __name__)
processes = []


def start_crawling_task(status, start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword):
    c = Crawl(status, start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword)
    c.run()


@bp_crawling.route("/start")
def start_crawling():
    try:
        crawler_duration_sec = request.args.get("duration", default="", type=str)
        crawler_act = request.args.get("status", default="resume", type=str)
        start_urls = request.args.getlist("urls[]")
        # start_urls = os.getenv("CRAWLER_START_URLS").split()
        max_threads = os.getenv("CRAWLER_MAX_THREADS")
        # print(crawler_start_urls)
        # return 200
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
        process = multiprocessing.Process(
            target=start_crawling_task,
            args=(crawler_act,start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword),
        )
        process.start()
        processes.append(process)

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


@bp_crawling.route("/stop")
def stop_crawling():
    try:
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


@bp_crawling.route("/crawlers", methods=["GET"])
def get_crawler_details():
    try:
        start = request.args.get("start", default="", type=int)
        length = request.args.get("length", default="", type=int)
        
        crawl_utils = CrawlUtils()

        crawlers, pagination = crawl_utils.get_crawlers(start, length)

        response = {
            "data": {
                "crawlers": crawlers,
                "pagination": pagination
            }
        }
        
        json_obj = json.dumps(response, indent=4, default=str)
        return json.loads(json_obj), 200

    except Exception as e:
        print(e)
        return {
            "ok": False,
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
