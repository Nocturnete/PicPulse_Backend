from flask import Blueprint, request, jsonify, session


main_bp = Blueprint("main_bp", __name__)


@main_bp.route("/comunity", methods=["GET"])
def comunity():
    print("COMUNITIY")


@main_bp.route("/iaImprove", methods=["GET"])
def ia_Improve():
    print("IA IMPROVE")


@main_bp.route("/iaColor", methods=["GET"])
def ia_Color():
    print("IA COLOR")


@main_bp.route("/gallery", methods=["GET"])
def gallery():
    print("GALLERY")