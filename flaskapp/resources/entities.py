"""Entity rest resources"""

from flask_restful import Resource, reqparse, marshal_with, fields, reqparse, marshal
from flaskapp.model import db, NewsArticle, Entity

from flaskapp.services.mskg import find_ent_frequencies

from collections import defaultdict

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
        ap.add_argument("grouped", type=str, default="false")

        args = ap.parse_args()

        args.grouped = args.grouped == "true"

        people = article.people()

        ptext = defaultdict(lambda:[])
        ptext.update({person.text.strip():[(person.start,person.end)] for person in people if person.text.strip() != ""})

        _,pfreq = find_ent_frequencies(defaultdict(lambda:[]), ptext)

        if args.grouped:
            return [{"text": key, "count":value} for key,value in pfreq.items()]
        elif len(people) > 0 and type(people[0]) is Entity:
            return marshal(people, entity_fields)
        else:
            return { ent:count for ent,count in people}



class InstitutionListResource(Resource):
    """List unis mentioned in news articles"""

    @marshal_with(entity_fields)
    def get(self, article_id):
        article = NewsArticle.query.get(article_id)

        return article.institutions()
