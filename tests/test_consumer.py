"""
Copyright 2020, All rights reserved.
Author : SangJae Kang
Mail : craftsangjae@gmail.com
"""
import unittest
from service.consumer import RedisQueue


class TestConsumerMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.queue = RedisQueue("repository", host="localhost", port="6379", db="0")

    def test_isEmpty_and_getLength(self):
        self.queue.deleteAll()
        self.assertTrue(self.queue.isEmpty())

        self.queue.put({"owner": "tensorflow", "name": "tensorflow"})
        self.assertFalse(self.queue.isEmpty())

        self.assertEqual(len(self.queue), 1)
        self.queue.put({"owner": "tensorflow", "name": "tensorflow"})
        self.assertEqual(len(self.queue), 2)
        self.queue.put({"owner": "tensorflow", "name": "tensorflow"})
        self.assertEqual(len(self.queue), 3)

    def test_putAndGet(self):
        self.queue.deleteAll()
        self.assertTrue(self.queue.isEmpty())
        self.assertIsNone(self.queue.get())

        msg1 = {"owner": "tensorflow1", "name": "tensorflow1"}
        self.queue.put(msg1)
        msg2 = {"owner": "tensorflow2", "name": "tensorflow2"}
        self.queue.put(msg2)
        msg3 = {"owner": "tensorflow3", "name": "tensorflow3"}
        self.queue.put(msg3)

        self.assertDictEqual(self.queue.get(), msg1)
        self.assertDictEqual(self.queue.get(), msg2)
        self.assertDictEqual(self.queue.get(), msg3)
        self.assertIsNone(self.queue.get())





