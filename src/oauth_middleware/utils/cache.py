import time
from functools import lru_cache


def timed_cache(seconds):
    g_limit = round(time.time() / seconds)

    def wrapper_a(func):
        def wrapper_b(*args, **kwargs):
            @lru_cache()
            def inner_wrapper(limit=None):
                return func(*args, **kwargs)

            return inner_wrapper(g_limit)

        return wrapper_b

    return wrapper_a
