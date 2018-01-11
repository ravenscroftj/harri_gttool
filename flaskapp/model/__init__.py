from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import or_, func

db = SQLAlchemy()

from urllib.parse import urlparse


class NewsArticle(db.Model):

    __tablename__ = "articles"

    id = db.Column("article_id", db.Integer, primary_key=True)

    url = db.Column(db.String(255))

    title = db.Column(db.String(255))

    text = db.Column("content", db.Text(collation="utf8_general_ci"))

    publish_date = db.Column(db.DateTime)

    @property
    def hostname(self):
        return urlparse(self.url).hostname

    def people(self, group=False):

        if group:
            q = db.session.query(func.count(Entity.text), Entity.text)\
                .group_by(Entity.text)\
                .filter(Entity.article_id == self.id)\
                .filter(Entity.ent_type == "PERSON")

        else:
            q = Entity.query\
                .filter(Entity.article_id == self.id)\
                .filter(Entity.ent_type == "PERSON")

        return q.all()

    def institutions(self):
        return Entity.query\
            .filter(Entity.article_id == self.id)\
            .filter(Entity.ent_type == "ORG")\
            .filter(or_(Entity.text.like("%university%"),
                        Entity.text.like("%college%")))\
            .all()


paper_authors = db.Table('paper_authors',
                         db.Column('paper_id', db.Integer,
                                   db.ForeignKey('papers.paper_id'),
                                   primary_key=True),
                         db.Column('author_id', db.Integer,
                                   db.ForeignKey('authors.author_id'),
                                   primary_key=True)
                         )


class ScientificPaper(db.Model):
    """Scientific papers as potential matches to articles"""

    __tablename__ = "papers"

    id = db.Column("paper_id", db.Integer, primary_key=True)
    doi = db.Column(db.String(64), unique=True)

    title = db.Column(db.String(255, collation="utf8_general_ci"))

    abstract = db.Column(db.Text(collation="utf8_general_ci"))

    pubdate = db.Column(db.DateTime())

    authors = db.relationship('AcademicAuthor',
                              secondary=paper_authors,
                              backref=db.backref('papers', lazy=True))






class AcademicAuthor(db.Model):
    """Authors of papers"""

    __tablename__ = "authors"

    id = db.Column("author_id", db.Integer, primary_key=True)

    fullname = db.Column("fullname", db.String(255))




class Entity(db.Model):
    """Entity represents a named entity found in a news article"""

    __tablename__ = "entities"

    id = db.Column("entity_id", db.Integer, primary_key=True)

    text = db.Column(db.String(128, collation="utf8_general_ci"))

    ent_type = db.Column('type', db.String(32))

    start = db.Column(db.Integer)

    end = db.Column(db.Integer)

    article_id = db.Column(db.ForeignKey("articles.article_id"))

    article = db.relationship("NewsArticle", backref="entities")
