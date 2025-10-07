from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from sqlalchemy import update
from app.database import get_db
from app.models import (
    DoctorAppointment, HealthIssue, Specialization,
    AppointmentHealthIssues, AppointmentSpecializations, UserAddress
)
from app.schemas import (
    DoctorAppointmentCreate, DoctorAppointmentResponse, DoctorAppointmentUpdate
)
from app.profile.user_auth import get_current_user_object

router = APIRouter(
    prefix="/doctor/appointment",
    tags=["Doctor Appointment"]
)

def appointment_to_response(appointment: DoctorAppointment) -> DoctorAppointmentResponse:
    return DoctorAppointmentResponse.from_orm(appointment)

# 1. Book Appointment (POST)
@router.post("/", response_model=DoctorAppointmentResponse)
async def book_appointment(
    data: DoctorAppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_object)
):
    user, _ = current_user

    # 1️Create the appointment
    appointment = DoctorAppointment(
        user_id=user.id,
        address_id=data.address_id,
        description=data.description,
        consultation_type=data.consultation_type,
        service_type=data.service_type,
        preferred_date_time=data.preferred_date_time,
        budget=data.budget,
        status="Pending"
    )
    db.add(appointment)
    await db.flush()  
    for issue_id in data.health_issues or []:
        db.add(AppointmentHealthIssues(
            appointment_id=appointment.id,
            health_issue_id=issue_id
        ))

    for spec_id in data.specialization_ids or []:
        db.add(AppointmentSpecializations(
            appointment_id=appointment.id,
            specialization_id=spec_id
        ))
    await db.commit()
    await db.refresh(appointment)
    
    result = await db.execute(
        select(DoctorAppointment)
        .where(DoctorAppointment.id == appointment.id)
        .options(
            selectinload(DoctorAppointment.address),
            selectinload(DoctorAppointment.health_issues),
            selectinload(DoctorAppointment.specializations)
        )
    )
    appointment = result.scalar_one()

    return appointment_to_response(appointment)

# 2. Get dropdown values (GET)
@router.get("/dropdowns")
async def get_dropdowns(db: AsyncSession = Depends(get_db)):
    health_issues = (await db.execute(select(HealthIssue))).scalars().all()
    specializations = (await db.execute(select(Specialization))).scalars().all()
    return {
        "health_issues": [{"id": h.id, "name": h.name} for h in health_issues],
        "specializations": [{"id": s.id, "name": s.name} for s in specializations]
    }


# 1. Appointment List
@router.get("/", response_model=List[DoctorAppointmentResponse])
async def appointment_list(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_object)
):
    user, profile = current_user

    result = await db.execute(
        select(DoctorAppointment)
        .where(DoctorAppointment.user_id == user.id)
        .options(
            selectinload(DoctorAppointment.address),
            selectinload(DoctorAppointment.health_issues),
            selectinload(DoctorAppointment.specializations)
        )
    )
    appointments = result.scalars().all()
    return [appointment_to_response(appt) for appt in appointments]


# 2. Appointment History
@router.get("/history", response_model=List[DoctorAppointmentResponse])
async def appointment_history(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_object)
):
    user, profile = current_user
    result = await db.execute(
        select(DoctorAppointment)
        .where(
            DoctorAppointment.user_id == user.id,
            DoctorAppointment.status.in_(["Completed", "Cancelled", "Pending"])
        )
        .options(
            selectinload(DoctorAppointment.address),
            selectinload(DoctorAppointment.health_issues),
            selectinload(DoctorAppointment.specializations)
        )
    )
    appointments = result.scalars().all()
    return [appointment_to_response(a) for a in appointments]


# 3. Appointment Info
@router.get("/{appointment_id}", response_model=DoctorAppointmentResponse)
async def appointment_info(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_object)
):
    user, profile = current_user
    result = await db.execute(
        select(DoctorAppointment)
        .where(
            DoctorAppointment.id == appointment_id,
            DoctorAppointment.user_id == user.id
        )
        .options(
            selectinload(DoctorAppointment.address),
            selectinload(DoctorAppointment.health_issues),
            selectinload(DoctorAppointment.specializations)
        )
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment_to_response(appointment)


# 4. Update Appointment
@router.put("/{appointment_id}", response_model=DoctorAppointmentResponse)
async def update_appointment(
    appointment_id: int,
    data: DoctorAppointmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_object)
):
    user, profile = current_user

    result = await db.execute(
        select(DoctorAppointment)
        .where(
            DoctorAppointment.id == appointment_id,
            DoctorAppointment.user_id == user.id
        )
        .options(
            selectinload(DoctorAppointment.address),
            selectinload(DoctorAppointment.health_issues),
            selectinload(DoctorAppointment.specializations)
        )
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    update_data = data.dict(exclude_unset=True)

    scalar_fields = {
        k: v for k, v in update_data.items()
        if k not in ["health_issues", "specialization_ids"]
    }
    if scalar_fields:
        await db.execute(
            update(DoctorAppointment)
            .where(
                DoctorAppointment.id == appointment_id,
                DoctorAppointment.user_id == user.id
            )
            .values(**scalar_fields)
        )

    if "health_issues" in update_data:
        await db.execute(
            AppointmentHealthIssues.__table__.delete().where(
                AppointmentHealthIssues.appointment_id == appointment_id
            )
        )
        for issue_id in update_data["health_issues"]:
            db.add(AppointmentHealthIssues(
                appointment_id=appointment_id,
                health_issue_id=issue_id
            ))

    if "specialization_ids" in update_data:
        await db.execute(
            AppointmentSpecializations.__table__.delete().where(
                AppointmentSpecializations.appointment_id == appointment_id
            )
        )
        for spec_id in update_data["specialization_ids"]:
            db.add(AppointmentSpecializations(
                appointment_id=appointment_id,
                specialization_id=spec_id
            ))

    if "address_id" in update_data:
        addr_result = await db.execute(
            select(UserAddress).where(
                UserAddress.id == update_data["address_id"],
                UserAddress.user_profile_id == profile.id  # ensure address belongs to this user
            )
        )
        address = addr_result.scalar_one_or_none()
        if not address:
            raise HTTPException(
                status_code=400,
                detail=f"Address {update_data['address_id']} does not exist or does not belong to you"
            )

    await db.commit()
    await db.refresh(appointment)
    return appointment_to_response(appointment)


# 5. Cancel Appointment
@router.put("/{appointment_id}/cancel", response_model=DoctorAppointmentResponse)
async def cancel_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_object)
):
    user, profile = current_user
    result = await db.execute(
        select(DoctorAppointment)
        .where(
            DoctorAppointment.id == appointment_id,
            DoctorAppointment.user_id == user.id
        )
        .options(
            selectinload(DoctorAppointment.address),
            selectinload(DoctorAppointment.health_issues),
            selectinload(DoctorAppointment.specializations)
        )
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = "Cancelled"
    await db.commit()
    await db.refresh(appointment)
    return appointment_to_response(appointment)
