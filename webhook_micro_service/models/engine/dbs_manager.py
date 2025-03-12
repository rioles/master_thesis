import os
import redis
from dotenv import load_dotenv
load_dotenv()
from dateutil import parser
from datetime import datetime
import json


class RedisDBManager:
    """Interacts with the Redis database for general operations and Bloom filter bit manipulation."""
    __redis_client = None

    def __init__(self):
        """Initialize a RedisDBManager instance and connect to Redis using environment variables."""
        self.__redis_client = redis.StrictRedis(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=int(os.environ.get('DB_PORT', 6379)),
            db=int(os.environ.get('DB_INDEX', 0)),
            decode_responses=True
        )

    def set(self, key, value):
        """Sets the value of the specified key in Redis."""
        return self.__redis_client.set(key, value)

    def get(self, key):
        """Retrieves the value of the specified key from Redis."""
        return self.__redis_client.get(key)

    def delete(self, key):
        """Deletes the specified key from Redis."""
        return self.__redis_client.delete(key)

    def exists(self, key):
        """Checks if the specified key exists in Redis."""
        return self.__redis_client.exists(key)

    def expire(self, key, seconds):
        """Sets a timeout on a key."""
        return self.__redis_client.expire(key, seconds)

    def ttl(self, key):
        """Gets the time to live for a key."""
        return self.__redis_client.ttl(key)

    def pipeline(self):
        """Returns a Redis pipeline for batch operations."""
        return self.__redis_client.pipeline()
        
    def getbit(self, key, offset):
        """
        Returns the bit value at offset in the string value stored at key.
        :param key: The Redis key for the Bloom filter.
        :param offset: The bit position to check.
        :return: The bit value at offset (1 or 0).
        """
        return self.__redis_client.getbit(key, offset)

        
if __name__ == "__main__":
    client_id = os.getenv("CLIENT_ID")
    client_id_test = os.getenv("CLIENT_IDs") 
    client_id_tests = os.getenv("CLIENT_IDss")
    client_url = os.getenv("CLIENT_URL")
    cmd_url = os.getenv("CLIENT_URLs")
    redis = RedisDBManager()
    pipeline = redis.pipeline()
    client_urls = {"client_ressour_url":client_url}
    client_urls["cmd_url"] = cmd_url
    redis.set(client_id, json.dumps(client_urls))
    redis.set(client_id_tests, json.dumps(client_urls))
    data = json.loads(redis.get(client_id_test))["client_ressour_url"]
    print(data)
    print(pipeline)
	
