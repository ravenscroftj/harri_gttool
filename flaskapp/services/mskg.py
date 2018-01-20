"""Service for calling microsoft knowledge graph"""

import os
import math
import requests
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
    doi_paper = defaultdict(lambda: 0)

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


        if 'DOI' in E:
            print(E['DOI'])
            doi2paper[E['DOI']] = ent


        for author in ent['AA']:

            best_match_name = max([ (fuzz.ratio(author['AuN'],person.lower().strip()) ** 2 *count) for
                             person,count in people_freq.items()])

            if 'AfN' in author:
                best_match_inst = max([ (fuzz.ratio(author['AfN'],inst.lower().strip()) **2 * count) for
                                 inst,count in inst_freq.items()])
            else:
                best_match_inst = 0

            #print(author['AuN'], best_match_name/people_count, best_match_inst/inst_count)

            score = (best_match_name/people_count)+(best_match_inst/inst_count) / td

            if 'DOI' in E:
                doi_paper[E['DOI']] += score
            else:
                doi_paper[ent['Ti']] += score

        if 'DOI' in E:
            doi_paper[E['DOI']] /= len(ent['AA'])
        else:
            doi_paper[ent['Ti']] /= len(ent['AA'])
            
    return doi2paper, doi_paper


def generate_date_constraint(date, days=60):
    """Generate date constraint for mskg. Only allow papers within X days."""
    DATE_OUT_FMT = "%Y-%m-%d"
    lower = date - timedelta(days=days)
    upper = date + timedelta(days=days)
    return "['{}','{}']".format(lower.strftime(DATE_OUT_FMT),
                                upper.strftime(DATE_OUT_FMT))


def generate_person_affil_constraint(person, inst=None):
    """Generate Microsoft knowledge graph person/affiliation constraint"""

    if inst is None:
        return "Composite(AA.AuN='{author}')".format(author=person.lower().strip())
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

    print(result.text)

    return result



def results_for_person_inst_date(query):

    person, inst, date = query

    print(inst, person)

    results = []

    q = "AND({person},D={daterange})"

    res = get_papers_for_query(q.format(person=generate_person_affil_constraint(person,inst),
               daterange=generate_date_constraint(date)))


    ents = res.json()['entities']

    if len(ents) > 0:
        results.extend(ents)

    # get crossref results too
    #ents = get_crossref_results(people, date)

    #if len(ents) > 0:
    #    results.extend(ents)

    return results


def find_candidate_papers(news_article):
    """Find candidate scientific paper matches for given news article"""

    cachedir = current_app.config['CACHE_DIR']
    candidate_cache = os.path.join(cachedir, "candidates")

    if not os.path.exists(candidate_cache):
        os.makedirs(candidate_cache)

    cache_file = os.path.join(candidate_cache,
                              "{}.json".format(news_article.id))

    if os.path.exists(cache_file):
        with open(cache_file) as f:
            return json.load(f)

    # find people and institutions
    people = defaultdict(lambda: [])
    insts = defaultdict(lambda: [])

    for person in news_article.people():
        people[person.text].append((person.start, person.end))

    for inst in news_article.institutions():
        insts[inst.text].append((inst.start, inst.end))

    inst_freq, people_freq = find_ent_frequencies(insts, people)

    top_people = sorted(people_freq, key=lambda x: people_freq[x], reverse=True)
    top_insts = sorted(inst_freq, key=lambda x: inst_freq[x], reverse=True)

    all_paper_results = []
    query_combos = []

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
