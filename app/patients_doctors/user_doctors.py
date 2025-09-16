from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, update, delete
from typing import List, Optional
from app.database import get_db
from app.models import DoctorProfile, UserProfile, HealthIssues
from app.schemas import DoctorProfileCreate, DoctorProfileOut, DoctorProfileUpdate, HealthIssueOut
from app.config import AUTHORIZATION_KEY
from app.routers.user_auth import get_current_user_object

router = APIRouter(
    prefix="/doctors",
    tags=["Patient Doctors"]
)

def check_authorization_key(authorization_key: str = Header(...)):
    if authorization_key != AUTHORIZATION_KEY:
        raise HTTPException(status_code=401, detail="Invalid authorization key")
    return authorization_key



# ========== DOCTOR MANAGEMENT APIs ==========
@router.post("/add_doctor", response_model=DoctorProfileOut)

async def add_doctor(
    doctor_data: DoctorProfileCreate,
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Add a new doctor for the current user"""
    try:
        # Check if doctor already exists for this user (by name and specialization)
        existing_doctor = await db.execute(
            select(DoctorProfile).where(
                and_(
                    DoctorProfile.user_id == current_user.id,
                    DoctorProfile.first_name == doctor_data.first_name,
                    DoctorProfile.last_name == doctor_data.last_name,
                    DoctorProfile.specialties == doctor_data.specialties
                )
            )
        )
        if existing_doctor.scalars().first():
            raise HTTPException(status_code=409, detail="Doctor with same name and specialization already exists")

        # Create new doctor profile
        new_doctor = DoctorProfile(
            user_id=current_user.id,
            first_name=doctor_data.first_name,
            last_name=doctor_data.last_name,
            gender=doctor_data.gender,
            age=doctor_data.age,
            specialties=doctor_data.specialties
        )

        db.add(new_doctor)
        await db.commit()
        await db.refresh(new_doctor)
        return new_doctor

    except Exception as e:
        await db.rollback()
        print(f"Error adding doctor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add doctor: {str(e)}")

# Get all doctors for the current user
@router.get("/get_doctors", response_model=List[DoctorProfileOut])
async def get_doctors(
    search_text: Optional[str] = Query(None, description="Search in doctor name or specialties"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    specialties: Optional[str] = Query(None, description="Filter by specialties"),
    limit: Optional[int] = Query(50, description="Number of records to return"),
    offset: Optional[int] = Query(0, description="Number of records to skip"),
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Get all doctors for the current user with optional filters"""
    try:
        # Base query for current user's doctors
        query = select(DoctorProfile).where(DoctorProfile.user_id == current_user.id)
        
        # Apply filters
        filters = []
        
        if search_text:
            search_condition = (
                DoctorProfile.first_name.ilike(f"%{search_text}%") |
                DoctorProfile.last_name.ilike(f"%{search_text}%") |
                DoctorProfile.specialties.ilike(f"%{search_text}%")
            )
            filters.append(search_condition)
        
        if gender:
            filters.append(DoctorProfile.gender.ilike(f"%{gender}%"))
        
        if specialties:
            filters.append(DoctorProfile.specialties.ilike(f"%{specialties}%"))
        
        if filters:
            query = query.where(and_(*filters))
        
        # Apply ordering, limit, and offset
        query = query.order_by(DoctorProfile.first_name.asc()).offset(offset).limit(limit)
        
        result = await db.execute(query)
        doctors = result.scalars().all()
        
        print(f"Found {len(doctors)} doctors for user {current_user.id}")
        return doctors

    except Exception as e:
        print(f"Error getting doctors: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get doctors: {str(e)}")

# Update doctor information
@router.put("/update_doctor/{doctor_id}", response_model=DoctorProfileOut)
async def update_doctor(
    doctor_id: int,
    doctor_data: DoctorProfileUpdate,
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Update doctor information"""
    try:
        # Check if doctor exists and belongs to current user
        doctor_query = await db.execute(
            select(DoctorProfile).where(
                and_(
                    DoctorProfile.id == doctor_id,
                    DoctorProfile.user_id == current_user.id
                )
            )
        )
        doctor = doctor_query.scalars().first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found or not authorized")

        # Update only provided fields
        update_data = doctor_data.dict(exclude_unset=True)
        if update_data:
            await db.execute(
                update(DoctorProfile)
                .where(DoctorProfile.id == doctor_id)
                .values(**update_data)
            )
            await db.commit()
            await db.refresh(doctor)

        return doctor

    except Exception as e:
        await db.rollback()
        print(f"Error updating doctor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update doctor: {str(e)}")

# Delete doctor
@router.delete("/delete_doctor/{doctor_id}")
async def delete_doctor(
    doctor_id: int,
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Delete a doctor"""
    try:
        # Check if doctor exists and belongs to current user
        doctor_query = await db.execute(
            select(DoctorProfile).where(
                and_(
                    DoctorProfile.id == doctor_id,
                    DoctorProfile.user_id == current_user.id
                )
            )
        )
        doctor = doctor_query.scalars().first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found or not authorized")

        # Permanently delete the doctor
        await db.execute(
            delete(DoctorProfile).where(DoctorProfile.id == doctor_id)
        )
        await db.commit()
        
        return {"message": "Doctor deleted successfully"}

    except Exception as e:
        await db.rollback()
        print(f"Error deleting doctor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete doctor: {str(e)}")

# Get single doctor details
@router.get("/get_doctor/{doctor_id}", response_model=DoctorProfileOut)
async def get_doctor(
    doctor_id: int,
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Get single doctor details"""
    try:
        doctor_query = await db.execute(
            select(DoctorProfile).where(
                and_(
                    DoctorProfile.id == doctor_id,
                    DoctorProfile.user_id == current_user.id
                )
            )
        )
        doctor = doctor_query.scalars().first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found or not authorized")

        return doctor

    except Exception as e:
        print(f"Error getting doctor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get doctor: {str(e)}")

@router.get("/get_health_issues", response_model=List[HealthIssueOut])
async def get_health_issues(
    db: AsyncSession = Depends(get_db), 
    _auth=Depends(check_authorization_key)):
    """Get list of common health issues"""
    try:
        result = await db.execute(select(HealthIssues).order_by(HealthIssues.name.asc()))
        health_issues = result.scalars().all()
        return health_issues
    except Exception as e:
        print(f"Error getting health issues: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get health issues: {str(e)}")