"""
Copyright 2020, All rights reserved.
Author : SangJae Kang
Mail : craftsangjae@gmail.com
"""
import asyncio
import requests
from collections import OrderedDict
from datetime import datetime, timedelta
import dateutil
from dateutil.parser import parse as parse_date
from service.query import GETLIMIT_QUERY, GITHUB_GQL
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
GITHUB_KEY_PATH = os.path.join(ROOT_DIR, "credentials/github.txt")


class GithubKeyGen(object):
    """
    복수개의 Github API Key를 관리하는 Singleton 객체를 생성하는 클래스
    GITHUB_KEY_PATH 에는 line 별로 github API Key가 저장되어 있다.
    github key가 Round-Robin 방식으로 돌면서 할당량을 소모해간다.

    **의견**
        Github Key가 수백개로 넘어가게 되면, Max-Heap 방식을 고민할 테지만,
        지금은 Round-Robin 방식으로도 충분하다고 생각

    Issues
    * https://github.com/vienna-project/recohub/issues/2

    Usages

    # 아래에 선언된 GithubKey을 이용해야 함
    >>> GithubKey = GithubKeyGen()

    # API 할당량이 남은 키 가져오기
    >>> (await GithubKey.get_async())

    # 키의 할당량 갱신하기
    >>> (await GithubKey.set_async(remain, resetAt))

    """
    def __init__(self, github_key_path):
        self.key_cache = OrderedDict()
        self.github_key_path = github_key_path
        self.load_keys()

    def load_keys(self):
        with open(self.github_key_path, 'r') as f:
            for key in f.readlines():
                key = key.strip()
                try:
                    remain, resetAt = self.get_resource_limit(key)
                except ValueError as e:
                    print(e)
                    continue
                self.key_cache[key] = (remain, resetAt)
        if len(self.key_cache) == 0:
            raise ValueError(f"{self.github_key_path} have no github key.")

    def __repr__(self):
        key_infos = []
        for key, (remain, resetAt) in self.key_cache.items():
            key_infos.append(f"{key} - ({remain},{resetAt})")
        return "\n".join(key_infos)

    def __len__(self):
        return sum(remain for remain, _ in self.key_cache.values())

    async def get_async(self):
        """ API 할당량이 남은 키 가져오기
        :return: key
        """
        while True:
            min_resetAt = None
            for _ in range(len(self.key_cache)):
                key, (remain, resetAt) = self.key_cache.popitem(last=False)
                self.key_cache[key] = (remain - 1, resetAt)
                min_resetAt = min(min_resetAt, resetAt) if min_resetAt else resetAt

                if remain > 0:
                    return key

            if min_resetAt:
                # key를 반환하지 못한 경우 : 할당량이 바닥남
                # 이 경우 resetAt이 가장 빠르게 도래하는 것을 기준으로 waiting 해주어야 함
                duration = (min_resetAt.replace(tzinfo=None)
                            - datetime.utcnow().replace(tzinfo=None)
                            + timedelta(seconds=10)).total_seconds()
                if duration > 0:
                    await asyncio.sleep(duration)

                # resource 갱신
                self.update_resource_limit()

            else:
                # key_cache가 없는 상황 (예외 상황)
                break

    async def set_async(self, key: str, remain: int, resetAt: datetime=None):
        """ 키의 할당량, 시간을 저장
        """
        if resetAt is None:
            resetAt = datetime.now(tz=dateutil.tz.tzutc()) + timedelta(hours=1)

        curr_remain, curr_resetAt = self.key_cache[key]
        # 비동기적으로 갱신하기 때문에 Skew가 발생할 수 있기 때문에
        # 비교를 통해 최소/ 최대값으로 넣어주어야 함
        self.key_cache[key] = (min(remain, curr_remain),
                               max(resetAt, curr_resetAt))

    def update_resource_limit(self):
        """ github Key의 resource limit을 조회 후 갱신하는 함수
        """
        for key in self.key_cache:
            remain, resetAt = self.get_resource_limit(key)
            self.key_cache[key] = (remain, resetAt)

    @staticmethod
    def get_resource_limit(key: str):
        """ 해당 Key의 resource limit을 가져오는 함수

        :param key: githubAPI Key
        :return:
        """
        auth = {"Authorization": "bearer " + key}
        query = {"query": GETLIMIT_QUERY}

        with requests.post(GITHUB_GQL, headers=auth, json=query) as res:
            if res.status_code == 200:
                query_results = res.json()

                remain = query_results['data']['rateLimit']['remaining']
                resetAt = parse_date(query_results['data']['rateLimit']['resetAt'])
                return remain, resetAt
            else:
                raise ValueError(f"{key} is Bad credentials")
