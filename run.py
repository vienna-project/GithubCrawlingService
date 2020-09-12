"""
Copyright 2020, All rights reserved.
Author : SangJae Kang
Mail : craftsangjae@gmail.com
"""
import os
from service.consumer import RedisQueue
from service.worker import RepositoryCrawler
from service.database import MongoDatabase
from service.github import GithubKeyGen


if __name__ == "__main__":
    BROKER_HOST = os.environ.get("REPO_HOST", "redis")
    DATABASE_HOST = os.environ.get("MONGO_HOST", "mongodb://mongo:27017/")
    NUM_CONCURRENT = int(os.environ.get('NUM_CONCURRENT', 100))

    repo_broker = RedisQueue('repository', host=BROKER_HOST)
    repo_database = MongoDatabase('repository', uri=DATABASE_HOST)
    githubkey = GithubKeyGen("./credentials/github.txt")

    crawler_server = RepositoryCrawler(repo_broker, repo_database, githubkey,
                                       num_concurrent=NUM_CONCURRENT)
    crawler_server.start()
    crawler_server.join()

