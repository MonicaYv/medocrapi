from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, update, delete
from typing import List, Optional
from app.database import get_db
from app.models import DoctorProfile, UserProfile, HealthIssues, DoctorAppointment
from app.schemas import DoctorProfileCreate, DoctorProfileOut, DoctorProfileUpdate, HealthIssueOut, DoctorAppointmentOut
from app.profile.user_auth import get_current_user_object, check_authorization_key

router = APIRouter(
    prefix="/doctors",
    tags=["Patient Doctors"]
)

# ========== DOCTOR MANAGEMENT APIs ==========
@router.post("/add_doctor", response_model=DoctorProfileOut)

async def add_doctor(
    doctor_data: DoctorProfileCreate,
    current_user = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Add a new doctor for the current user"""
    user, profile = current_user
    try:
        # Check if doctor already exists for this user (by name and specialization)
        existing_doctor = await db.execute(
            select(DoctorProfile).where(
                and_(
                    DoctorProfile.user_id == user.id,
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
            user_id=user.id,
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
    current_user = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Get all doctors for the current user with optional filters"""
    user, profile = current_user
    try:
        # Base query for current user's doctors
        query = select(DoctorProfile).where(DoctorProfile.user_id == user.id)
        
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
        
        print(f"Found {len(doctors)} doctors for user {user.id}")
        return doctors

    except Exception as e:
        print(f"Error getting doctors: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get doctors: {str(e)}")

# Update doctor information
@router.put("/update_doctor/{doctor_id}", response_model=DoctorProfileOut)
async def update_doctor(
    doctor_id: int,
    doctor_data: DoctorProfileUpdate,
    current_user = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Update doctor information"""
    user, profile = current_user
    try:
        # Check if doctor exists and belongs to current user
        doctor_query = await db.execute(
            select(DoctorProfile).where(
                and_(
                    DoctorProfile.id == doctor_id,
                    DoctorProfile.user_id == user.id
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
    current_user = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Delete a doctor"""
    user, profile = current_user
    try:
        # Check if doctor exists and belongs to current user
        doctor_query = await db.execute(
            select(DoctorProfile).where(
                and_(
                    DoctorProfile.id == doctor_id,
                    DoctorProfile.user_id == user.id
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
    current_user = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Get single doctor details"""
    user, profile = current_user
    try:
        doctor_query = await db.execute(
            select(DoctorProfile).where(
                and_(
                    DoctorProfile.id == doctor_id,
                    DoctorProfile.user_id == user.id
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
    
# appoinments

@router.get("/appointment_list", response_model=List[DoctorAppointmentOut])
async def get_all_appointments(
    doctor_id: Optional[int] = Query(None, description="Filter by doctor ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    limit: Optional[int] = Query(50, description="Number of records to return"),
    offset: Optional[int] = Query(0, description="Number of records to skip"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_object),
    _auth=Depends(check_authorization_key)
):
    """Get all appointments with optional filters and pagination"""
    try:
        query = select(DoctorAppointment)
        filters = []
        if doctor_id:
            filters.append(DoctorAppointment.doctor_id == doctor_id)
        if user_id:
            filters.append(DoctorAppointment.user_id == user_id)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(DoctorAppointment.id.desc()).offset(offset).limit(limit)
        result = await db.execute(query)
        appointments = result.scalars().all()
        return appointments
    except Exception as e:
        print(f"Error getting appointments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get appointments: {str(e)}")

# ✅ Get appointment by ID

@router.get("/{appointment_id}", response_model=DoctorAppointmentOut)
async def get_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Get appointment by ID"""
    try:
        result = await db.execute(select(DoctorAppointment).where(DoctorAppointment.id == appointment_id))
        appointment = result.scalars().first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return appointment
    except Exception as e:
        print(f"Error getting appointment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get appointment: {str(e)}")


# ✅ Get appointments by Doctor ID
@router.get("/doctor/{doctor_id}", response_model=List[DoctorAppointmentOut])
async def get_appointments_by_doctor(
    doctor_id: str,  # <-- change to str
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    try:
        result = await db.execute(
            select(DoctorAppointment).where(DoctorAppointment.doctor_id == doctor_id)
        )
        appointments = result.scalars().all()
        if not appointments:
            raise HTTPException(status_code=404, detail="No appointments found for this doctor")
        return appointments
    except Exception as e:
        print(f"Error getting appointments by doctor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get appointments by doctor: {str(e)}")