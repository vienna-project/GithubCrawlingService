"""
Copyright 2020, All rights reserved.
Author : SangJae Kang
Mail : craftsangjae@gmail.com
"""
import os
import abc
import json
from motor.motor_asyncio import AsyncIOMotorClient
import aiofiles


class BaseDatabase:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    async def put(self, document: dict):
        """
        데이터베이스에 document 저장하기

        :param document:
        :return:
        """
        pass


class MongoDatabase(BaseDatabase):
    """
    Crawling document을 MongoDB에 비동기적으로 저장하는 데이터베이스 클래스
    """

    def __init__(self,
                 collection,
                 dbname='github',
                 uri="mongodb://localhost:27017/"):
        self.uri = uri
        self.collection = collection
        self.dbname = dbname

    async def put(self, document: dict):
        # caution : 이벤트 루프가 충돌할 수 있기 때문에, 넣을 때마다 매번 client를 선언해 주어야 함
        client = AsyncIOMotorClient(self.uri)
        collection = client[self.dbname][self.collection]

        if 'id' not in document:
            raise ValueError("document should contain id")

        await collection.replace_one({"id": document["id"]}, document, upsert=True)
        client.close()

    async def get(self, document_id):
        # caution : 이벤트 루프가 충돌할 수 있기 때문에, 넣을 때마다 매번 client를 선언해 주어야 함
        client = AsyncIOMotorClient(self.uri)
        collection = client[self.dbname][self.collection]

        res = await collection.find_one({"id": document_id})
        if res:
            res.pop('_id', None)
        client.close()
        return res

    async def deleteAll(self):
        client = AsyncIOMotorClient(self.uri)
        collection = client[self.dbname][self.collection]
        await collection.drop()
        client.close()

    async def count(self):
        client = AsyncIOMotorClient(self.uri)
        collection = client[self.dbname][self.collection]
        res = await collection.count_documents({})
        client.close()
        return res


class FileSystemDatabase(BaseDatabase):
    """
    Crawling document을 FileSystem에 비동기적으로 저장하는 데이터베이스 클래스
    """

    def __init__(self, fpath):
        self.fpath = fpath
        os.makedirs(os.path.dirname(self.fpath), exist_ok=True)

    async def put(self, document: dict):
        async with aiofiles.open(self.fpath, 'a+') as f:
            await f.write(json.dumps(document) + '\n')
