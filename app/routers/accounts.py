from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account
from app.schemas import AccountCreate, AccountResponse, BalanceResponse

router = APIRouter(tags=["Accounts"])


@router.post("/accounts", response_model=AccountResponse, status_code=201)
def create_account(data: AccountCreate, db: Session = Depends(get_db)):
    account = Account(name=data.name, balance=0)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/accounts/{account_id}/balance", response_model=BalanceResponse)
def get_account_balance(account_id: int, db: Session = Depends(get_db)):
    account = db.scalar(select(Account).where(Account.id == account_id))
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return BalanceResponse(account_id=account.id, balance=float(account.balance))
