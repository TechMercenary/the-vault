import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if os.environ.get('DEBUG', 'False') == 'True':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

SQLALQUEMY_ECHO = os.environ.get('SQLALQUEMY_ECHO', 'False') == 'True'