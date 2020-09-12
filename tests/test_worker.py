"""
Copyright 2020, All rights reserved.
Author : SangJae Kang
Mail : craftsangjae@gmail.com
"""
import asyncio
import unittest
from service.github import GithubKeyGen
from service.consumer import RedisQueue
from service.database import MongoDatabase
from service.document import parse_repository
from service.worker import RepositoryCrawler


class TestConsumerMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        github = GithubKeyGen("../credentials/github.txt")
        database = MongoDatabase("repository")
        broker = RedisQueue("repository", host="localhost", port="6379", db="0")
        cls.worker = RepositoryCrawler(broker, database, github)

        cls.api_key = list(github.key_cache.keys())[0]

    def test_get_name_and_owner_by_repository_id(self):
        loop = asyncio.get_event_loop()
        repo_name, repo_owner = (
            loop.run_until_complete(self.worker.get_name_and_owner_by_repository_id(56417681, self.api_key)))
        self.assertEqual(repo_name, "implicit")
        self.assertEqual(repo_owner, "benfred")

    def test_get_name_and_owner_by_repository_id_not_exist(self):
        loop = asyncio.get_event_loop()
        with self.assertRaises(ValueError):
            loop.run_until_complete(self.worker.get_name_and_owner_by_repository_id(56417222222222212312681, self.api_key))

    def test_get_repository_info_by_name_and_worker(self):
        loop = asyncio.get_event_loop()
        document = loop.run_until_complete(self.worker.get_repository_info_by_name_and_owner("implicit", "benfred", self.api_key))
        print(parse_repository(document))

    def test_get_repository_info_by_name_and_worker_not_exists(self):
        loop = asyncio.get_event_loop()

        with self.assertRaises(ValueError):
            document = loop.run_until_complete(self.worker.get_repository_info_by_name_and_owner("implasdsicit", "benfred", self.api_key))
            print(parse_repository(document))