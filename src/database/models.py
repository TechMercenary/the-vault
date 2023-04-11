from sqlalchemy import DateTime, String, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing_extensions import Annotated
from decimal import Decimal
from sqlalchemy.orm import foreign, remote

# type_timestamp = Annotated[datetime, mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP()),]
# str_30 = Annotated[str, 30]
# num_6_2 = Annotated[Decimal, 6]
# amount_18_2 = Annotated[Decimal, 18, 2]

class Base(DeclarativeBase):
    pass


class Provider(Base):
    __tablename__ = "provider"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[str|None] = mapped_column(nullable=False, default="")
    

class Currency(Base):
    __tablename__ = "currency"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(3), nullable=False, unique=True)
    description: Mapped[str|None] = mapped_column(nullable=False, default="")


class AccountGroup(Base):
    __tablename__ = "account_group"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[str|None] = mapped_column(nullable=False, default="")
    parent_id : Mapped[int|None] = mapped_column(ForeignKey("account_group.id"))

    parent: Mapped["AccountGroup"] = relationship("AccountGroup", remote_side="AccountGroup.id", back_populates="children")
    children: Mapped[list["AccountGroup"]] = relationship("AccountGroup", back_populates="parent")
    accounts: Mapped[list["Account"]] = relationship(back_populates="account_group")

    @property
    def alias(self):
        if self.parent_id is not None:
            return f"{self.parent.alias}>{self.name}"
        return self.name


class AccountType(Base):
    """
        normal_side: The normal side of the account type. It must be either "DEBIT" or "CREDIT"
    """
    __tablename__ = "account_type"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    normal_side: Mapped[str] = mapped_column(nullable=False)
    
    accounts: Mapped[list["Account"]] = relationship(back_populates="account_type")


class Account(Base):
    """
    Account model
        opened_at: The date the account was opened in UTC
        closed_at: The date the account was closed in UTC
        account_type: The formal accounting type of the account
    """
    __tablename__ = "account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str|None] = mapped_column(nullable=False, default="")
    account_number: Mapped[str|None] = mapped_column(nullable=False, default="")
    currency_id: Mapped[int] = mapped_column(ForeignKey("currency.id"))
    opened_at: Mapped[str]
    closed_at: Mapped[str|None]
    account_group_id: Mapped[int] = mapped_column(ForeignKey("account_group.id"))
    account_type_id: Mapped[int] = mapped_column(ForeignKey("account_type.id"))
    
    currency: Mapped["Currency"] = relationship("Currency")
    account_group: Mapped["AccountGroup"] = relationship(back_populates="accounts")
    account_type: Mapped["AccountType"] = relationship("AccountType", back_populates="accounts")
    account_overdrafts: Mapped[list["AccountOverdraft"]] = relationship("AccountOverdraft", back_populates="account")
    
    @property
    def alias(self):
        return f"{self.account_group.alias}>{self.name}"

    @property
    def overdraft_limit(self):
        return self.account_overdrafts[-1].limit if self.account_overdrafts else 0

class AccountOverdraft(Base):
    __tablename__ = "account_overdraft"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"))
    limit: Mapped[Decimal]
    started_at : Mapped[str]
    ended_at : Mapped[str|None]
    
    account = relationship("Account", back_populates="account_overdrafts")


class Transaction(Base):
    """
       Transaction model 
    """
    __tablename__ = "transaction"
    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[str]
    description: Mapped[str|None] = mapped_column(nullable=False, default="")
    installment_number: Mapped[int|None] = mapped_column(nullable=False, default=1)
    installment_total: Mapped[int|None] = mapped_column(nullable=False, default=1)
    debit_reference: Mapped[str|None] = mapped_column(nullable=False, default="")
    debit_account_id: Mapped[int] = mapped_column(ForeignKey("account.id"))
    debit_amount: Mapped[Decimal]
    credit_reference: Mapped[str|None] = mapped_column(nullable=False, default="")
    credit_account_id: Mapped[int] = mapped_column(ForeignKey("account.id"))
    credit_amount: Mapped[Decimal]
    is_reconciled: Mapped[bool] = mapped_column(nullable=False, default=False)
    
    debit_account = relationship("Account", foreign_keys=[debit_account_id])
    credit_account = relationship("Account", foreign_keys=[credit_account_id])
    


# TODO: Implement model Employer
# TODO: Implement model Salary
# TODO: Implement model CreditCard
# TODO: Implement model CreditCardSummary
# TODO: Implement model CreditCardSummaryBalance
# TODO: Implement model CreditCardSummaryTransaction
# TODO: Implement model FixedTerm (TBD)
# TODO: Implement model SupplyPurchase (TBD)
# TODO: Implement model SupplyConsumption (TBD)
# TODO: Implement model PhysicalAsset (TBD)
# TODO: Implement model Monotax (TBD)
# TODO: Implement model AFIPInvoice (TBD)

