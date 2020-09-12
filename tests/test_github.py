"""
Copyright 2020, All rights reserved.
Author : SangJae Kang
Mail : craftsangjae@gmail.com
"""
import asyncio
import unittest
from service.github import GithubKeyGen


class TestGithub(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.github = GithubKeyGen("../credentials/github.txt")

    def test_get_async(self):
        print("Length : ", len(self.github))

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.github.get_async())
        print("Key : ", result)
        print("Length : ", len(self.github))

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.github.get_async())
        print("Key : ", result)
        print("Length : ", len(self.github))

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.github.get_async())
        print("Key : ", result)
        print("Length : ", len(self.github))

        self.github.update_resource_limit()
        print("Length : ", len(self.github))
        loop.close()