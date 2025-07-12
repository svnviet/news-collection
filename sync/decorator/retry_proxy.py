import time
from functools import wraps


def retry_on_proxy(max_attempts=5, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    print(f"[Attempt {attempt}] Error: {e}")
                    last_exception = e
                    time.sleep(delay)
            raise RuntimeError(f"All {max_attempts} attempts failed.") from last_exception

        return wrapper

    return decorator
