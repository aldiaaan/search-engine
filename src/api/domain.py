from flask import Blueprint, request, jsonify
from src.auth import Auth
from src.common.errors import ServerException
from src.domain import Domain
import math

bp_domain = Blueprint("domain", __name__)


@bp_domain.route("/xx")
def get_domains():
    domains, total = Domain.find({
        "limit": int(request.args.get("limit") or 10),
        "start": int(request.args.get("start") or 0),
        "sort_total_pages": request.args.get("sort_total_pages") or "DESC"
    })
    return {
        "data": list(map(lambda x: x.to_dict(), domains)),
        "pagination": {
            "total": total,
            "pages": math.ceil(total / int(request.args.get("limit") or 10)),
            "current_page": math.floor(int(request.args.get("start") or 0) / int(request.args.get("limit") or 10))
        }
    }
