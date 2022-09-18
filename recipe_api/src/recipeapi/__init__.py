"""
recipeapi - A small API for managing recipe recipes.
"""

from datetime import datetime
import os

from pymongo.collection import Collection, ReturnDocument

import flask
from flask import Flask, request, url_for, jsonify
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError

from .model import Recipe
from .objectid import PydanticObjectId

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


@app.route("/recipes/")
def list_recipes():
    """
    GET a list of recipe recipes.

    The results are paginated using the `page` parameter.
    """

    page = int(request.args.get("page", 1))
    per_page = 10  # A const value.

    # For pagination, it's necessary to sort by name,
    # then skip the number of docs that earlier pages would have displayed,
    # and then to limit to the fixed page size, ``per_page``.
    cursor = recipes.find().sort("name").skip(per_page * (page - 1)).limit(per_page)

    recipe_count = recipes.count_documents({})

    links = {
        "self": {"href": url_for(".list_recipes", page=page, _external=True)},
        "last": {
            "href": url_for(
                ".list_recipes", page=(recipe_count // per_page) + 1, _external=True
            )
        },
    }
    # Add a 'prev' link if it's not on the first page:
    if page > 1:
        links["prev"] = {
            "href": url_for(".list_recipes", page=page - 1, _external=True)
        }
    # Add a 'next' link if it's not on the last page:
    if page - 1 < recipe_count // per_page:
        links["next"] = {
            "href": url_for(".list_recipes", page=page + 1, _external=True)
        }

    return {
        "recipes": [Recipe(**doc).to_json() for doc in cursor],
        "_links": links,
    }


@app.route("/recipes/", methods=["POST"])
def new_recipe():
    raw_recipe = request.get_json()
    raw_recipe["date_added"] = datetime.utcnow()

    recipe = Recipe(**raw_recipe)
    insert_result = recipes.insert_one(recipe.to_bson())
    recipe.id = PydanticObjectId(str(insert_result.inserted_id))
    print(recipe)

    return recipe.to_json()


@app.route("/recipes/<string:slug>", methods=["GET"])
def get_recipe(slug):
    recipe = recipes.find_one_or_404({"slug": slug})
    return Recipe(**recipe).to_json()


@app.route("/recipes/<string:slug>", methods=["PUT"])
def update_recipe(slug):
    recipe = Recipe(**request.get_json())
    recipe.date_updated = datetime.utcnow()
    updated_doc = recipes.find_one_and_update(
        {"slug": slug},
        {"$set": recipe.to_bson()},
        return_document=ReturnDocument.AFTER,
    )
    if updated_doc:
        return Recipe(**updated_doc).to_json()
    else:
        flask.abort(404, "Recipe not found")


@app.route("/recipes/<string:slug>", methods=["DELETE"])
def delete_recipe(slug):
    deleted_recipe = recipes.find_one_and_delete(
        {"slug": slug},
    )
    if deleted_recipe:
        return Recipe(**deleted_recipe).to_json()
    else:
        flask.abort(404, "Recipe not found")
