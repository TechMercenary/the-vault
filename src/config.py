import os
import logging
from enum import Enum


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if os.environ.get('DEBUG', 'False') == 'True':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

SQLALQUEMY_ECHO = os.environ.get('SQLALQUEMY_ECHO', 'False') == 'True'


class NormalSideEnum(Enum):
    CREDIT = 'CREDIT'
    DEBIT = 'DEBIT'


class AccountTypeEnum(Enum):
    # Assets
    CASH = 'CASH'
    ACCOUNT_RECEIVABLE = 'ACCOUNT_RECEIVABLE'
    SALARY_RECEIVABLE = 'SALARY_RECEIVABLE'
    # Liabilities
    CASH_OVERDRAFT = 'CASH_OVERDRAFT'
    SALARY_DEFERRED_REVENUE = 'SALARY_DEFERRED_REVENUE'
    ACCOUNT_PAYABLE = 'ACCOUNT_PAYABLE'
    LOAN = 'LOAN'
    CREDIT_CARD = 'CREDIT_CARD'
    DEFERRED_REVENUE = 'DEFERRED_REVENUE'
    # Revenue
    SALARY_REVENUE = 'SALARY_REVENUE'
    # Expenses
    AMORTIZATION_EXPENSE = 'AMORTIZATION_EXPENSE'
    SALARY_TAX = 'SALARY_TAX'
    SALARY_EXPENSE = 'SALARY_EXPENSE'
    
    @classmethod
    def to_list(cls) -> list[str]:
        # sort unsorted_names by the first letter of the name case insensitive
        
        return [member.name for member in cls].sort(key=lambda name: name[0].lower())


MAP_ACCOUNT_TYPE_TO_SIDE = {
    AccountTypeEnum.CASH.name: NormalSideEnum.DEBIT.name,
    AccountTypeEnum.CASH_OVERDRAFT.name: NormalSideEnum.CREDIT.name,
    AccountTypeEnum.SALARY_REVENUE.name: NormalSideEnum.CREDIT.name,
    AccountTypeEnum.ACCOUNT_RECEIVABLE.name: NormalSideEnum.DEBIT.name,
    AccountTypeEnum.SALARY_RECEIVABLE.name: NormalSideEnum.DEBIT.name,
    AccountTypeEnum.SALARY_DEFERRED_REVENUE.name: NormalSideEnum.CREDIT.name,
    AccountTypeEnum.ACCOUNT_PAYABLE.name: NormalSideEnum.CREDIT.name,
    AccountTypeEnum.LOAN.name: NormalSideEnum.CREDIT.name,
    AccountTypeEnum.CREDIT_CARD.name: NormalSideEnum.CREDIT.name,
    AccountTypeEnum.SALARY_TAX.name: NormalSideEnum.DEBIT.name,
    AccountTypeEnum.SALARY_EXPENSE.name: NormalSideEnum.DEBIT.name,
    AccountTypeEnum.AMORTIZATION_EXPENSE.name: NormalSideEnum.DEBIT.name,
}

# TODO: Expose the LOCAL_TIME_ZONE as a setting, and in a bottom bar (to the right corner)
LOCAL_TIME_ZONE = os.environ.get('LOCAL_TIME_ZONE', 'America/Argentina/Buenos_Aires')
