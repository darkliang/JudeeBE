from redis import StrictRedis


class RedisQueue(object):
    def __init__(self, name, host='localhost', port=6379):
        # redis的默认参数为：host='localhost', port=6379, db=0， 其中db为定义redis database的数量
        self.db = StrictRedis(host=host, port=port, db=0, password=123456)
        self.key = name

    def size(self):
        return self.db.llen(self.key)  # 返回队列里面list内元素的数量

    def add(self, message):
        self.db.rpush(self.key, message)  # 添加新元素到队列最右方

    def pool_block(self, timeout=None):
        # 返回并移除队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        item = self.db.blpop(self.key, timeout=timeout)[1].decode()
        return item

    def pool(self):
        # 返回并移除队列的第一个的元素，如果队列为空返回的是None
        item = self.db.lpop(self.key).decode()
        return item

    def peek(self):
        # 返回队列的第一个元素，如果队列为空返回None
        item = self.db.lindex(self.key, 0).decode()
        return item
