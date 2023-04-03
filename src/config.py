import os
import logging
from enum import Enum, auto


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if os.environ.get('DEBUG', 'False') == 'True':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

SQLALQUEMY_ECHO = os.environ.get('SQLALQUEMY_ECHO', 'False') == 'True'


class Side(Enum):
    CREDIT = 'CREDIT'
    DEBIT = 'DEBIT'


# TODO: Add more account types
class AccountType(Enum):
    ASSET = 'ASSET'
    LIABILITY = 'LIABILITY'

# TODO: Complete the mapping after adding more account types
MAP_ACCOUNT_TYPE_TO_SIDE = {
    AccountType.ASSET.value: Side.DEBIT.value,
    AccountType.LIABILITY.value: Side.CREDIT.value,
}

# TODO: Expose the LOCAL_TIME_ZONE as a setting, and in a bottom bar (to the right corner)
LOCAL_TIME_ZONE = os.environ.get('LOCAL_TIME_ZONE', 'America/Argentina/Buenos_Aires')
