import logging

logger = logging.getLogger('main')

def log_catcher(func):

    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = f'Error occurred: {e}'
            logger.error(error_message)
            raise e

    return inner

