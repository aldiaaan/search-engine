from flask import Blueprint, request
from src.document_ranking.tf_idf import get_all_tfidf_for_api, run_background_service
import multiprocessing
import json
from threading import Thread
import time
from flask import current_app
import os
import signal
import json
from src.document_ranking.service import DocumentRankingService
from celery.contrib.abortable import AbortableAsyncResult


bp_document_ranking = Blueprint(
    "document_ranking",
    __name__,
)

handles = []


def get_document_ranking_task():
    tasks = [x for x in current_app.extensions["celery"].control.inspect().active(
    ).get('celery@SEARCH_ENGINE_WORKERS') if x.get('name') == 'workers.document_ranking.run']
    print(tasks)
    if len(tasks) == 0:
        return None
    task = AbortableAsyncResult(tasks[0].get('id'))
    return task

@bp_document_ranking.route("/stop", methods=["POST"])
def stop_task():
    t = get_document_ranking_task()
    if t is None:
        return {
            "message": "nothing running!"
        }, 200
    t.abort()
    return {
        "message": "task stopped!"
    }, 200


@bp_document_ranking.route("status", methods=["GET"])
def get_task_status():
    t = get_document_ranking_task()

    if t is None:
        return {
            "status": "IDLE",
        }, 200

    return {
        "status": "RUNNING",
        "start_time": t.info.get("start_time") if len(handles) > 0 else -1,
        "algorithm":  t.info.get("algorithm")
    }, 200


@bp_document_ranking.route("/start", methods=["POST"])
def create_new_task():
    t = get_document_ranking_task()
    if t is not None:
        return {
            "message": "service is currently running!",
        }, 400
    

    from src.celery.workers import run_document_ranking
    run_document_ranking.delay(request.args.get('algorithm') or 'tfidf', {"use_gst": request.args.get('use_gst')})
    return {'message': 'started!'}, 200

# @bp_document_ranking.route("/start", methods=["POST"])
# def create_new_task():
#     if (len(handles) != 0):
#         return {
#             "message": "service is currently running!",
#         }, 400

#     event = multiprocessing.Event()
#     kill_event = multiprocessing.Event()

#     document_ranking_process = multiprocessing.Process(
#         target=document_ranking_task,
#         args=(event,request.args.get('algorithm') or 'tfidf', {"use_gst": request.args.get('use_gst')}),
#     )

#     checker_thread = Thread(
#         target=document_ranking_task_checker, args=(event, kill_event))
#     checker_thread.start()
#     document_ranking_process.start()
#     start_time = time.time()
#     handles.append({
#         "task": "document-ranking",
#         "start_time": start_time,
#         "pid": document_ranking_process.pid,
#         "algorithm": request.args.get('algorithm') or 'tfidf'
#     })

#     return {'message': 'started!'}, 200


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
