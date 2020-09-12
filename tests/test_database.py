"""
Copyright 2020, All rights reserved.
Author : SangJae Kang
Mail : craftsangjae@gmail.com
"""
import asyncio
import unittest
import json
from service.database import MongoDatabase


class TestConsumerMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = MongoDatabase("repository")
        cls.documents = json.load(open("./mock_document.json"))

    def test_count_documents_and_put_and_get(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.db.deleteAll())
        res = loop.run_until_complete(self.db.count())

        self.assertEqual(res, 0)

        for i, document in enumerate(self.documents, 1):
            loop.run_until_complete(self.db.put(document))
            res = loop.run_until_complete(self.db.count())
            self.assertEqual(res, i)
            res = loop.run_until_complete(self.db.get(document['id']))
            self.assertDictEqual(res, document)

        # Not Exists
        res = loop.run_until_complete(self.db.get("abc"))
        self.assertIsNone(res)

    def test_get_not_exist(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.db.deleteAll())
        res = loop.run_until_complete(self.db.count())
        self.assertEqual(res, 0)

        # Not Exists
        res = loop.run_until_complete(self.db.get("abc"))
        self.assertIsNone(res)




