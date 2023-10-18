from flask import Blueprint, request, jsonify
from src.account import Account
from src.auth import Auth
from functools import wraps
import math

bp_account = Blueprint("account", __name__)


def match_account_with_incoming_account_id(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if kwargs['account_id'] != str(kwargs['account'].id):
            return jsonify({'message': 'you are not allowed accessing this resource'}), 400
        return f(*args, **kwargs)
    return wrap

def roles_needed(roles):
    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            account = kwargs['account']

            if account.role not in roles:
                return jsonify({"message": "not allowed with current role"}), 400

            return f(*args, **kwargs)
        return wrap
    return decorator

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        token = request.headers.get("X-Auth-Token")
        account = Auth.verify(token)
        
        if account is None:
            return jsonify({
                "message": "invalid credentials or account not found"
            }), 400
        kwargs['account'] = account
        return f(*args, **kwargs)
    return wrap

@bp_account.route("/", methods=["GET"])
@login_required
# @roles_needed(['root'])
def get_accounts(account):
    accounts, total = Account.find({'query': request.args.get('query') or None})

    return jsonify({
        "data": accounts,
        "pagination": {
            "total": total,
            "limit": int(request.args.get("limit") or 20),
            "pages": math.ceil(total / int(request.args.get("limit") or 20)),
            "current_page": math.floor(int(request.args.get("start") or 0) / int(request.args.get("limit") or 10))
        }
    })

@bp_account.route("/create", methods=["POST"])
def create_new_account():
    payload = request.get_json()
    new_account = Account(email=payload["email"], first_name=payload["first_name"],
                          last_name=payload["last_name"], password=payload["password"], role=Account.ROLE_STAFF)
    new_account.save()

    return jsonify({
        "data": new_account.to_json(),
        "message": "Ok"
    }), 200

@bp_account.route("/me", methods=["GET"])
@login_required
@roles_needed(['staff'])
def me(account):
    payload = request.get_json()
    try:
        return jsonify({"data": account.to_dict()}), 200
    except Exception as e:
        return jsonify({"message": "something went wrong"}), 400

@bp_account.route("/<account_id>/update", methods=["PUT"])
@login_required
@match_account_with_incoming_account_id
def update_account(account_id, account):
    payload = request.get_json()
    account.first_name = payload.get("first_name") or account.first_name
    account.last_name = payload.get("last_name") or account.last_name
    account.update()
    return jsonify({"message": "ok"}), 200


@bp_account.route("/<account_id>/delete", methods=["DELETE"])
@login_required
@roles_needed(['root'])
def delete_account(account_id, account):
    Account(id=account_id).delete()
    return jsonify({"message": "ok"}), 200
