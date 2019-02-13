"""News article rest resources"""

import random
import dateutil.parser

from flask import current_app
from flask_restful import Resource, abort, fields, marshal_with, reqparse
from flaskapp.model import NewsArticle, db
from flaskapp.services.mskg import find_candidate_papers
from flask_security import auth_token_required
from flask_security.core import current_user, AnonymousUser

from sqlalchemy.sql import select
from sqlalchemy import func, and_, or_

from ..model import ScientificPaper, ArticlePaper, ROLE_FULL_TEXT_ACCESS
from ..services.news import link_news_candidate

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

        parser.add_argument('review', default="false",
                            choices=['true', 'false'],
                            location='args')

        args = parser.parse_args()

        # use boolean comparisons to convert string "true"/"false" vals into bool type
        args.hidden = args.hidden == "true"

        args.spam = args.spam == "true"

        if current_user.is_authenticated:
            # query for articles that the current user has seen
            userlist = db.session.query(ArticlePaper.article_id)\
                .filter(ArticlePaper.user_id == current_user.id)
        else:
            # query for articles that the current user has seen
            userlist = db.session.query(ArticlePaper.article_id)\
                .filter(ArticlePaper.user_id == None)


        if current_app.config.get('REVIEW_PROCESS_ENABLED', True):
            min_iaa_users = current_app.config.get('REVIEW_MIN_IAA', 3)
            blacklisted_iaa_users = current_app.config.get('REVIEW_USER_BLACKLIST', [])
        else:
            min_iaa_users = 1
            blacklisted_iaa_users = []

        

        # add query for getting articles that have are not passed IAA
        linked = db.session.query(ArticlePaper.article_id)\
            .filter(~ArticlePaper.user_id.in_(blacklisted_iaa_users))\
            .group_by(ArticlePaper.article_id)\
            .having(and_(func.count(ArticlePaper.user_id.distinct()) > 0, 
                         func.count(ArticlePaper.user_id.distinct()) < min_iaa_users))

        # query for articles that have been linked and have passed IAA
        linked_and_reviewed = db.session.query(ArticlePaper.article_id)\
            .group_by(ArticlePaper.article_id)\
            .having(func.count(ArticlePaper.user_id.distinct()) >= min_iaa_users)



        # add select filters for hidden and spam states
        r = NewsArticle.query\
            .filter(NewsArticle.hidden == args.hidden)\
            .filter(NewsArticle.spam == args.spam)

        if args.urlfilter != "":
            r = r.filter(NewsArticle.url.like("%{}%".format(args.urlfilter)))

        # if linked then show all linked articles that the user is allowed to see
        if args.linked == "true":

            r = r.join(ArticlePaper).filter(
                or_(NewsArticle.do_iaa == False,
                and_(NewsArticle.do_iaa == True, NewsArticle.id.in_(linked_and_reviewed.union(userlist)))
                )
            ).distinct(NewsArticle.id)

        # deal with review
        elif args.review == "true":
            # we want articles that have one or more links but that the user hasn't seen
            r = r.filter(NewsArticle.do_iaa == True).filter(NewsArticle.id.in_(linked)).filter(
                ~NewsArticle.id.in_(userlist))

        # default case -show 'new' articles that need to be tagged - news has no ArticlePapers
        else:
            r = r.filter(~NewsArticle.id.in_(
                select([ArticlePaper.article_id])))

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
        parser.add_argument('hidden', default="false",
                            choices=['true', 'false'])
        parser.add_argument('spam', default="false", choices=['true', 'false'])
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

        q = ArticlePaper.query\
            .filter(ArticlePaper.article_id==article_id, 
                    ArticlePaper.paper_id==paper_id, ArticlePaper.user_id == current_user.id)

        if q.count() < 1:
            abort(404)
        
        link = q.first()

        #remove the link from paper and article
        db.session.delete(link)

        db.session.commit()

        return {"message": "Removed link"}, 201


class NewsArticleLinksResource(Resource):
    """Resource endpoint for news article/scientific paper links"""

    reqparser = reqparse.RequestParser()
    reqparser.add_argument("candidate_doi", type=str, required=True,
                           help="You must provide DOI to link")
    reqparser.add_argument('annotation_time', type=int, required=True, 
                            help="You must say how long the annotation took in milliseconds")

    @marshal_with(paper_fields)
    @auth_token_required
    def post(self, article_id):
        """Create a new link between an article an a scientific paper."""
        args = self.reqparser.parse_args()

        article = NewsArticle.query.get(article_id)

        # there's a random chance that we make the news article an IAA article
        

        if random.randint(0,100) < 10:
            article.do_iaa = True

        if article is None:
            abort(404)

        return link_news_candidate(article, args.candidate_doi, args.annotation_time)

    @marshal_with(paper_fields)
    def get(self, article_id):
        """Return a list of papers and their dois linked to this article"""
        article = NewsArticle.query.get(article_id)
        # if the article isn't valid then fail
        if article is None:
            abort(404)

        papers = ScientificPaper.query.join(ArticlePaper)\
            .filter( ArticlePaper.article_id == article_id)
        
        if current_app.config.get('REVIEW_PROCESS_ENABLED', True):
            min_iaa_users = current_app.config.get('REVIEW_MIN_IAA', 3)
        else:
            min_iaa_users = 1

        # check that the links were created by the current user
        if current_user.is_authenticated:
            papers = papers.filter(ArticlePaper.user_id == current_user.id)
        else:
            papers = papers.filter(ArticlePaper.user_id == None)

        # union results with links that have more than annotations
        linked_iaa = db.session.query(ArticlePaper.paper_id)\
            .filter(ArticlePaper.article_id == article_id)\
            .group_by(ArticlePaper.article_id, ArticlePaper.paper_id)\
            .having(func.count(ArticlePaper.article_id)>=min_iaa_users)

        papers = papers.union(ScientificPaper.query.filter(ScientificPaper.id.in_(linked_iaa)))

        # finally return the papers
        papers = papers.all()

        return papers


class NewsArticleCandidatePapers(Resource):
    """Candidate papers for news articles"""

    reqparser = reqparse.RequestParser()
    reqparser.add_argument("cached", type=str, default="true")

    def get(self, article_id):

        args = self.reqparser.parse_args()

        article = NewsArticle.query.get(article_id)

        if article is None:
            abort(404)

        # find_candidate_papers(article)

        use_cache = args.cached == "true"

        return {"candidate": find_candidate_papers(article, use_cache)}
