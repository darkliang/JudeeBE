import redis
import json


class RedisConnPool:
    def __init__(self, **redis_cp_kwargs):
        self.__conn_pool = redis.ConnectionPool(**redis_cp_kwargs)

    @property
    def conn_pool(self):
        return self.__conn_pool


with open('utils/message_queue/redis_conn_pool.json', 'r') as f:
    kwargs = json.load(f)

redis_connection_pool = RedisConnPool(**kwargs).conn_pool
