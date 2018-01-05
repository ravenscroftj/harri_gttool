"""News article rest resources"""

from flask_restful import Resource, reqparse, marshal_with, fields
from flaskapp.model import db, NewsArticle

article_fields = {
    "id": fields.Integer(),
    "title": fields.String(),
    "content": fields.String(attribute='text')
}

class NewsArticleList(Resource):
    """List news articles stored in tool"""

    @marshal_with(article_fields)
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('offset', default=0, type=int, location='args')
        parser.add_argument('limit', default=10, type=int, location='args')

        args = parser.parse_args()

        r = NewsArticle.query.offset(args.offset).limit(min(args.limit,100))


        return r.all()
