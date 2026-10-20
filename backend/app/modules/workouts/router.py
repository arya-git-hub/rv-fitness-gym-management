from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Query as SQLAlchemyQuery
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.all_models import Member, Profile, Trainer, WorkoutPlan
from app.modules.workouts.schemas import (
    WorkoutMeRead,
    WorkoutOptions,
    WorkoutPlanPage,
    WorkoutPlanRead,
    WorkoutPlanWrite,
)
from app.modules.workouts.service import (
    apply_search,
    exercise_models,
    get_member_for_profile,
    get_trainer_for_profile,
    member_options,
    plan_query,
    serialize_plan,
    trainer_options,
)

optional_bearer = HTTPBearer(auto_error=False)


def require_authentication_header(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication is required.")


router = APIRouter(
    prefix="/workouts",
    tags=["Workouts"],
    dependencies=[Depends(require_authentication_header)],
)


def _require_member(db: Session, profile: Profile) -> Member:
    member = get_member_for_profile(db, profile)
    if not member:
        raise HTTPException(status_code=403, detail="This account is not linked to a member.")
    return member


def _require_trainer(db: Session, profile: Profile) -> Trainer:
    trainer = get_trainer_for_profile(db, profile)
    if not trainer or trainer.status != "active":
        raise HTTPException(status_code=403, detail="This account is not linked to an active trainer.")
    return trainer


def _accessible_plan_query(db: Session, profile: Profile) -> SQLAlchemyQuery[WorkoutPlan]:
    query = plan_query(db)
    if profile.role == "admin":
        return query
    if profile.role == "trainer":
        trainer = _require_trainer(db, profile)
        return query.filter(WorkoutPlan.trainer_id == trainer.id)
    member = _require_member(db, profile)
    return query.filter(WorkoutPlan.member_id == member.id)


def _validate_assignment(
    db: Session, profile: Profile, member_id: str, trainer_id: str | None
) -> tuple[Member, Trainer]:
    member = db.query(Member).options(joinedload(Member.profile)).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found.")

    if profile.role == "trainer":
        trainer = _require_trainer(db, profile)
        if member.trainer_id != trainer.id:
            raise HTTPException(status_code=403, detail="You can create plans only for your assigned members.")
        return member, trainer

    if not trainer_id:
        raise HTTPException(status_code=422, detail="Select a trainer for this workout plan.")
    trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
    if not trainer or trainer.status != "active":
        raise HTTPException(status_code=404, detail="Active trainer not found.")
    return member, trainer


@router.get("/me", response_model=WorkoutMeRead)
def get_workout_user(
    profile: Profile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    member = get_member_for_profile(db, profile) if profile.role == "member" else None
    trainer = get_trainer_for_profile(db, profile) if profile.role == "trainer" else None
    if profile.role == "member" and not member:
        raise HTTPException(status_code=403, detail="This account is not linked to a member.")
    if profile.role == "trainer" and not trainer:
        raise HTTPException(status_code=403, detail="This account is not linked to a trainer.")
    return WorkoutMeRead(
        id=profile.id,
        full_name=profile.full_name,
        role=profile.role,
        member_id=member.id if member else None,
        trainer_id=trainer.id if trainer else None,
    )


@router.get("/options", response_model=WorkoutOptions)
def get_workout_options(
    profile: Profile = Depends(require_role("admin", "trainer")),
    db: Session = Depends(get_db),
):
    member_query = db.query(Member).options(joinedload(Member.profile))
    trainer_query = db.query(Trainer).options(joinedload(Trainer.profile)).filter(Trainer.status == "active")
    if profile.role == "trainer":
        trainer = _require_trainer(db, profile)
        member_query = member_query.filter(Member.trainer_id == trainer.id)
        trainer_query = trainer_query.filter(Trainer.id == trainer.id)
    members = member_query.order_by(Member.member_code).all()
    trainers = trainer_query.order_by(Trainer.id).all()
    return WorkoutOptions(members=member_options(members), trainers=trainer_options(trainers))


@router.get("", response_model=WorkoutPlanPage)
def list_workout_plans(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None, max_length=100),
    member_id: str | None = Query(default=None),
    profile: Profile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = _accessible_plan_query(db, profile)
    if member_id:
        query = query.filter(WorkoutPlan.member_id == member_id)
    query = apply_search(query, search)
    total = query.count()
    plans = (
        query.order_by(WorkoutPlan.created_at.desc(), WorkoutPlan.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [serialize_plan(plan) for plan in plans],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.get("/{plan_id}", response_model=WorkoutPlanRead)
def get_workout_plan(
    plan_id: str,
    profile: Profile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = _accessible_plan_query(db, profile).filter(WorkoutPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found.")
    return serialize_plan(plan)


@router.post("", response_model=WorkoutPlanRead, status_code=status.HTTP_201_CREATED)
def create_workout_plan(
    payload: WorkoutPlanWrite,
    profile: Profile = Depends(require_role("admin", "trainer")),
    db: Session = Depends(get_db),
):
    member, trainer = _validate_assignment(db, profile, payload.member_id, payload.trainer_id)
    plan = WorkoutPlan(
        member_id=member.id,
        trainer_id=trainer.id,
        title=payload.title.strip(),
        notes=payload.notes.strip() if payload.notes else None,
        exercises=exercise_models(payload.exercises),
    )
    db.add(plan)
    db.commit()
    plan = plan_query(db).filter(WorkoutPlan.id == plan.id).first()
    return serialize_plan(plan)


@router.put("/{plan_id}", response_model=WorkoutPlanRead)
def update_workout_plan(
    plan_id: str,
    payload: WorkoutPlanWrite,
    profile: Profile = Depends(require_role("admin", "trainer")),
    db: Session = Depends(get_db),
):
    plan = _accessible_plan_query(db, profile).filter(WorkoutPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found.")

    member, trainer = _validate_assignment(db, profile, payload.member_id, payload.trainer_id)
    plan.member_id = member.id
    plan.trainer_id = trainer.id
    plan.title = payload.title.strip()
    plan.notes = payload.notes.strip() if payload.notes else None
    plan.exercises = exercise_models(payload.exercises)
    db.commit()
    plan = plan_query(db).filter(WorkoutPlan.id == plan.id).first()
    return serialize_plan(plan)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout_plan(
    plan_id: str,
    profile: Profile = Depends(require_role("admin", "trainer")),
    db: Session = Depends(get_db),
):
    plan = _accessible_plan_query(db, profile).filter(WorkoutPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found.")
    db.delete(plan)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
