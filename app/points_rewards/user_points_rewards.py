from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models import PointsBadge, CouponHistory, UserProfile, RewardHistory, PointsActionType
from app.schemas import PointsBadgeOut, CouponHistoryOut, RewardHistoryOut, PointsActionTypeOut
from app.config import AUTHORIZATION_KEY
from app.routers.user_auth import get_current_user_object

# Response model for reward history with total points
class RewardHistoryResponse(BaseModel):
    reward_history: List[RewardHistoryOut]
    total_points: int
    filtered_total_points: int  # Total points for the applied filters

router = APIRouter(
    prefix="/points-rewards",
    tags=["Points & Rewards"]
)
 
def check_authorization_key(authorization_key: str = Header(...)):
    if authorization_key != AUTHORIZATION_KEY:
        raise HTTPException(status_code=401, detail="Invalid authorization key")
    return authorization_key

# GET /points-rewards/badge-list - Get all available badges
@router.get("/badge-list", response_model=List[PointsBadgeOut])
async def get_badge_list(
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Get all available badges with their point requirements"""
    try:
        query = select(PointsBadge).order_by(PointsBadge.min_points.asc())
        result = await db.execute(query)
        badges = result.scalars().all()
        
        # Debug: Print badge data to see what's in the database
        for badge in badges:
            print(f"Badge: {badge.name}, min_points: {badge.min_points}, max_points: {badge.max_points}")
        
        return badges
    except Exception as e:
        print(f"Error getting badge list: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get badge list: {str(e)}")

@router.get("/coupon-history", response_model=List[CouponHistoryOut])
async def get_coupon_history(
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    current_user: UserProfile = Depends(get_current_user_object)):

    try:
        query = select(CouponHistory).where(CouponHistory.user_id == current_user.id)
        result = await db.execute(query)
        coupon_history = result.scalars().all()
        return coupon_history
    except Exception as e:
        print(f"Error getting coupon history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get coupon history: {str(e)}")

@router.get("/reward-history", response_model=RewardHistoryResponse)
async def get_reward_history(
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    current_user: UserProfile = Depends(get_current_user_object),
    action_type_id: Optional[int] = Query(None, description="Filter by action type ID"), #category
    start_date: Optional[datetime] = Query(None, description="Filter from start date"),
    end_date: Optional[datetime] = Query(None, description="Filter until end date"),
    limit: Optional[int] = Query(50, description="Number of records to return"),
    offset: Optional[int] = Query(0, description="Number of records to skip")
):
    """Get user's reward history with optional filters and total points"""
    try:
        # Calculate total points for the user (all time)
        total_query = select(func.sum(RewardHistory.points)).where(
            RewardHistory.user_id == current_user.id
        )
        total_result = await db.execute(total_query)
        total_points = total_result.scalar() or 0
        
        # Build the base query for filtered data
        base_query = select(RewardHistory).where(RewardHistory.user_id == current_user.id)
        
        # Apply filters
        filters = []
        
        if action_type_id is not None:
            filters.append(RewardHistory.action_type_id == action_type_id)
            
        if start_date is not None:
            filters.append(RewardHistory.timestamp >= start_date)
            
        if end_date is not None:
            filters.append(RewardHistory.timestamp <= end_date)
        
        if filters:
            base_query = base_query.where(and_(*filters))
        
        # Calculate filtered total points
        filtered_total_query = select(func.sum(RewardHistory.points)).where(
            RewardHistory.user_id == current_user.id
        )
        if filters:
            filtered_total_query = filtered_total_query.where(and_(*filters))
        
        filtered_total_result = await db.execute(filtered_total_query)
        filtered_total_points = filtered_total_result.scalar() or 0
        
        # Get paginated reward history with action_type details
        query = base_query.options(
            selectinload(RewardHistory.action_type)
        ).order_by(RewardHistory.timestamp.desc()).offset(offset).limit(limit)
        
        result = await db.execute(query)
        reward_history = result.scalars().all()
        
        # Debug: Print reward history data
        print(f"Found {len(reward_history)} reward history records for user {current_user.id}")
        print(f"Total points (all time): {total_points}")
        print(f"Filtered total points: {filtered_total_points}")
        for reward in reward_history:
            print(f"Reward: {reward.id}, points: {reward.points}, action_type_id: {reward.action_type_id}, timestamp: {reward.timestamp}")
        
        return RewardHistoryResponse(
            reward_history=reward_history,
            total_points=total_points,
            filtered_total_points=filtered_total_points
        )
    except Exception as e:
        print(f"Error getting reward history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get reward history: {str(e)}")

@router.get("/points-actions", response_model=List[PointsActionTypeOut])
async def get_points_actions(
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Get all available points action types"""
    try:
        query = select(PointsActionType).order_by(PointsActionType.action_type.asc())
        result = await db.execute(query)
        action_types = result.scalars().all()
        
        # Debug: Print action types data
        print(f"Found {len(action_types)} action types")
        for action in action_types:
            print(f"Action: {action.action_type}, default_points: {action.default_points}")
        
        return action_types
    except Exception as e:
        print(f"Error getting points actions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get points actions: {str(e)}")