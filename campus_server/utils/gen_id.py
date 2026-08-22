import time
import random

def gen_id(prefix=""):
    """复用 hospital_server/utils.py:gen_id 规则 -> PREFIX + 毫秒时间戳 + 2位随机数"""
    ts = int(time.time() * 1000)
    rnd = random.randint(10, 99)
    return f"{prefix}{ts}{rnd}"
