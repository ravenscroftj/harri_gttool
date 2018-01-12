"""Resource API blueprint"""

from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__, url_prefix="/api")

api = Api(api_bp)

from .news import NewsArticleListResource,\
 NewsArticleCandidatePapers,\
 NewsArticleResource,\
 NewsArticleLinksResource,\
 NewsArticleLinkResource

from .entities import PersonListResource, InstitutionListResource

api.add_resource(NewsArticleListResource, "/news", "/news/")
api.add_resource(NewsArticleResource, "/news/<string:article_id>")
api.add_resource(PersonListResource, "/news/<string:article_id>/people")
api.add_resource(InstitutionListResource, "/news/<string:article_id>/institutions")
api.add_resource(NewsArticleCandidatePapers, "/news/<string:article_id>/candidates")
api.add_resource(NewsArticleLinksResource, "/news/<string:article_id>/links")
api.add_resource(NewsArticleLinkResource, "/news/<int:article_id>/links/<int:paper_id>")
