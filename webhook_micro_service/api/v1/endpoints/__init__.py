#!/usr/bin/python3
""" Blueprint for API """
from flask import Blueprint
app_views = Blueprint('app_views', __name__, url_prefix='/api/v1')
from api.v1.endpoints.enterprise.enterprise import *
from api.v1.endpoints.enterprise.login import *





