# -*- coding: utf-8 -*-
from flask import Blueprint
from app import derive_import_root, add_url_rules_for_blueprint

bp = Blueprint(__name__.split('.')[-1], __name__)
root = derive_import_root(__name__)
add_url_rules_for_blueprint(root, bp)
