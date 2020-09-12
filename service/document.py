"""
Copyright 2020, All rights reserved.
Author : SangJae Kang
Mail : craftsangjae@gmail.com
"""
import base64
from dateutil.parser import parse as parse_date


def parse_repository(query):
    if 'data' in query and 'repository' in query['data']:
        document = query['data']['repository']
        if not isinstance(document, dict):
            raise ValueError(query)
    else:
        raise ValueError("query" + query)

    for k, v in document.items():
        if k == 'owner':
            document[k] = v.get('login', "")
        elif k in {"watchers", "stargazers", "commitComments",
                   "pullRequests", "releases", "deployments", "labels"}:
            if isinstance(v, dict):
                document[k] = v.get('totalCount', 0)
            else:
                document[k] = 0
        elif k == "primaryLanguage":
            if isinstance(v, dict):
                document[k] = v.get('name', "")
            else:
                document[k] = ""
        elif k == "licenseInfo":
            if isinstance(v, dict):
                document[k] = v.get('name', "")
            else:
                document[k] = ""
        elif k == "languages":
            if isinstance(v, dict):
                document[k] = [
                    elem.get('name', "") for elem in v.get('nodes', [])
                    if isinstance(elem, dict)]
        elif k == "repositoryTopics":
            try:
                document[k] = [
                    elem.get('topic', {}).get("name", "")
                    for elem in v.get('nodes', [])]
            except AttributeError:
                document[k] = []

    try:
        repo_id = int(base64.decodebytes(document['id'].encode("utf8"))
                      .decode('utf8').split('Repository')[-1])
    except:
        repo_id = -1

    document["repo_id"] = repo_id
    return document


def parse_rateLimit(query):
    if "data" in query and 'rateLimit' in query['data']:
        limit_result = query['data']['rateLimit']
        remain, resetAt = limit_result['remaining'], parse_date(limit_result['resetAt'])
        return remain, resetAt
    else:
        raise ValueError()

