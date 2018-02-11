"""Service for calling microsoft knowledge graph"""

import os
import math
import requests
import hashlib
import ujson as json

from flask import current_app
from datetime import datetime, timedelta

from flaskapp.model import NewsArticle
from collections import defaultdict
from fuzzywuzzy import fuzz




def score_results(all_paper_results, date, people_freq, inst_freq):

    seconds_in_day = 86400

    people_count = sum(people_freq.values())
    inst_count = sum(inst_freq.values())
    doi_paper = defaultdict(lambda: 1)

    doi2paper = {}

    for ent in all_paper_results:

        #print(ent['Ti'], ent['D'])

        if type(ent['E']) is str:
            E = json.loads(ent['E'])
        else:
            E = ent['E']

        pdate = datetime.strptime(ent['D'], "%Y-%m-%d")

        td = math.sqrt((pdate.timestamp()-date.timestamp())**2) / seconds_in_day

        # if there is no time difference then reward result
        if td == 0:
            td = 0.1

        doi = ""

        if 'DOI' in E:
            doi = E['DOI']
        elif 'Ti' in ent:
            hash = hashlib.new('sha256')
            hash.update(ent['Ti'].encode('utf8'))
            doi = hash.hexdigest()
        else:
            print(E)

        if doi in doi2paper:
            doi2paper[doi]['_source'] += "," + ent['_source']
        else:
            doi2paper[doi] = ent

        for author in ent['AA']:

            best_match_name = max([ (fuzz.ratio(author['AuN'],person.lower().strip()) ** 2 *count) for
                             person,count in people_freq.items()] + [0])

            if 'AfN' in author:
                best_match_inst = max([ (fuzz.ratio(author['AfN'],inst.lower().strip()) **2 * count) for
                                 inst,count in inst_freq.items()] + [0])
            else:
                best_match_inst = 0

            #print(author['AuN'], best_match_name/people_count, best_match_inst/inst_count)

            if(people_count) == 0:
                people_count = 0.01

            if(inst_count) == 0:
                inst_count = 0.01

            score = (best_match_name/people_count)+(best_match_inst/inst_count) / td

            doi_paper[doi] += score

        if len(ent['AA']) > 0:
            doi_paper[doi] /= len(ent['AA'])

    return doi2paper, doi_paper


def generate_date_constraint(date, days=60):
    """Generate date constraint for mskg. Only allow papers within X days."""
    DATE_OUT_FMT = "%Y-%m-%d"
    lower = date - timedelta(days=days)
    upper = date + timedelta(days=days)
    return "['{}','{}']".format(lower.strftime(DATE_OUT_FMT),
                                upper.strftime(DATE_OUT_FMT))


def generate_person_affil_constraint(person=None, inst=None):
    """Generate Microsoft knowledge graph person/affiliation constraint"""

    if inst is None:
        return "Composite(AA.AuN='{author}')".format(author=person.lower().strip())
    elif person is None:
        return "Composite(AA.AfN='{inst}')".format(inst=inst.lower().strip())
    else:
        return "Composite(AA.AuN='{author}'),Composite(AA.AfN='{inst}')".format(
            author=person.lower().strip(),
            inst=inst.lower().strip()
        )

def find_ent_frequencies(insts, people):

    ents = sorted(list(insts.keys()) + list(people.keys()),
                  key=lambda x: len(x),
                  reverse=True)

    for ent in ents:

        # if the ent contains apostrophe s ('s) skip for now
        if ent.lower().endswith("'s"):
            continue

        for e2 in ents:

            if e2 == ent:
                continue

            if e2.lower().strip() in ent.lower().strip():

                #print(ent, e2)
                if e2 in insts:
                    from_array = insts
                else:
                    from_array = people


                if ent in insts:
                    to_array = insts
                else:
                    to_array = people

                to_array[ent].extend(from_array[e2])
                del from_array[e2]

    inst_freq = {key: len(val) for key, val in insts.items()}
    people_freq = {key: len(val) for key, val in people.items()}

    for freqdict in [people_freq, inst_freq]:

        rename_jobs = []

        for ent in freqdict:

            if ent.lower().endswith("'s"):
                rename_jobs.append(ent)

        for ent in rename_jobs:
            freqdict[ent[:-2]] = freqdict[ent]
            del freqdict[ent]

    return inst_freq, people_freq





def get_papers_for_query(q):
    """Execute knowledge graph query and return json"""

    headers = {
        'Ocp-Apim-Subscription-Key': current_app.config['MSAKG_KEY']
    }

    params = {
        "expr": q,
        "attributes": "Ti,J.JN,Y,D,CIN,CC,AA.AuN,AA.AfN,AA.AuId,W,E"
    }

    endpoint = "https://westus.api.cognitive.microsoft.com/academic/v1.0/evaluate"
    #endpoint = "https://westus.api.cognitive.microsoft.com/academic/v1.0/interpret"

    result = requests.post(endpoint, headers=headers, data=params)

    print(result.json())

    return result



def results_for_person_inst_date(query):

    person, inst, date = query

    print(inst, person)

    results = []

    q = "AND({person},D={daterange})"

    res = get_papers_for_query(q.format(person=generate_person_affil_constraint(person,inst),
               daterange=generate_date_constraint(date)))


    if 'entities' in res.json():
        ents = res.json()['entities']

        for ent in ents:
            ent['_source'] = "mskg"
            ent['_query_author'] = person
            ent['_query_inst'] = inst

        if len(ents) > 0:
            results.extend(ents)

    #get springer results too
    results.extend(get_springer_results(person, date))

    #get scopus results too
    results.extend(get_scopus_results(person, inst, date))

    # get crossref results too
    #ents = get_crossref_results(person, date)


    return results


def get_scopus_results(author, inst, pubdate):
    """Query function for getting scopus api results"""

    results = []

    if author != None:
        names = author.split(" ")

        lastname = names[-1]
        initial = names[0][0]



        query = "AUTHOR-NAME({name}) YEAR({year}) AFFIL({affil})"\
            .format(year=pubdate.strftime("%Y"),
                    name=lastname + "," + initial,
                    affil=inst)



        params={
                "apiKey": current_app.config['SCOPUS_API_KEY'],
                "query": query
               }

        r = requests.get("https://api.elsevier.com/content/search/scopus",
                         params=params)

        print(r.json())


        if 'search-results' not in r.json():
            return []




        for item in r.json()['search-results']['entry']:

            ent = {}
            if 'error' in item and item['error'] == "Result set was empty":
                continue

            ent['Ti'] = item['dc:title']
            ent['D'] = item['prism:coverDate']

            if 'prism:publicationName' in item:
                ent['J'] = {"JN": item['prism:publicationName']}

            if 'prism:doi' in item:
                ent['E'] = {'DOI':item['prism:doi']}
            else:
                ent['E'] = {}


            #ent['AA'] = [{"AuN":item['dc:creator'],
            #              "AfN": item['affiliation'][0]['affilname'] if 'affiliation' in item else ""
            #              }]


            # author information must be extracted with a new API call

            for link in  item['link']:
                if link['@ref'] == "author-affiliation":
                    authorlink = link['@href']
                    break

            author_affil_url = "{}&apiKey={}".format( authorlink,
                current_app.config['SCOPUS_API_KEY']
                )

            adata = requests.get(author_affil_url,
                             headers={"Accept":"application/json"}).json()

            authors = adata['abstracts-retrieval-response']['authors']['author']

            amap = {a['@id']: a for a in
                    adata['abstracts-retrieval-response']['affiliation']}

            ent['AA'] = []
            for author in authors:

                # affiliation of author may not be defined
                if 'affiliation' in author:
                    # if affilaition is defined it could be a list (many affil)
                    if type(author['affiliation']) is list:
                        aid = author['affiliation'][0]['@id']
                    else:
                        aid = author['affiliation']['@id']

                    affilname = amap[aid]['affilname']
                else:
                    #if affiliation not defined, leave blank
                    affilname = ""

                ent['AA'].append({"AuN": author['ce:indexed-name'],
                                  "AfN": affilname})


            ent['_source'] = "scopus"
            ent['_query_author'] = author
            ent['_query_inst'] = inst
            results.append(ent)


    return results




def get_springer_results(author, pubdate):
    """Query function for getting springer api results"""

    query = "year: {year} AND name:\"{name}\"".format(year=pubdate.strftime("%Y"),
                                                  name=author)

    params={
            "api_key": current_app.config['SPRINGER_API_KEY'],
            "q": query
           }

    r = requests.get("http://api.springer.com/metadata/json",params=params)

    results = []
    for item in r.json()['records']:

        ent = {}

        ent['Ti'] = item['title']
        ent['D'] = item['publicationDate']
        ent['E'] = {'DOI':item['doi']}

        ent['AA'] = []
        for author in item['creators']:
            aa = {}
            aa['AuN'] = author['creator'].lower()
            ent['AA'].append(aa)

        ent['_source'] = "springer"
        ent['_query_author'] = author
        results.append(ent)


    return results


def get_crossref_results(author, pubdate):

    DATE_OUT_FMT = "%Y"
    lower=pubdate - timedelta(days=0)
    upper=pubdate + timedelta(days=354)

    filter_text = "from-pub-date:{},until-pub-date:{}".format(lower.strftime(DATE_OUT_FMT),
                                upper.strftime(DATE_OUT_FMT))


    params={
            "query.author": author,
            "filter": filter_text
           }

    r = requests.get("https://api.crossref.org/works", params=params)

    results = []
    for item in r.json()['message']['items']:

        ent = {}

        if 'title' in item:

            ent['Ti'] = item['title'][0]

            if 'published-online' in item:
                dparts = item['published-online']['date-parts'][0]

            elif 'published-print' in item:
                dparts = item['published-print']['date-parts'][0]

            # if we don't know the date we can't use the paper
            if len(dparts) < 1:
                continue


            if len(dparts) < 3:
                dparts.append(1)

            try:
                ent['D'] = "{0:04d}-{1:02d}-{2:02d}".format(*dparts)
            except:
                ent['D']="1970-01-01"

            ent['E'] = {'DOI':item['DOI']}
            ent['AA'] = []
            for author in item['author']:
                aa = {}
                if 'given' in author and 'family' in author:
                    aa['AuN'] = "{given} {family}".format(**author).lower()

                    for affiliation in author['affiliation'][:1]:
                        aa['AfN'] = affiliation['name'].lower()

                    ent['AA'].append(aa)

            results.append(ent)

    return results


def normalize_insts(insts):

    normalized = {}

    for inst, props in insts.items():

        if inst.strip().lower().startswith("the"):
            inst = inst[4:]

        normalized[inst] = props

    return normalized


def find_candidate_papers(news_article, use_cache=True):
    """Find candidate scientific paper matches for given news article"""

    cachedir = current_app.config['CACHE_DIR']
    candidate_cache = os.path.join(cachedir, "candidates")

    if not os.path.exists(candidate_cache):
        os.makedirs(candidate_cache)

    cache_file = os.path.join(candidate_cache,
                              "{}.json".format(news_article.id))

    if os.path.exists(cache_file) and use_cache:
        with open(cache_file) as f:
            return json.load(f)

    # find people and institutions
    people = defaultdict(lambda: [])
    insts = defaultdict(lambda: [])

    for person in news_article.people():
        people[person.text].append((person.start, person.end))

    for inst in news_article.institutions():
        insts[inst.text].append((inst.start, inst.end))


    insts = normalize_insts(insts)

    inst_freq, people_freq = find_ent_frequencies(insts, people)

    top_people = sorted(people_freq, key=lambda x: people_freq[x], reverse=True)
    top_insts = sorted(inst_freq, key=lambda x: inst_freq[x], reverse=True)

    all_paper_results = []
    query_combos = []

    if len(top_insts) < 1:
        top_insts.append(None)

    if len(top_people) < 1:
        top_people.append(None)

    for inst in top_insts:
        for people in top_people:
            query_combos.append((people, inst, news_article.publish_date))

    for paper_group in map(results_for_person_inst_date, query_combos):
        all_paper_results.extend(paper_group)

    doi2paper, doi_paper = score_results(all_paper_results,
                                         news_article.publish_date,
                                         people_freq,
                                         inst_freq)

    result = {"inst_freq": inst_freq,
            "people_freq": people_freq,
            "doi_paper": doi_paper, "doi2paper": doi2paper}

    with open(cache_file,"w") as f:
        json.dump(result, f)

    return result
