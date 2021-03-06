"""
Copyright 2020, All rights reserved.
Author : SangJae Kang
Mail : craftsangjae@gmail.com
"""
import redis
import json
import abc


class BaseConsumer:
    __metaclass__ = abc.ABC

    @abc.abstractmethod
    def deleteAll(self):
        """
        메시지 모두 없애기
        """
        pass

    @abc.abstractmethod
    def isEmpty(self):
        """
        브로커의 메시지가 비었는지 확인
        """
        pass

    @abc.abstractmethod
    def put(self, elem):
        """
        브로커에 메시지를 담기
        """
        pass

    @abc.abstractmethod
    def get(self):
        """
        브로커에서 메시지를 가져오기
        """
        pass

    @abc.abstractmethod
    def __len__(self):
        """
        브로커에 남아있는 메시지 수 가져오기
        """
        pass


class RedisQueue(BaseConsumer):
    """
        redis로 이루어진 FIFO Queue Style Broker 클래스
    """

    def __init__(self, topic, **redis_kwargs):
        """
            host='localhost', port=6379, db=0
        """
        self.topic = topic
        self.rq = redis.Redis(**redis_kwargs)

    def deleteAll(self):
        return self.rq.delete(self.topic)

    def isEmpty(self):
        return self.rq.llen(self.topic) == 0

    def put(self, elem):
        self.rq.lpush(self.topic, json.dumps(elem))

    def get(self):
        elem = self.rq.rpop(self.topic)
        if elem:
            return json.loads(elem)
        else:
            return None

    def __len__(self):
        return self.rq.llen(self.topic)


