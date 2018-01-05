"""Service for calling microsoft knowledge graph"""

import requests
from flask import current_app
from datetime import datetime, timedelta

def generate_date_constraint(date, days=60):
    """Generate date constraint for mskg. Only allow papers within X days."""
    DATE_OUT_FMT = "%Y-%m-%d"
    lower = date - timedelta(days=days)
    upper = date + timedelta(days=days)
    return "['{}','{}']".format(lower.strftime(DATE_OUT_FMT),
                                upper.strftime(DATE_OUT_FMT))


def generate_person_affil_constraint(person,inst=None):
    """Generate Microsoft knowledge graph person/affiliation constraint"""

    if inst is None:
        return "Composite(AA.AuN='{author}')".format(author=person.lower().strip())
    else:
        return "Composite(AA.AuN='{author}'),Composite(AA.AfN='{inst}')".format(
            author=person.lower().strip(),
            inst=inst.lower().strip()
        )


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

    return requests.post(endpoint, headers=headers, data=params)
