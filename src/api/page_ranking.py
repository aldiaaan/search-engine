from flask import Blueprint, request
from src.page_ranking.page_rank import get_all_pagerank_for_api
from src.page_ranking.page_rankling_service import PageRankingService
import json

bp_page_ranking = Blueprint("page_ranking", __name__)


@bp_page_ranking.route("/status", methods=['GET'])
def status_pageranking_service():
    try:
        return PageRankingService.status()
    except Exception as e:
        return {
            "ok": False,
            "message": str(e),
        }, 500


@bp_page_ranking.route("/metrics", methods=['GET'])
def metrics_pageranking_service():
    try:
        return PageRankingService.get_metrics()
    except Exception as e:
        return {
            "ok": False,
            "message": str(e),
        }, 500
    

@bp_page_ranking.route("/stop", methods=['POST'])
def stop_pageranking_service():
    try:
        PageRankingService.stop()
        return {
            "ok": True
        }
    except Exception as e:
        return {
            "ok": False,
            "message": str(e),
        }, 500


@bp_page_ranking.route("/start", methods=['POST'])
def start_pagerank_service():
    try:
        max_iterations = int(request.args.get("max_iterations", default="20", type=str))
        damping_factor = float(request.args.get("damping_factor", default="0.85", type=str))

        PageRankingService.run({
            'max_iterations': max_iterations,
            'damping_factor': damping_factor
        })

        response = {
            "ok": True,
            "message": "Sukses",
        }
        json_obj = json.dumps(response, indent=4, default=str)
        return json.loads(json_obj), 200

    except Exception as e:
        return {
            "ok": False,
            "message": str(e),
        }, 500


@bp_page_ranking.route("/page_rank")
def get_page_rank_ranks():
    try:
        start = request.args.get("start", default="", type=str)
        length = request.args.get("length", default="", type=str)

        if start != "" and length != "":
            data = get_all_pagerank_for_api(int(start), int(length))
        else:
            data = get_all_pagerank_for_api()
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
