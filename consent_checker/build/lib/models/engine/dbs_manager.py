import os
import redis
from dotenv import load_dotenv
from dateutil import parser
from datetime import datetime

# Load environment variables from a .env file
load_dotenv()

class RedisDBManager:
    """
    Interacts with the Redis database for general operations and Bloom filter bit manipulation.
    Provides methods for setting, getting, deleting keys, and manipulating bits for Bloom filters.
    """
    
    def __init__(self):
        """
        Initialize a RedisDBManager instance and connect to Redis using environment variables.
        Default values are used if environment variables are not set.
        """
        self.__redis_client = redis.StrictRedis(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 6379)),
            db=int(os.getenv('DB_INDEX', 5)),
            decode_responses=True  # Ensures string responses by decoding bytes
        )

    def set(self, key, value):
        """
        Sets the value of the specified key in Redis.
        :param key: Redis key to set.
        :param value: Value to associate with the key.
        :return: True if successful, False otherwise.
        """
        return self.__redis_client.set(key, value)

    def get(self, key):
        """
        Retrieves the value of the specified key from Redis.
        :param key: Redis key to retrieve.
        :return: Value associated with the key or None if the key does not exist.
        """
        return self.__redis_client.get(key)

    def delete(self, key):
        """
        Deletes the specified key from Redis.
        :param key: Redis key to delete.
        :return: The number of keys removed.
        """
        return self.__redis_client.delete(key)

    def exists(self, key):
        """
        Checks if the specified key exists in Redis.
        :param key: Redis key to check.
        :return: 1 if the key exists, 0 otherwise.
        """
        return self.__redis_client.exists(key)

    def expire(self, key, seconds):
        """
        Sets a timeout on a key.
        :param key: Redis key to set the timeout on.
        :param seconds: Expiration time in seconds.
        :return: True if the timeout was set, False otherwise.
        """
        return self.__redis_client.expire(key, seconds)

    def ttl(self, key):
        """
        Gets the time-to-live for a key.
        :param key: Redis key to check.
        :return: TTL in seconds, -1 if the key does not have an expiration, or -2 if the key does not exist.
        """
        return self.__redis_client.ttl(key)

    def setbit(self, key, offset, value):
        """
        Sets or clears the bit at offset in the string value stored at key.
        :param key: Redis key for the Bloom filter.
        :param offset: The bit position to set.
        :param value: 1 to set the bit, 0 to clear it.
        :return: The original bit value stored at the offset.
        """
        return self.__redis_client.setbit(key, offset, value)

    def getbit(self, key, offset):
        """
        Returns the bit value at offset in the string value stored at key.
        :param key: Redis key for the Bloom filter.
        :param offset: The bit position to check.
        :return: The bit value at offset (1 or 0).
        """
        return self.__redis_client.getbit(key, offset)

    def pipeline(self):
        """
        Returns a Redis pipeline for batch operations.
        Pipelines group multiple commands to be sent as a single batch.
        :return: Redis pipeline object.
        """
        return self.__redis_client.pipeline()

