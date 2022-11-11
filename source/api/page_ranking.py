from flask import Blueprint, request
from source.page_ranking.page_rank import PageRank
import json

bp_page_ranking = Blueprint("page_ranking", __name__)


@bp_page_ranking.route("/page_rank")
def get_page_rank_ranks():
    try:
        start = request.args.get("start", default="", type=str)
        length = request.args.get("length", default="", type=str)

        page_rank = PageRank()
        if start != "" and length != "":
            data = page_rank.get_all_pagerank_for_api(int(start), int(length))
        else:
            data = page_rank.get_all_pagerank_for_api()
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