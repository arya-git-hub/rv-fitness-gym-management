from collections.abc import Sequence

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.all_models import (
    Member,
    Profile,
    Trainer,
    WorkoutExercise,
    WorkoutPlan,
)
from app.modules.workouts.schemas import (
    WorkoutExerciseRead,
    ExerciseWrite,
    WorkoutMemberOption,
    WorkoutPlanRead,
    WorkoutTrainerOption,
)


def get_member_for_profile(db: Session, profile: Profile) -> Member | None:
    return db.query(Member).filter(Member.profile_id == profile.id).first()


def get_trainer_for_profile(db: Session, profile: Profile) -> Trainer | None:
    return db.query(Trainer).filter(Trainer.profile_id == profile.id).first()


def plan_query(db: Session):
    return db.query(WorkoutPlan).options(
        joinedload(WorkoutPlan.member).joinedload(Member.profile),
        selectinload(WorkoutPlan.exercises),
    )


def serialize_plan(plan: WorkoutPlan) -> WorkoutPlanRead:
    return WorkoutPlanRead(
        id=plan.id,
        member_id=plan.member_id,
        member_name=plan.member.profile.full_name,
        member_code=plan.member.member_code,
        trainer_id=plan.trainer_id,
        title=plan.title,
        notes=plan.notes,
        created_at=plan.created_at,
        exercises=[
            WorkoutExerciseRead.model_validate(exercise)
            for exercise in plan.exercises
        ],
    )


def exercise_models(exercises: Sequence[ExerciseWrite]) -> list[WorkoutExercise]:
    return [
        WorkoutExercise(**exercise.model_dump())
        for exercise in exercises
    ]


def member_options(members: list[Member]) -> list[WorkoutMemberOption]:
    return [
        WorkoutMemberOption(
            id=member.id,
            member_code=member.member_code,
            full_name=member.profile.full_name,
            trainer_id=member.trainer_id,
        )
        for member in members
    ]


def trainer_options(trainers: list[Trainer]) -> list[WorkoutTrainerOption]:
    return [
        WorkoutTrainerOption(id=trainer.id, full_name=trainer.profile.full_name)
        for trainer in trainers
    ]


def apply_search(query, search: str | None):
    if search:
        pattern = f"%{search.strip()}%"
        query = (
            query.join(WorkoutPlan.member)
            .join(Member.profile)
            .filter(
                or_(
                    WorkoutPlan.title.ilike(pattern),
                    Member.member_code.ilike(pattern),
                    Profile.full_name.ilike(pattern),
                )
            )
        )
    return query
