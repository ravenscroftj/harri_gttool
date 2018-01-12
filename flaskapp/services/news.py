from datetime import datetime

import spacy

from flaskapp.model import Entity, NewsArticle, db, ScientificPaper, AcademicAuthor

from .mskg import find_candidate_papers

_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load('en')

    return _nlp

class NoSuchCandidateException(Exception):
    """Exception class that handles a lack of paper candidate"""
    pass

def list_unpaired_news():
    """Find news articles that do not have a scientific paper pairing"""


def generate_paper_from_mskg(candidate, doi):
    """Given an MSKG json, create ScientificPaper record and Authors"""

    paper = ScientificPaper(title=candidate['Ti'],
                            pubdate=datetime.strptime(candidate['D'],
                                                      "%Y-%m-%d"),
                            doi=doi)

    db.session.add(paper)

    for author in candidate['AA']:

        name = author['AuN']
        inst = author['AfN']

        arec = AcademicAuthor.query\
            .filter(AcademicAuthor.fullname == name)\
            .filter(AcademicAuthor.institution == inst).first()

        if arec is None:
            arec = AcademicAuthor(fullname=name, institution=inst)
            db.session.add(arec)

        paper.authors.append(arec)

    db.session.commit()

    return paper



def link_news_candidate(article, doi):
    """Link an article to a given doi"""

    # check to see if paper already in db
    paper = ScientificPaper.query.filter(ScientificPaper.doi == doi).first()

    if paper is None:
        # if no paper was found we need to create one

        candidate_result = find_candidate_papers(article)

        found_match = False
        for cdoi, candidate in candidate_result['doi2paper'].items():

            if cdoi == doi:
                paper = generate_paper_from_mskg(candidate, cdoi)
                found_match = True
                break

        # if we got to end of for loop without finding doi, throw error
        if not found_match:
            raise NoSuchCandidateException("Could not find candidate with doi={}".format(doi))

    # now we create the link
    article.papers.append(paper)

    db.session.commit()

    return paper


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
