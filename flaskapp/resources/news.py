"""News article rest resources"""

from flask_restful import Resource, abort, fields, marshal_with, reqparse
from flaskapp.model import NewsArticle, db
from flaskapp.services.mskg import find_candidate_papers

from ..services.news import link_news_candidate

article_fields = {
    "id": fields.Integer(),
    "title": fields.String(),
    "url": fields.String(),
    "hostname": fields.String(),
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
    """News Article content and metadata"""
    @marshal_with(article_fields)
    def get(self, article_id):

        article = NewsArticle.query.get(article_id)

        if article is None:
            abort(404)


        return article

author_fields = {
    "id": fields.Integer(),
    "fullname": fields.String(),
    "institution": fields.String(),
}

paper_fields = {
    "id": fields.Integer(),
    "title": fields.String(),
    "doi": fields.String(),
    "publish_date": fields.DateTime(attribute="pubdate"),
    "authors": fields.Nested(author_fields)
}



class NewsArticleLinksResource(Resource):
    """Resource endpoint for news article/scientific paper links"""

    reqparser = reqparse.RequestParser()
    reqparser.add_argument("candidate_doi", type=str, required=True,
                          help="You must provide DOI to link")

    def post(self, article_id):
        """Create a new link between an article an a scientific paper."""
        args = self.reqparser.parse_args()

        article = NewsArticle.query.get(article_id)

        if article is None:
            abort(404)

        link_news_candidate(article, args.candidate_doi)

    @marshal_with(paper_fields)
    def get(self, article_id):
        """Return a list of papers and their dois linked to this article"""
        article = NewsArticle.query.get(article_id)

        if article is None:
            abort(404)

        return article.papers


class NewsArticleCandidatePapers(Resource):
    """Candidate papers for news articles"""


    def get(self, article_id):

        article = NewsArticle.query.get(article_id)

        if article is None:
            abort(404)

        #find_candidate_papers(article)

        return {"candidate":find_candidate_papers(article)}
