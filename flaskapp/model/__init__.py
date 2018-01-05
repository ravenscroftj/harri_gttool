from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class NewsArticle(db.Model):

    __tablename__ = "articles"

    id = db.Column("article_id", db.Integer, primary_key=True)

    url = db.Column(db.String(255))

    title = db.Column(db.String(255))

    text = db.Column("content", db.Text(collation="utf8_general_ci") )



class Entity(db.Model):

    __tablename__ = "entities"

    id = db.Column("entity_id", db.Integer, primary_key=True)

    text = db.Column(db.String(128, collation="utf8_general_ci"))

    ent_type = db.Column('type', db.String(32))

    start = db.Column(db.Integer)

    end = db.Column(db.Integer)

    article_id = db.Column(db.ForeignKey("articles.article_id"))

    article = db.relationship("NewsArticle", backref="entities")
