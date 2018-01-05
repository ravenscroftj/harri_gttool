from datetime import datetime
import spacy
from flaskapp.model import db, NewsArticle, Entity

_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load('en')

    return _nlp


def list_unpaired_news():
    """Find news articles that do not have a scientific paper pairing"""


def import_news_json(news_json):
    """Import news from JSON into database"""
    nlp = get_nlp()

    if(NewsArticle.query
       .filter(NewsArticle.url == news_json['url'])
       .count() > 0):
        print("Skipping article - already exists")
        return

    if len(news_json['url']) > 254:
        print("URL too long")
        return

    # parse date

    news = {k:news_json[k] for k in ['title','text','url']}

    if news_json['publish_date'] != None:
        news['publish_date'] = datetime.strptime(news_json['publish_date'],
                                             "%Y/%m/%d %H:%M:%S")


    article = NewsArticle(**news)
    db.session.add(article)

    doc = nlp(article.text)


    for ent in doc.ents:
        if len(ent.text) > 128:
            continue
        article.entities.append(Entity(text=ent.text,
                        ent_type=ent.label_,
                        start=ent.start,
                        end=ent.end))

    db.session.commit()
