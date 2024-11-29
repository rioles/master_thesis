import hashlib
import redis
from models import storage
#storage = RedisDBManager()  # This should correctly instantiate the class
import hashlib
import json
class BloomFilter:
    def __init__(self, size=10000, hash_count=7, redis_key="consent_metadata"):
        self.size = size
        self.hash_count = hash_count
        self.redis_key = redis_key

    def _hashes(self, item):
        hashes = []
        for i in range(self.hash_count):
            item_str = json.dumps(item)
            hash_digest = hashlib.sha256((item_str + str(i)).encode()).hexdigest()
            hash_val = int(hash_digest, 16) % self.size
            hashes.append(hash_val)
        return hashes

    def add(self, redis_client, item):
        hashes = self._hashes(item)
        pipeline = redis_client.pipeline()
        for hash_val in hashes:
            pipeline.setbit(self.redis_key, hash_val, 1)
        pipeline.execute()

    def check(self, redis_client, item):
        hashes = self._hashes(item)
        print(hashes)
        for hash_val in hashes:
            if redis_client.getbit(self.redis_key, hash_val) == 0:
                return False
        return True

# Initialize Redis connection (commented out for demonstration)
# redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Initialize Bloom Filter
bloom_filter = BloomFilter(size=10000, hash_count=7, redis_key="consent_data")
bloom_filter1 = BloomFilter(size=10000, hash_count=7, redis_key="user_id_enterprise_id")

# Example usage
bloom_filter1.add(storage, "47utr")
print(dir(storage))

exists = bloom_filter1.check(storage, "terfd")
print("Exists:", exists)  # Output: True
