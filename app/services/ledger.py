from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Account, Transaction
from app.schemas import TransactionCreate


def create_transaction(
    db: Session, account_id: int, data: TransactionCreate
) -> Transaction:
    account = db.scalar(
        select(Account).where(Account.id == account_id).with_for_update()
    )
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    amount = data.amount.quantize(Decimal("0.01"))
    current_balance = Decimal(account.balance)

    if data.type == "debit" and current_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    if data.type == "credit":
        account.balance = current_balance + amount
    else:
        account.balance = current_balance - amount

    transaction = Transaction(
        account_id=account_id,
        type=data.type,
        amount=amount,
        description=data.description,
        reference_id=f"txn_{uuid4().hex}",
    )
    db.add(transaction)

    try:
        db.commit()
        db.refresh(transaction)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Transaction could not be created",
        )

    return transaction
