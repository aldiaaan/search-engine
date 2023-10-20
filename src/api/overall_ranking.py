from flask import Blueprint, request
from src.overall_ranking.similarity import get_all_similarity_for_api
import json
import math

bp_overall_ranking = Blueprint(
    "overall_ranking",
    __name__,
)


@bp_overall_ranking.route("/similarity")
def get_similarity_ranks():
    try:
        keyword = request.args.get("keyword", default="", type=str)
        sort = request.args.get("sort", default="similarity", type=str)
        start = request.args.get("start", default="", type=str)
        length = request.args.get("length", default="", type=str)

        if keyword == "":
            response = {
                "ok": False,
                "message": "Keyword tidak ada. Masukkan keyword pada url seperti '?keyword=barcelona'",
            }
        else:
            if start != "" and length != "":
                data, total = get_all_similarity_for_api(keyword, sort, int(start), int(length))
            else:
                data, total = get_all_similarity_for_api(keyword, sort)
                print(total)
            response = {
                "ok": True,
                "message": "Sukses",
                "data": data,
                "pagination": {
                    "total": total,
                    "pages": math.ceil(total / int(length)),
                    "per_page": int(length)
                }
            }
        json_obj = json.dumps(response, indent=4, default=str)
        return json.loads(json_obj), 200

    except Exception as e:
        return {
            "ok": False,
            "message": e,
        }, 500
