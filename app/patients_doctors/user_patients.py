from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.database import get_db
from app.models import PatientProfile, User
from app.profile.user_auth import get_current_user_object
from app.schemas import PatientCreate, PatientResponse, PatientUpdate

router = APIRouter(
    prefix="/patients",
    tags=["Patient"]
)

@router.post("/add-patient", response_model=PatientResponse)
async def add_patient(
    patient_data: PatientCreate,
    current_user: tuple = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db)
):
    user, profile = current_user  

    new_patient = PatientProfile(
        user_id=user.id,
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        gender=patient_data.gender,
        age=patient_data.age,
        relation=patient_data.relation
    )
    
    db.add(new_patient)
    try:
        await db.commit()
        await db.refresh(new_patient)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return new_patient


# Get all patients of the current user
@router.get("/patient-list", response_model=List[PatientResponse])
async def patient_list(
    current_user: User = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db)
):
    user, profile = current_user
    result = await db.execute(
        select(PatientProfile).where(PatientProfile.user_id == user.id)
    )
    patients = result.scalars().all()
    return patients


# Update patient
@router.put("/update-patient/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate = Body(...), 
    current_user: User = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db)
):
    user, profile = current_user
    result = await db.execute(
        select(PatientProfile).where(
            PatientProfile.id == patient_id,
            PatientProfile.user_id == user.id
        )
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    update_fields = patient_data.dict(exclude_unset=True)
    if not update_fields:
        raise HTTPException(status_code=400, detail="No data provided for update")

    for key, value in update_fields.items():
        setattr(patient, key, value)

    await db.commit()
    await db.refresh(patient)
    return patient


# Delete patient
@router.delete("/remove-patient/{patient_id}")
async def remove_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db)
):
    user, profile = current_user
    result = await db.execute(
        select(PatientProfile).where(
            PatientProfile.id == patient_id,
            PatientProfile.user_id == user.id
        )
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    await db.delete(patient)
    await db.commit()
    return {"detail": "Patient deleted successfully"}