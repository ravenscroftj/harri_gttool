"""Tooling for automatically filtering spam articles (e.g. celebrity)"""

import pickle

from flask_restful import Resource, abort, fields, marshal_with, reqparse
from flaskapp.model import NewsArticle, db

article_fields = {
    "id": fields.Integer(),
    "title": fields.String(),
    "url": fields.String(),
    "hostname": fields.String(),
    "content": fields.String(attribute='text'),
    "publish_date": fields.DateTime(),
    "hidden": fields.Boolean()
}


class SpamFilterResource(Resource):
    """List news articles stored in tool"""

    def _score_articles(self, articles):
        """Given an array of articles, score them for spam/ham"""

        pipeline = pickle.load(open("spam_classifier.pickle","rb"))

        y_pred = pipeline.predict_proba([a.text for a in articles])

        labelled_pred = [
            {lbl: score for lbl,score in zip(pipeline.classes_, result)} for
                result in y_pred
        ]

        return labelled_pred

    def _load_articles(self):
        """Load articles based on IDs passed in as get params."""
        parser = reqparse.RequestParser()

        parser.add_argument('articles', action='store', required=True,
                            location='args')

        args = parser.parse_args()

        article_ids = args.articles.split(",")

        for id in article_ids:
            if not id.isnumeric():
                abort(400, message="{} is not a valid article ID".format(id))

        articles = NewsArticle.query\
        .filter(NewsArticle.id.in_(article_ids))\
        .limit(100)\
        .all()

        return articles


    def get(self):
        """Preview spam filter but don't apply"""

        articles = self._load_articles()
        labelled_pred = self._score_articles(articles)

        results = [{
            "id" : article.id,
            "title": article.title,
            "scores":pred,
            "spam": article.spam,
        } for article, pred in zip(articles, labelled_pred)]


        return results

    def post(self):
        """Apply spam filters"""

        articles = self._load_articles()
        labelled_pred = self._score_articles(articles)

        results = [{
            "id" : article.id,
            "title": article.title,
            "scores":pred,
        } for article, pred in zip(articles, labelled_pred)]


        spamlist = [article['id'] for article in results
                    if article['scores']['spam'] > 0.6]

        NewsArticle.query.filter(NewsArticle.id.in_(spamlist))\
                .update({NewsArticle.spam: True},
                        synchronize_session=False)

        db.session.commit()

        return spamlist
