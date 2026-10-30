from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from service.models import Account, db


accounts = Blueprint("accounts", __name__)
EDITABLE_FIELDS = ("name", "email", "phone", "account_type", "status", "balance")


def _error(message, status_code):
    return jsonify({"error": message}), status_code


def _request_data():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, _error("Request body must be a JSON object", 400)
    return data, None


def _validated_fields(data, creating=False):
    unknown = set(data) - set(EDITABLE_FIELDS)
    if unknown:
        return None, f"Unknown field: {sorted(unknown)[0]}"

    if creating:
        for field in ("name", "email"):
            if not isinstance(data.get(field), str) or not data[field].strip():
                return None, f"{field} is required"

    fields = dict(data)
    if "name" in fields and (not isinstance(fields["name"], str) or not fields["name"].strip()):
        return None, "name must be a non-empty string"
    if "email" in fields:
        if not isinstance(fields["email"], str) or "@" not in fields["email"]:
            return None, "email must be a valid email address"
    if "balance" in fields:
        try:
            balance = Decimal(str(fields["balance"]))
        except (InvalidOperation, ValueError):
            return None, "balance must be a number"
        if not balance.is_finite() or balance < 0:
            return None, "balance must be a non-negative number"
        fields["balance"] = balance

    for field in ("phone", "account_type", "status"):
        if field in fields and not isinstance(fields[field], str):
            return None, f"{field} must be a string"

    return fields, None


@accounts.get("/accounts")
def list_accounts():
    records = Account.query.order_by(Account.id).all()
    return jsonify({"accounts": [record.to_dict() for record in records], "count": len(records)})


@accounts.post("/accounts")
def create_account():
    data, error = _request_data()
    if error:
        return error

    fields, message = _validated_fields(data, creating=True)
    if message:
        return _error(message, 400)

    account = Account(**fields)
    db.session.add(account)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("An account with this email already exists", 409)

    return jsonify(account.to_dict()), 201


@accounts.get("/accounts/<int:account_id>")
def read_account(account_id):
    account = db.session.get(Account, account_id)
    if account is None:
        return _error("Account not found", 404)
    return jsonify(account.to_dict())


@accounts.put("/accounts/<int:account_id>")
def update_account(account_id):
    account = db.session.get(Account, account_id)
    if account is None:
        return _error("Account not found", 404)

    data, error = _request_data()
    if error:
        return error
    fields, message = _validated_fields(data)
    if message:
        return _error(message, 400)
    if not fields:
        return _error("At least one account field is required", 400)

    for field, value in fields.items():
        setattr(account, field, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("An account with this email already exists", 409)

    return jsonify(account.to_dict())


@accounts.delete("/accounts/<int:account_id>")
def delete_account(account_id):
    account = db.session.get(Account, account_id)
    if account is None:
        return _error("Account not found", 404)

    db.session.delete(account)
    db.session.commit()
    return jsonify({"id": account_id, "deleted": True})


@accounts.delete("/accounts")
def delete_account_by_email():
    data, error = _request_data()
    if error:
        return error

    email = data.get("email")
    if not isinstance(email, str) or not email.strip():
        return _error("email is required", 400)

    account = Account.query.filter_by(email=email).first()
    if account is None:
        return _error("Account not found", 404)

    db.session.delete(account)
    db.session.commit()
    return "", 204
