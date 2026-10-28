from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models
from app.database import Base, engine
from app.routers import accounts, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Transaction Ledger API",
    description="A simple API for accounts, transactions, balances, and transaction history.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(accounts.router)
app.include_router(transactions.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"message": "Transaction Ledger API is running"}
