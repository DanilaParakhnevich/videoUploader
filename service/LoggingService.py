from loguru import logger

from service.StateService import StateService

# Просто обертка над loguru

logger.add('log/BuxarVideoUploader.log', format='{time} {level} {message}', level='DEBUG', rotation='10MB', compression='zip')
state_service = StateService()

def log_error(msg: str):
    state_service.set_error_status(True)
    logger.log(_Logger__level='ERROR', _Logger__message=msg)


def log_info(msg: str):
    logger.log(_Logger__level='INFO', _Logger__message=msg)

import smtpd
import asyncore

class FakeSMTPServer(smtpd.SMTPServer):
    """A Fake smtp server"""

    def __init__(*args, **kwargs):
        smtpd.SMTPServer.__init__(*args, **kwargs)

    def process_message(*args, **kwargs):
        pass

if __name__ == "__main__":
    smtp_server = FakeSMTPServer(('localhost', 1025), None)
    smtp_server.send()
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        smtp_server.close()