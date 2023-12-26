from flask import Blueprint, request, current_app
from src.document_ranking.tf_idf import get_all_tfidf_for_api, run_background_service
import multiprocessing
import json
from threading import Thread
import time
import os
import signal
import json
from src.document_ranking.service import DocumentRankingService
from celery.result import AsyncResult

bp_document_ranking = Blueprint(
    "document_ranking",
    __name__,
)


def get_active_document_ranking_task():
    try:
        active_tasks = current_app.extensions["celery"].control.inspect().active().get('celery@SEARCH_ENGINE_WORKERS')
    except Exception as e:
        return None, {}


    tasks = [x for x in active_tasks if x.get('name') == 'workers.document_ranking.run']
    
    if len(tasks) == 0:
        return None, {}
    
    task = AsyncResult(tasks[0].get('id'))
    return task, task._get_task_meta().get('result')


@bp_document_ranking.route("/stop", methods=["POST"])
def stop_task():
    task, info = get_active_document_ranking_task()
    if task is None:
        return {
            "message": "nothing running!"
        }, 200
    
    task.revoke(terminate=True, signal='SIGKILL')

    return {
        "message": "task stopped!"
    }, 200


@bp_document_ranking.route("status", methods=["GET"])
def get_task_status():

    task, info = get_active_document_ranking_task()

    if task is None:
        return {
            "status": "IDLE",
        }, 200

    return {
        "status": "RUNNING",
        "start_time": info.get('start_time'),
        "algorithm":  info.get("algorithm")
    }, 200


@bp_document_ranking.route("/start", methods=["POST"])
def create_new_task():
    task, info = get_active_document_ranking_task()
    if task is not None:
        return {
            "message": "service is currently running!",
        }, 400

    from src.celery.workers import run_document_ranking
    run_document_ranking.delay(request.args.get('algorithm') or 'tfidf', {"use_gst": request.args.get('use_gst')})

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
