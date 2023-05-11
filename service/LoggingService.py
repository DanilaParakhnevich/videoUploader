from loguru import logger

# Просто обертка над loguru

logger.add('log/app.log', format='{time} {level} {message}', level='DEBUG', rotation='10MB', compression='zip')


def log_error(msg: str):
    logger.log(_Logger__level='ERROR', _Logger__message=msg)


def log_info(msg: str):
    logger.log(_Logger__level='INFO', _Logger__message=msg)
