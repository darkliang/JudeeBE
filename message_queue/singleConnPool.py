import redis
import json

class redis_conn_pool():
    def __init__(self, **redis_cp_kwargs):
        self.__conn_pool = redis.ConnectionPool(**redis_cp_kwargs)

    @property
    def conn_pool(self):
        return self.__conn_pool


with open('redis_conn_pool.json', 'r') as f:
    a = json.load(f)
    
    
redis_connection_pool = redis_conn_pool(**a).conn_pool