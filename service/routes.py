"""
Account Service

This microservice handles the lifecycle of Accounts
"""

# pylint: disable=unused-import
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            # paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based the data in the body that is posted
    """
    if request.content_type != "application/json":
        return make_response(
            "Unsupported content type sent ", status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    # Uncomment once get_accounts has been implemented
    # location_url = url_for("get_accounts", account_id=account.id, _external=True)
    location_url = "/"  # Remove once get_accounts has been implemented
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# LIST ALL ACCOUNTS
######################################################################


@app.route("/accounts", methods=["GET"])
def list_accounts():
    all_accounts = Account.all()
    account_list = [account.serialize() for account in all_accounts]
    app.logger.info(f"Listing {len(account_list)} accounts")
    return make_response(jsonify(account_list), status.HTTP_200_OK)


######################################################################
# READ AN ACCOUNT
######################################################################


@app.route("/accounts/<id>", methods=["GET"])
def read_account(id):
    account = Account.find(id)
    if account is None:
        return make_response(
            f"Account with id {0} not found", status.HTTP_404_NOT_FOUND
        )
    else:
        account_data = account.serialize()
        return make_response(account_data, status.HTTP_200_OK)


######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################


@app.route("/accounts/<id>", methods=["PUT"])
def update_account(id):
    updated_account = request.get_json()
    account = Account.find(id)
    if account is None:
        return make_response(
            "Could not find account to update", status.HTTP_404_NOT_FOUND
        )
    account.deserialize(updated_account)
    account.update()
    return make_response(account.serialize(), status.HTTP_200_OK)


######################################################################
# DELETE AN ACCOUNT
######################################################################


@app.route("/accounts/<id>", methods=["DELETE"])
def delete_account(id):
    account = Account.find(id)
    if account is None:
        return make_response(
            "Could not find account to delete", status.HTTP_404_NOT_FOUND
        )
    else:
        account.delete()
        return make_response(f"Account with {id} deleted", status.HTTP_204_NO_CONTENT)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
