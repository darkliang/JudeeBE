import redis
from utils.message_queue.singleConnPool import redis_connection_pool


class RedisQueue:
    def __init__(self, name, namespace='queue', **redis_sr_kwargs):
        self.__rc = redis.StrictRedis(**redis_sr_kwargs)
        self.key = '{}:{}'.format(namespace, name)

    def qsize(self):
        return self.__rc.llen(self.key)  # 返回队列里面list内元素的数量

    def put(self, item):
        return self.__rc.rpush(self.key, item)  # 添加新元素到队列最右方

    def pop_block(self, timeout=None, need_name=False) -> bytes:
        # 返回队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        # 返回值为一个tuple
        item = self.__rc.blpop(self.key, timeout=timeout)
        if need_name:
            return item
        else:
            return item[1]

    def pop(self):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        item = self.__rc.lpop(self.key)
        return item

    def peek(self):
        # 返回队列的第一个元素，如果队列为空返回None
        item = self.__rc.lindex(self.key, 0)
        return item


def get_queue_from_single_pool(name, namespace='queue'):
    return RedisQueue(name, namespace=namespace, connection_pool=redis_connection_pool)


class Producer:
    def __init__(self, queue=None, namespace='queue', name='', **redis_sr_kwargs):
        if type(queue) == RedisQueue:
            self.__queue = queue
        else:
            self.__queue = RedisQueue(name, namespace, **redis_sr_kwargs)

    def produce(self, product):
        return self.__queue.put(product)

    def get_size(self):
        return self.__queue.qsize()


def get_producer_from_single_pool(name, namespace='queue'):
    return Producer(queue=get_queue_from_single_pool(name, namespace=namespace))


class Consumer:
    def __init__(self, queue=None, namespace='queue', name='', **redis_sr_kwargs):
        if type(queue) == RedisQueue:
            self.__queue = queue
        else:
            self.__queue = RedisQueue(name, namespace, **redis_sr_kwargs)

    def consume(self, block=True):
        if block:
            return self.__queue.pop_block().decode()
        return self.__queue.pop().decode()

    def get_size(self):
        return self.__queue.qsize()


def get_consumer_from_single_pool(name, namespace='queue'):
    return Consumer(queue=get_queue_from_single_pool(name, namespace=namespace))
