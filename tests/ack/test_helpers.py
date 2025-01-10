import random
import time

from ack.helpers import redis_client


def test_redis_int():
    unixtime = int(time.time())
    value = random.randint(3, 134)
    key = f"test_redis_int.{unixtime}.{value}"
    redis_client.set_int(key, value)
    retrieved_value = redis_client.get(key)
    assert retrieved_value == value


def test_redis_str():
    unixtime = int(time.time())
    value = str(random.randint(3, 134))
    key = f"test_redis_str.{unixtime}.{value}"
    redis_client.set_str(key, value)
    retrieved_value = redis_client.get(key)
    assert retrieved_value == value
