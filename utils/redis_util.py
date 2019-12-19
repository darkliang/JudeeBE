from django_redis import get_redis_connection
from user.models import UserData


class RedisQueue:

    @staticmethod
    def qsize(key):
        return get_redis_connection('default').llen(key)  # 返回队列里面list内元素的数量

    @staticmethod
    def put(key, item):
        return get_redis_connection('default').rpush(key, item)  # 添加新元素到队列最右方

    @staticmethod
    def pop_block(key, timeout=None, need_name=False) -> bytes:
        # 返回队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        # 返回值为一个tuple
        rc = get_redis_connection('default')
        item = rc.blpop(key, timeout=timeout)
        if need_name:
            return item
        else:
            return item[1]

    @staticmethod
    def pop(key):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        return get_redis_connection('default').lpop(key)

    @staticmethod
    def peek(key):
        # 返回队列的第一个元素，如果队列为空返回None
        return get_redis_connection('default').lindex(key, 0)


class RedisRank:
    user_num = 0
    name = 'user:score'

    @classmethod
    def record_score(cls, mapping):
        rds = get_redis_connection('default')
        rds.zadd(cls.name, mapping)
        cls.user_num = rds.zcard('user:score')
        if len(mapping) == 1:
            return rds.zrevrank('user:score', list(mapping)[0])

        # 获取排行前num位的数据

    @classmethod
    def get_ranking(cls, username):
        return get_redis_connection('default').zrevrank('user:score', username)

    @classmethod
    def get_top_n_users(cls, limit, offset=0):
        # zrevrange key start stop [WITHSCORES(是否返回数组的形式(article_id, count))]
        # 返回有序集 key 中，指定区间内的成员
        rds = get_redis_connection('default')
        if limit == -1:
            users = rds.zrevrange(cls.name, 0, limit)
        else:
            users = rds.zrevrange(cls.name, offset, offset + limit)
        # 返回前num项数据，每一包含（'User-clicks',user_id,count）
        # 取出id和count
        # print(users)
        users_data = []
        for username in users:
            # print(username)
            users_data.append(UserData.objects.get(username=username.decode()))
        return cls.user_num, users_data
