import ujson
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

    news = {k:news_json[k] for k in ['title','text','url']}

    news['text'] = news['text'].replace("\\xE2\\x97\\x8F","")

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
