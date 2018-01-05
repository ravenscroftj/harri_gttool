"""News article rest resources"""

from flask_restful import Resource, reqparse, marshal_with, fields, abort
from flaskapp.model import db, NewsArticle

from flaskapp.services.mskg import find_candidate_papers

article_fields = {
    "id": fields.Integer(),
    "title": fields.String(),
    "content": fields.String(attribute='text'),
    "publish_date": fields.DateTime()
}

class NewsArticleListResource(Resource):
    """List news articles stored in tool"""

    @marshal_with(article_fields)
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('offset', default=0, type=int, location='args')
        parser.add_argument('limit', default=10, type=int, location='args')

        args = parser.parse_args()

        r = NewsArticle.query.offset(args.offset).limit(min(args.limit,100))


        return r.all()

class NewsArticleResource(Resource):

    @marshal_with(article_fields)
    def get(self, article_id):

        article = NewsArticle.query.get(article_id)

        if article is None:
            abort(404)


        return article

class NewsArticleCandidatePapers(Resource):
    """Candidate papers for news articles"""


    def get(self, article_id):

        article = NewsArticle.query.get(article_id)

        if article is None:
            abort(404)

        #find_candidate_papers(article)

        return {"candidate":find_candidate_papers(article)}
