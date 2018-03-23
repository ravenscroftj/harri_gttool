from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import or_, func

from urllib.parse import urlparse

from flask_security import UserMixin, RoleMixin


db = SQLAlchemy()

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    full_name = db.Column(db.String(255))
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


# pivot table definitions

paper_authors = db.Table('paper_authors',
                         db.Column('paper_id', db.Integer,
                                   db.ForeignKey('papers.paper_id'),
                                   primary_key=True),
                         db.Column('author_id', db.Integer,
                                   db.ForeignKey('authors.author_id'),
                                   primary_key=True)
                         )

class ArticlePaper(db.Model):

    __tablename__ = "article_papers"

    article_id = db.Column('article_id', db.Integer, db.ForeignKey('articles.article_id'),  primary_key=True)

    paper_id = db.Column('paper_id', db.Integer, db.ForeignKey('papers.paper_id'), primary_key=True)

    user_id = db.Column('user_id', db.Integer, 
        db.ForeignKey('user.id'), nullable=True)

    article = db.relationship('NewsArticle', 
        backref=db.backref('links', lazy=True))

    paper = db.relationship('ScientificPaper', 
        backref=db.backref('links', lazy=True))

    user = db.relationship('User')
                            


class NewsArticle(db.Model):

    __tablename__ = "articles"

    id = db.Column("article_id", db.Integer, primary_key=True)

    url = db.Column(db.String(255))

    hostname = db.Column(db.String(255))

    title = db.Column(db.String(255))

    text = db.Column("content", db.Text(collation="utf8_general_ci"))

    publish_date = db.Column(db.DateTime)

    papers = db.relationship('ScientificPaper',
                             secondary=ArticlePaper.__table__,
                             backref=db.backref('articles', lazy=True))

    hidden = db.Column("hidden", db.Boolean, server_default='0')

    spam = db.Column("spam", db.Boolean, server_default='0')

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

    institution = db.Column("Institution", db.String(255))


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
