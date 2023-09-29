from flask import Blueprint, request, jsonify
from src.account import Account

bp_account = Blueprint("account", __name__)


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


@bp_account.route("/<id>/update", methods=["PATCH"])
def update_account(id):
    payload = request.get_json()
    account = Account(id=id, email=payload["email"], first_name=payload["first_name"],
                      last_name=payload["last_name"])
