"""Resource API blueprint"""

from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__, url_prefix="/api")

api = Api(api_bp)

from .news import NewsArticleList

api.add_resource(NewsArticleList, "/news")
