from math import ceil
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account, Transaction
from app.schemas import TransactionCreate, TransactionHistoryResponse, TransactionResponse
from app.services.ledger import create_transaction

router = APIRouter(tags=["Transactions"])


@router.post("/accounts/{account_id}/transactions", response_model=TransactionResponse, status_code=201)
def add_transaction(account_id: int, data: TransactionCreate, db: Session = Depends(get_db)):
    return create_transaction(db, account_id, data)


@router.get("/accounts/{account_id}/transactions", response_model=TransactionHistoryResponse)
def get_transaction_history(
    account_id: int,
    type: Literal["credit", "debit"] | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    account_exists = db.scalar(select(Account.id).where(Account.id == account_id))
    if account_exists is None:
        raise HTTPException(status_code=404, detail="Account not found")

    filters = [Transaction.account_id == account_id]
    if type is not None:
        filters.append(Transaction.type == type)

    total_records = db.scalar(
        select(func.count(Transaction.id)).where(*filters)
    ) or 0

    transactions = db.scalars(
        select(Transaction)
        .where(*filters)
        .order_by(Transaction.created_at.desc(), Transaction.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    return TransactionHistoryResponse(
        items=transactions,
        page=page,
        page_size=limit,
        total_records=total_records,
        total_pages=ceil(total_records / limit),
    )
