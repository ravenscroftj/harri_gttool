"""Entity rest resources"""

from flask_restful import Resource, reqparse, marshal_with, fields, reqparse, marshal
from flaskapp.model import db, NewsArticle, Entity


entity_fields = {
    "id": fields.Integer(),
    "text": fields.String(),
    "type": fields.String(attribute="ent_type"),
    "start": fields.Integer(),
    "end": fields.Integer()
}

class PersonListResource(Resource):
    """List people mentioned in news articles"""

    def get(self, article_id):
        article = NewsArticle.query.get(article_id)

        ap = reqparse.RequestParser()
        ap.add_argument("grouped", type=bool, default=False)

        args = ap.parse_args()

        people = article.people()

        if type(people[0]) is Entity:
            return marshal(people, entity_fields)
        else:
            return { ent:count for ent,count in people}



class InstitutionListResource(Resource):
    """List unis mentioned in news articles"""

    @marshal_with(entity_fields)
    def get(self, article_id):
        article = NewsArticle.query.get(article_id)

        return article.institutions()
