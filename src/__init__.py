import os
from datetime import timedelta

from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
import validators
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from bson.objectid import ObjectId

from src.constants.http_status_codes import *


app = Flask(__name__, instance_relative_config=True)

CORS(app, resources={r"/*": {"origins": "*"}})

mongo = MongoClient(host="localhost", port=27017)
db = mongo[os.environ.get("DB_NAME")]

jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=60)


client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
users_collection = db["users"]
templates_collection = db["templates"]


@app.route("/api/v1/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        email = data["email"]
        password = data["password"]

        if not validators.email(email):
            return (
                jsonify({"msg": "Error", "data": None, "error": "Email is not valid"}),
                HTTP_400_BAD_REQUEST,
            )

        data["password"] = generate_password_hash(password)

        user = users_collection.find_one({"email": email})
        if not user:
            user_data = {
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "email": email,
                "password": data["password"],
            }
            users_collection.insert_one(user_data)
            return (
                jsonify(
                    {
                        "msg": "User created successfully",
                        "data": None,
                        "error": None,
                    }
                ),
                HTTP_201_CREATED,
            )
        else:
            return (
                jsonify(
                    {
                        "msg": "Error",
                        "data": None,
                        "error": "Username already exists",
                    }
                ),
                HTTP_409_CONFLICT,
            )
    except Exception as err:
        print(f"\n_________________Error: {err}_________________\n")
        return (
            jsonify({"msg": "Error", "data": None, "error": "Something went wrong"}),
            HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data["email"]
        password = data["password"]

        user = users_collection.find_one({"email": email})

        if user:
            check_password = check_password_hash(user["password"], password)

            if check_password:
                access_token = create_access_token(identity=str(user["_id"]))
                refresh_token = create_refresh_token(identity=str(user["_id"]))

            return (
                jsonify(
                    {
                        "msg": "Login successful",
                        "data": {
                            "email": email,
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                        },
                        "error": None,
                    }
                ),
                HTTP_200_OK,
            )

        return (
            jsonify({"msg": "Error", "data": None, "error": "Invalid credentials"}),
            HTTP_401_UNAUTHORIZED,
        )

    except Exception as err:
        print(f"\n_________________Error: {err}_________________\n")
        return (
            jsonify({"msg": "Error", "data": None, "error": "Something went wrong"}),
            HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.route("/api/v1/auth/token/refresh", methods=["GET"])
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)

    return jsonify({"access_token": access_token}), HTTP_200_OK


@app.route("/api/v1/template", methods=["POST"])
@jwt_required()
def insert_template():
    try:
        data = request.get_json()
        template_data = {
            "user_id": get_jwt_identity(),
            "template_name": data["template_name"],
            "subject": data["subject"],
            "body": data["body"],
        }
        templates_collection.insert_one(template_data)
        return (
            jsonify(
                {
                    "msg": "Template stored successfully",
                    "data": None,
                    "error": None,
                }
            ),
            HTTP_201_CREATED,
        )
    except Exception as err:
        print(f"\n_________________Error: {err}_________________\n")
        return (
            jsonify({"msg": "Error", "data": None, "error": "Something went wrong"}),
            HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.route("/api/v1/template", methods=["GET"])
@jwt_required()
def get_all_templates():
    try:
        templates = list(templates_collection.find({"user_id": get_jwt_identity()}))
        for template in templates:
            template["_id"] = str(template["_id"])
            del template["user_id"]
        return (
            jsonify(
                {
                    "msg": "Templates fetched successfully",
                    "data": templates,
                    "error": None,
                }
            ),
            HTTP_200_OK,
        )
    except Exception as err:
        print(f"\n_________________Error: {err}_________________\n")
        return (
            jsonify({"msg": "Error", "data": None, "error": "Something went wrong"}),
            HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.route("/api/v1/template/<id>", methods=["GET"])
@jwt_required()
def get_template(id):
    try:
        data = templates_collection.find_one(
            {"_id": ObjectId(id), "user_id": get_jwt_identity()}
        )
        data["_id"] = str(data["_id"])
        if data:
            return (
                jsonify(
                    {
                        "msg": "Template fetched successfully",
                        "data": data,
                        "error": None,
                    }
                ),
                HTTP_200_OK,
            )
        return (
            jsonify({"msg": "Error", "data": None, "error": "Invalid Template Id"}),
            HTTP_404_NOT_FOUND,
        )

    except Exception as err:
        print(f"\n_________________Error: {err}_________________\n")
        return (
            jsonify({"msg": "Error", "data": None, "error": "Something went wrong"}),
            HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.route("/api/v1/template/<id>", methods=["PUT"])
@jwt_required()
def update_template(id):
    data = request.get_json()
    template_data = {
        "template_name": data["template_name"],
        "subject": data["subject"],
        "body": data["body"],
    }
    try:
        template = templates_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": template_data}
        )
        if template.modified_count == 1:
            return (
                jsonify(
                    {
                        "msg": "Template updated successfully",
                        "data": None,
                        "error": None,
                    }
                ),
                HTTP_200_OK,
            )
        return (
            jsonify(
                {
                    "msg": "Nothing to update",
                    "data": None,
                    "error": None,
                }
            ),
            HTTP_200_OK,
        )
    except Exception as err:
        print(f"\n_________________Error: {err}_________________\n")
        return (
            jsonify(
                {
                    "msg": "Template not found",
                    "data": None,
                    "error": None,
                }
            ),
            HTTP_404_NOT_FOUND,
        )


@app.route("/api/v1/template/<id>", methods=["DELETE"])
@jwt_required()
def delete_template(id):
    try:
        check_template = templates_collection.find_one(
            {"_id": ObjectId(id), "user_id": get_jwt_identity()}
        )
        if check_template:
            template = templates_collection.delete_one({"_id": ObjectId(id)})
            if template.deleted_count == 1:
                return (
                    jsonify(
                        {
                            "msg": "Template deleted successfully",
                            "data": None,
                            "error": None,
                        }
                    ),
                    HTTP_204_NO_CONTENT,
                )
        return (
            jsonify(
                {
                    "msg": "Template not found",
                    "data": None,
                    "error": None,
                }
            ),
            HTTP_404_NOT_FOUND,
        )
    except Exception as err:
        print(f"\n_________________Error: {err}_________________\n")
        return (
            jsonify({"msg": "Error", "data": None, "error": "Something went wrong"}),
            HTTP_500_INTERNAL_SERVER_ERROR,
        )
