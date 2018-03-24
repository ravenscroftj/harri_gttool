"""News article rest resources"""

import dateutil.parser

from flask_restful import Resource, abort, fields, marshal_with, reqparse
from flaskapp.model import NewsArticle, db
from flaskapp.services.mskg import find_candidate_papers
from flask_security import auth_token_required
from flask_security.core import current_user

from sqlalchemy.sql import select

from ..model import ScientificPaper, ArticlePaper
from ..services.news import link_news_candidate

ROLE_FULL_TEXT_ACCESS = "full_text_access"

article_fields = {
    "id": fields.Integer(),
    "title": fields.String(),
    "url": fields.String(),
    "hostname": fields.String(),
    "content": fields.String(attribute='text'),
    "publish_date": fields.DateTime(),
    "hidden": fields.Boolean(),
    "spam": fields.Boolean()
}

news_envelope = {
    "total_count": fields.Integer(),
    "articles": fields.Nested(article_fields)
}

class NewsArticleListResource(Resource):
    """List news articles stored in tool"""

    @marshal_with(news_envelope)
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('urlfilter', type=str, default="", location='args')
        parser.add_argument('offset', default=0, type=int, location='args')
        parser.add_argument('limit', default=10, type=int, location='args')
        parser.add_argument('hidden', default="false",
                            choices=['true', 'false'],
                            location='args')

        parser.add_argument('spam', default="false",
                            choices=['true', 'false'],
                            location='args')

        parser.add_argument('linked', default="false",
                            choices=['true', 'false'],
                            location='args')

        args = parser.parse_args()

        args.hidden = args.hidden == "true"

        args.spam = args.spam == "true"

        r = NewsArticle.query\
            .filter(NewsArticle.hidden==args.hidden)\
            .filter(NewsArticle.spam==args.spam)

        if args.urlfilter != "":
            r = r.filter(NewsArticle.url.like("%{}%".format(args.urlfilter)))



        if args.linked == "true":
            r = r.filter(NewsArticle.id.in_(select([ArticlePaper.article_id])))
        else:
            r = r.filter(~NewsArticle.id.in_(select([ArticlePaper.article_id])))

        articles = r.offset(args.offset).limit(min(args.limit, 100)).all()

        if not current_user.has_role(ROLE_FULL_TEXT_ACCESS):
            for article in articles:
                article.text = None

        return {"total_count": r.count(), "articles": articles}

class NewsArticleResource(Resource):
    """News Article content and metadata"""
    @marshal_with(article_fields)
    def get(self, article_id):

        article = NewsArticle.query.get(article_id)


        if not current_user.has_role(ROLE_FULL_TEXT_ACCESS):
            article.text = None

        if article is None:
            abort(404)

        return article

    @auth_token_required
    @marshal_with(article_fields)
    def put(self, article_id):

        parser = reqparse.RequestParser()
        parser.add_argument('hidden', default="false", choices=['true','false'])
        parser.add_argument('spam', default="false", choices=['true','false'])
        parser.add_argument('publish_date', default=None)

        args = parser.parse_args()

        article = NewsArticle.query.get(article_id)

        if article is None:
            abort(404)

        if args.publish_date is not None:
            newdate = dateutil.parser.parse(args.publish_date)
            article.publish_date = newdate

        article.spam = args.spam == "true"
        article.hidden = args.hidden == "true"

        db.session.commit()

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


class NewsArticleLinkResource(Resource):

    @auth_token_required
    def delete(self, article_id, paper_id):
        """Remove a link between an article and a scientific paper"""

        article = NewsArticle.query.get(article_id)

        if article is None:
            abort(404)

        for paper in article.papers:
            if paper.id == paper_id:
                article.papers.remove(paper)

        db.session.commit()

        return {"message":"Removed link"}, 201

class NewsArticleLinksResource(Resource):
    """Resource endpoint for news article/scientific paper links"""

    reqparser = reqparse.RequestParser()
    reqparser.add_argument("candidate_doi", type=str, required=True,
                          help="You must provide DOI to link")

    @marshal_with(paper_fields)
    @auth_token_required
    def post(self, article_id):
        """Create a new link between an article an a scientific paper."""
        args = self.reqparser.parse_args()

        article = NewsArticle.query.get(article_id)

        if article is None:
            abort(404)

        return link_news_candidate(article, args.candidate_doi)

    @marshal_with(paper_fields)
    def get(self, article_id):
        """Return a list of papers and their dois linked to this article"""
        article = NewsArticle.query.get(article_id)

        if article is None:
            abort(404)

        return article.papers


class NewsArticleCandidatePapers(Resource):
    """Candidate papers for news articles"""

    reqparser = reqparse.RequestParser()
    reqparser.add_argument("cached", type=str, default="true")

    def get(self, article_id):

        args = self.reqparser.parse_args()

        article = NewsArticle.query.get(article_id)

        if article is None:
            abort(404)

        #find_candidate_papers(article)

        use_cache = args.cached == "true"

        return {"candidate":find_candidate_papers(article, use_cache)}
