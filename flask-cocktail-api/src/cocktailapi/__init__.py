"""
cocktailapi - A small API for managing cocktail recipes.
"""

from datetime import datetime
import os

from pymongo.collection import Collection

import flask
from flask import Flask, request, url_for, jsonify
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError

from .model import Cocktail

# Configure Flask & Flask-PyMongo:
app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
pymongo = PyMongo(app)

# Get a reference to the recipes collection.
# Uses a type-hint, so that your IDE knows what's happening!
recipes: Collection = pymongo.db.recipes


@app.errorhandler(404)
def resource_not_found(e):
    """
    An error-handler to ensure that 404 errors are returned as JSON.
    """
    return jsonify(error=str(e)), 404


@app.errorhandler(DuplicateKeyError)
def resource_not_found(e):
    """
    An error-handler to ensure that MongoDB duplicate key errors are returned as JSON.
    """
    return jsonify(error=f"Duplicate key error."), 400


@app.route("/cocktails/")
def list_cocktails():
    """
    GET a list of cocktail recipes.

    The results are paginated using the `page` parameter.
    """

    page = int(request.args.get("page", 1))
    per_page = 10
    cursor = recipes.find().sort("name").skip(per_page * (page - 1)).limit(per_page)

    cocktail_count = recipes.count_documents({})

    links = {
        "self": {"href": url_for(".list_cocktails", page=page, _external=True)},
        "last": {
            "href": url_for(
                ".list_cocktails", page=(cocktail_count // per_page) + 1, _external=True
            )
        },
    }
    if page > 1:
        links["prev"] = (
            {"href": url_for(".list_cocktails", page=page - 1, _external=True)},
        )
    if page - 1 < cocktail_count // per_page:
        links["next"] = (
            {"href": url_for(".list_cocktails", page=page + 1, _external=True)},
        )

    return {
        "recipes": [Cocktail(**doc).to_json() for doc in cursor],
        "_links": links,
    }


@app.route("/cocktails/", methods=["POST"])
def new_cocktail():
    raw_cocktail = request.get_json()
    raw_cocktail["date_added"] = datetime.utcnow()

    cocktail = Cocktail(**raw_cocktail)
    insert_result = recipes.insert_one(cocktail.to_bson())
    cocktail_doc = recipes.find_one({"_id": insert_result.inserted_id})
    if cocktail_doc is None:
        flask.abort(500, "The inserted cocktail went away.")

    return Cocktail(**cocktail_doc).to_json()


@app.route("/cocktails/<string:slug>", methods=["GET"])
def get_cocktail(slug):
    recipe = recipes.find_one_or_404({"slug": slug})
    return Cocktail(**recipe).to_json()


@app.route("/cocktails/<string:slug>", methods=["PUT"])
def update_cocktail(slug):
    cocktail = Cocktail(**request.get_json())
    cocktail.date_updated = datetime.utcnow()
    update_result = recipes.update_one(
        {"slug": slug},
        {"$set": cocktail.to_bson()},
    )

    if update_result.matched_count == 1:
        cocktail_doc = recipes.find_one({"slug": cocktail.slug})
        if cocktail_doc is None:
            flask.abort(500, "The updated cocktail went away.")
        return Cocktail(**cocktail_doc).to_json()
    else:
        flask.abort(404, "Cocktail not found")


@app.route("/cocktails/<string:slug>", methods=["DELETE"])
def delete_cocktail(slug):
    deleted_cocktail = recipes.find_one_and_delete(
        {"slug": slug},
    )
    if deleted_cocktail:
        return Cocktail(**deleted_cocktail).to_json()
    else:
        flask.abort(404, "Cocktail not found")
