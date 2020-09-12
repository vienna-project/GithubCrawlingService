"""
Copyright 2020, All rights reserved.
Author : SangJae Kang
Mail : craftsangjae@gmail.com
"""
import asyncio
import aiohttp
from threading import Thread
from service.consumer import BaseConsumer
from service.query import GETREPO_QUERY, GITHUB_GQL, GITHUB_REPOSITORY_ID_URL
from service.github import GithubKeyGen
from service.database import BaseDatabase
from service.document import parse_repository, parse_rateLimit


class RepositoryCrawler(Thread):
    """
    리파짓토리 정보를 메시지 브로커로부터 가져와서, GihutAPI로부터 획득 후 데이터 베이스로 전달하는 Crawling Thread

    Arguments
        broker: messaga를 가져올 브로커 인스턴스
        database: crawling한 repository를 저장할 데이터베이스 인스턴스
        num_concurrent: 비동기적으로 몇개의 동시 IO를 진행할 것인가 결정

    """

    def __init__(self,
                 broker:BaseConsumer,
                 database:BaseDatabase,
                 githubkey:GithubKeyGen,
                 num_concurrent=100,
                 sleep=1.):
        Thread.__init__(self)
        self.daemon = True
        self.broker = broker
        self.database = database
        self.githubkey = githubkey
        self.num_concurrent = num_concurrent
        self.sleep = sleep

    def run(self):
        """ Create and run `Crawling` Event Loop
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.crawl_concurrent())
        loop.close()

    async def crawl_concurrent(self):
        """ 동시에 github API로 crawl
        """
        concurrent_tasks = set()
        loop = asyncio.get_event_loop()
        while True:
            if self.broker.isEmpty():
                await asyncio.sleep(self.sleep)
                continue
            if len(concurrent_tasks) >= self.num_concurrent:
                # Wait for some tasks to finish before adding a new one
                # ref : https://stackoverflow.com/questions/48483348/how-to-limit-concurrency-with-python-asyncio
                _done, concurrent_tasks = await asyncio.wait(
                    concurrent_tasks, return_when=asyncio.FIRST_COMPLETED)
            concurrent_tasks.add(loop.create_task(self.crawl()))

    async def crawl(self):
        """ 비동기 방식으로 아래 작업을 진행
        1. Github keys 중 할당량이 남아있는 키 획득
        2. Crawling할 github repository name & owner 가져오기
        3. Github api를 통해 해당 리파짓토리 정보 획득
        4. 성공한 경우, database에 put, 실패한 경우, error-cases.log에 저장
        """

        api_key = await asyncio.wait_for(self.githubkey.get_async(), timeout=3600)
        message = self.broker.get()
        try:
            if isinstance(message, dict) and 'owner' in message and 'name' in message:
                repo_name, repo_owner = message['name'], message['owner']

            # TODO : 'id'를 바탕으로 Crawling하는 코드 구성하기
            # RestAPI을 통해 먼저 이름과 소유주를 받고, 없는 녀석을 채워야 함
            # elif isinstance(message, dict) and 'id' in message:
            #     try:
            #         repo_name, repo_owner = await self.get_name_and_owner_by_repository_id(message['id'], api_key)
            #     except ConnectionAbortedError:
            #         await self.githubkey.set_async(api_key, 0)
            #         self.broker.put(message)
            #         return
            #     except ValueError:
            #
            #         return
            #     self.broker.put({"name": repo_name, "owner": repo_owner})
            #     return
            else:
                return

            github_repository_info = await self.get_repository_info_by_name_and_owner(repo_name, repo_owner, api_key)

            try:
                document = parse_repository(github_repository_info)
            except ValueError:
                return

            await asyncio.wait_for(self.database.put(document), timeout=10)

            # 깃헙의 할당량 정보 갱신
            try:
                remain, resetAt = parse_rateLimit(github_repository_info)
            except ValueError:
                return
            await asyncio.wait_for(self.githubkey.set_async(api_key, remain, resetAt), timeout=10)
        except asyncio.TimeoutError:
            self.broker.put(message)

    @staticmethod
    async def get_name_and_owner_by_repository_id(repo_id, api_key):
        async with aiohttp.ClientSession() as sess:
            auth = {"Authorization": "bearer " + api_key}
            async with sess.get(GITHUB_REPOSITORY_ID_URL + str(repo_id), headers=auth) as res:
                content = await asyncio.wait_for(res.json(), timeout=10)
                status_code = res.status

                if status_code == 403 and "api rate limit" in content.get("message", "").lower():
                    raise ConnectionAbortedError(str(content))

                if ('owner' in content
                        and isinstance(content['owner'], dict)
                        and 'login' in content['owner']):
                    repo_owner = content['owner']['login']
                else:
                    raise ValueError(f"{repo_id} - content: {content}")
                repo_name = content.get("name", "")
        return repo_name, repo_owner

    @staticmethod
    async def get_repository_info_by_name_and_owner(name, owner, api_key):
        auth = {"Authorization": "bearer " + api_key}
        query = {
            "query": GETREPO_QUERY,
            "variables": {
                "owner": owner,
                "name": name
            }
        }
        async with aiohttp.ClientSession() as sess:
            async with sess.post(GITHUB_GQL, headers=auth, json=query) as res:
                return await asyncio.wait_for(res.json(), timeout=10)
