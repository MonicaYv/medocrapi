from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from datetime import datetime
import uuid
from decimal import Decimal

from app.database import get_db
from app.models import WalletTransaction, RewardHistory
from app.schemas import WalletAddBalance, WalletBalanceOut, WalletHistoryOut, WalletTransactionOut
from app.profile.user_auth import get_current_user_object, check_authorization_key

router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"]
)


@router.get("/balance", response_model=WalletBalanceOut)
async def get_balance(
    current_user = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, profile = current_user
    result = await db.execute(
        select(WalletTransaction).where(WalletTransaction.user_id == user.id).order_by(desc(WalletTransaction.created_at)).limit(1)
    )
    last_txn = result.scalars().first()
    balance = last_txn.current_balance if last_txn else Decimal("0.00")
    return WalletBalanceOut(
        user_name = profile.first_name + profile.last_name,
        balance=balance, 
        last_updated=last_txn.created_at if last_txn else datetime.utcnow()
        )


@router.post("/add_balance", response_model=WalletTransactionOut)
async def add_balance(
    payload: WalletAddBalance,
    current_user = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, _ = current_user
    result = await db.execute(
        select(WalletTransaction).where(WalletTransaction.user_id == user.id).order_by(desc(WalletTransaction.created_at)).limit(1)
    )
    last_txn = result.scalars().first()
    prev_balance = last_txn.current_balance if last_txn else Decimal("0.00")

    new_balance = prev_balance + payload.amount
    points = payload.amount * Decimal("10") / Decimal("100")  # earning 10 points per 100 currency

    txn = WalletTransaction(
        user_id=user.id,
        order_id=payload.order_id,
        tranx_id=str(uuid.uuid4()),
        amount=payload.amount,
        transaction_type="Payment",
        points_earned=points,
        current_balance=new_balance
    )
    db.add(txn)
    await db.flush()
    reward = RewardHistory(
        user_id=user.id,
        action_type_id=10,
        points=int(points),  # if you want to store only integer points
        timestamp=datetime.now()
    )
    db.add(reward)    
    await db.commit()
    await db.refresh(txn)
    return txn


@router.get("/transaction_history", response_model=WalletHistoryOut)
async def transaction_history(
    current_user = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, _ = current_user
    result = await db.execute(
        select(WalletTransaction).where(WalletTransaction.user_id == user.id).order_by(desc(WalletTransaction.created_at))
    )
    txns = result.scalars().all()
    return WalletHistoryOut(transactions=txns, total=len(txns))
