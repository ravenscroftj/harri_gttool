"""Entity rest resources"""

from flask_restful import Resource, reqparse, marshal_with, fields
from flaskapp.model import db, NewsArticle


entity_fields = {
    "id": fields.Integer(),
    "text": fields.String(),
    "type": fields.String(attribute="ent_type"),
    "start": fields.Integer(),
    "end": fields.Integer()
}

class PersonListResource(Resource):
    """List people mentioned in news articles"""

    @marshal_with(entity_fields)
    def get(self, article_id):
        article = NewsArticle.query.get(article_id)

        print(article.title, article.people())

        return article.people()


class InstitutionListResource(Resource):
    """List unis mentioned in news articles"""

    @marshal_with(entity_fields)
    def get(self, article_id):
        article = NewsArticle.query.get(article_id)

        return article.institutions()
