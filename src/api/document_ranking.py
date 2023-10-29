from flask import Blueprint, request
from src.document_ranking.tf_idf import get_all_tfidf_for_api, run_background_service
import multiprocessing
import json
from threading import Thread
import time
import os
import signal
import json
from src.document_ranking.service import DocumentRankingService

bp_document_ranking = Blueprint(
    "document_ranking",
    __name__,
)

handles = []


def document_ranking_task_checker(event, kill_event):

    print("[checker thread] waiting for document ranking task finished...")
    event.wait()
    print("[checker thread] document ranking task done, clearing...")
    handles.clear()
    kill_event.set()
    print("[checker thread] all done, handles cleared!")


def document_ranking_task(event, type, options):
    
    DocumentRankingService(type).run(options)

    event.set()


@bp_document_ranking.route("/stop", methods=["POST"])
def stop_task():
    if (len(handles) == 0):
        return {
            "message": "nothing running!"
        }, 200
    os.kill(handles[0].get("pid"), signal.SIGTERM)
    handles.clear()
    return {
        "message": "task stopped!"
    }, 200


@bp_document_ranking.route("status", methods=["GET"])
def get_task_status():

    if len(handles) == 0:
        return {
            "status": "IDLE",
        }, 200

    return {
        "status": "RUNNING" if len(handles) > 0 else "IDLE",
        "start_time": handles[0]["start_time"] if len(handles) > 0 else -1,
        "algorithm":  handles[0]["algorithm"]
    }, 200


@bp_document_ranking.route("/start", methods=["POST"])
def create_new_task():
    if (len(handles) != 0):
        return {
            "message": "service is currently running!",
        }, 400

    event = multiprocessing.Event()
    kill_event = multiprocessing.Event()

    document_ranking_process = multiprocessing.Process(
        target=document_ranking_task,
        args=(event,request.args.get('algorithm') or 'tfidf', {"use_gst": request.args.get('use_gst')}),
    )

    checker_thread = Thread(
        target=document_ranking_task_checker, args=(event, kill_event))
    checker_thread.start()
    document_ranking_process.start()
    start_time = time.time()
    handles.append({
        "task": "document-ranking",
        "start_time": start_time,
        "pid": document_ranking_process.pid,
        "algorithm": request.args.get('algorithm') or 'tfidf'
    })

    return {'message': 'started!'}, 200


@bp_document_ranking.route("/tf_idf")
def get_tf_idf_ranks():
    try:
        keyword = request.args.get("keyword", default="", type=str)
        start = request.args.get("start", default="", type=str)
        length = request.args.get("length", default="", type=str)

        if keyword == "":
            response = {
                "ok": False,
                "message": "Keyword tidak ada. Masukkan keyword pada url seperti '?keyword=barcelona'",
            }
        else:
            if start != "" and length != "":
                data = get_all_tfidf_for_api(keyword, int(start), int(length))
            else:
                data = get_all_tfidf_for_api(keyword)
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
