import random
import time
import logging


def log_time_async( func ):
    async def wrapper( *args, **kwargs ):
        id = random.randint(1, 1000000)
        start_time = time.time()
        logging.info(f"{func.__name__}: Start {id}")

        result = await func(*args, **kwargs)

        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f"{func.__name__}: End {id} | Execution time: {execution_time:.4f} seconds")
        return result
    return wrapper

def log_time( func ):
    def wrapper( *args, **kwargs ):
        id = random.randint(1, 1000000)
        start_time = time.time()
        logging.info(f"{func.__name__}: Start {id}", id)

        result = func(*args, **kwargs)

        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f"{func.__name__}: End {id} | Execution time: {execution_time:.4f} seconds")
        return result
    return wrapper