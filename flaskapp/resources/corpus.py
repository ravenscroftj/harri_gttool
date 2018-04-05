"""Corpus download resources"""

from flask_restful import Resource, reqparse, marshal_with, fields, reqparse, marshal
from flaskapp.model import db, ArticlePaper, NewsArticle, ScientificPaper, ROLE_FULL_TEXT_ACCESS
from flask_security.core import current_user

from flaskapp.services.mskg import find_ent_frequencies

from collections import defaultdict




link_fields = {
    "doi": fields.String(attribute="paper.doi"),
    "title": fields.String(attribute="paper.title"),
    "user_id": fields.Integer(attribute="user_id")
}

article_fields = {
    "id": fields.Integer(),
    "title": fields.String(),
    "url": fields.String(),
    "hostname": fields.String(),
    "content": fields.String(attribute='text'),
    "publish_date": fields.DateTime(),
    "links": fields.Nested(link_fields)
}

corpus_fields = {
    "total_count": fields.Integer(),
    "links": fields.Nested(article_fields)
}

class CorpusResource(Resource):

    @marshal_with(corpus_fields)
    def get(self):
        """Download a corpus of linked news and science"""


        parser = reqparse.RequestParser()
        parser.add_argument('offset', default=0, type=int, location='args')
        parser.add_argument('limit', default=10, type=int, location='args')


        args = parser.parse_args()

        q = NewsArticle.query.join(ArticlePaper).filter(NewsArticle.hidden==False, NewsArticle.spam==False).distinct(NewsArticle.id)

        articles = q.limit(args.limit).offset(args.offset).all()

        if not current_user.has_role(ROLE_FULL_TEXT_ACCESS):
            for article in articles:
                article.text = None
    
        return {
            "total_count": q.count(),
            "links": articles
        }
