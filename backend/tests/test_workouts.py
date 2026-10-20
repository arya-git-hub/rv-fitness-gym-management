from datetime import date

import pytest

from app.core.security import get_current_user
from app.main import app
from app.models.all_models import Member, Profile, Trainer, WorkoutExercise, WorkoutPlan
from app.modules.workouts.router import require_authentication_header


def make_profile(db_session, profile_id, role, name):
    profile = Profile(
        id=profile_id,
        full_name=name,
        email=f"{profile_id}@example.com",
        role=role,
        is_active=True,
    )
    db_session.add(profile)
    db_session.flush()
    return profile


def make_trainer(db_session, trainer_id, profile_id, name="Coach"):
    profile = make_profile(db_session, profile_id, "trainer", name)
    trainer = Trainer(
        id=trainer_id,
        profile_id=profile.id,
        mobile="9876543210",
        status="active",
    )
    db_session.add(trainer)
    db_session.flush()
    return trainer


def make_member(db_session, member_id, profile_id, trainer_id, code, name):
    profile = make_profile(db_session, profile_id, "member", name)
    member = Member(
        id=member_id,
        member_code=code,
        profile_id=profile.id,
        mobile="9876543210",
        joining_date=date(2026, 1, 1),
        status="active",
        trainer_id=trainer_id,
    )
    db_session.add(member)
    db_session.flush()
    return member


def authenticate_as(profile):
    app.dependency_overrides[get_current_user] = lambda: profile
    app.dependency_overrides[require_authentication_header] = lambda: None


@pytest.fixture(autouse=True)
def clear_auth_override():
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(require_authentication_header, None)
    yield
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(require_authentication_header, None)


def plan_payload(member_id, trainer_id=None, title="Strength", exercise="Squat"):
    return {
        "member_id": member_id,
        "trainer_id": trainer_id,
        "title": title,
        "notes": "Build strength",
        "exercises": [
            {
                "workout_day": "Monday",
                "exercise_name": exercise,
                "muscle_group": "Legs",
                "sets": 3,
                "reps": "10",
                "duration": None,
                "rest_time": "60 sec",
                "instructions": None,
            }
        ],
    }


def test_workout_routes_require_authentication(client):
    response = client.get("/api/workouts")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication is required."}


def test_member_only_sees_own_plans(client, db_session):
    trainer = make_trainer(db_session, "trainer-1", "trainer-profile-1")
    member = make_member(db_session, "member-1", "member-profile-1", trainer.id, "RVF-0001", "Asha")
    other_member = make_member(db_session, "member-2", "member-profile-2", trainer.id, "RVF-0002", "Ravi")
    db_session.add_all(
        [
            WorkoutPlan(id="plan-1", member_id=member.id, trainer_id=trainer.id, title="My plan"),
            WorkoutPlan(id="plan-2", member_id=other_member.id, trainer_id=trainer.id, title="Other plan"),
        ]
    )
    db_session.commit()
    authenticate_as(member.profile)

    response = client.get("/api/workouts")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["title"] == "My plan"
    assert response.json()["items"][0]["member_name"] == "Asha"


def test_trainer_can_create_plan_for_assigned_member(client, db_session):
    trainer = make_trainer(db_session, "trainer-1", "trainer-profile-1")
    member = make_member(db_session, "member-1", "member-profile-1", trainer.id, "RVF-0001", "Asha")
    authenticate_as(trainer.profile)

    response = client.post("/api/workouts", json=plan_payload(member.id))

    assert response.status_code == 201
    plan = response.json()
    assert plan["member_id"] == member.id
    assert plan["trainer_id"] == trainer.id
    assert plan["exercises"][0]["exercise_name"] == "Squat"


def test_trainer_cannot_create_plan_for_unassigned_member(client, db_session):
    trainer = make_trainer(db_session, "trainer-1", "trainer-profile-1")
    other_trainer = make_trainer(db_session, "trainer-2", "trainer-profile-2", "Other coach")
    member = make_member(
        db_session, "member-1", "member-profile-1", other_trainer.id, "RVF-0001", "Asha"
    )
    authenticate_as(trainer.profile)

    response = client.post("/api/workouts", json=plan_payload(member.id))

    assert response.status_code == 403


def test_member_cannot_modify_workout_plan(client, db_session):
    trainer = make_trainer(db_session, "trainer-1", "trainer-profile-1")
    member = make_member(db_session, "member-1", "member-profile-1", trainer.id, "RVF-0001", "Asha")
    plan = WorkoutPlan(id="plan-1", member_id=member.id, trainer_id=trainer.id, title="Original")
    db_session.add(plan)
    db_session.commit()
    authenticate_as(member.profile)

    response = client.delete(f"/api/workouts/{plan.id}")

    assert response.status_code == 403
    assert db_session.query(WorkoutPlan).filter_by(id=plan.id).first() is not None


def test_update_replaces_exercises_and_search_paginates(client, db_session):
    admin = make_profile(db_session, "admin-1", "admin", "Gym admin")
    trainer = make_trainer(db_session, "trainer-1", "trainer-profile-1")
    member = make_member(db_session, "member-1", "member-profile-1", trainer.id, "RVF-0001", "Asha")
    plan = WorkoutPlan(id="plan-1", member_id=member.id, trainer_id=trainer.id, title="Strength")
    db_session.add(plan)
    db_session.commit()
    authenticate_as(admin)

    response = client.put(
        f"/api/workouts/{plan.id}",
        json=plan_payload(member.id, trainer.id, "Updated", "Deadlift"),
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"
    assert [item["exercise_name"] for item in response.json()["exercises"]] == ["Deadlift"]

    response = client.get("/api/workouts?search=Updated&page=1&page_size=1")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["page_size"] == 1

    response = client.delete(f"/api/workouts/{plan.id}")
    assert response.status_code == 204
    assert db_session.query(WorkoutPlan).filter_by(id=plan.id).first() is None
    assert db_session.query(WorkoutExercise).filter_by(plan_id=plan.id).count() == 0


def test_invalid_exercise_data_returns_validation_error(client, db_session):
    trainer = make_trainer(db_session, "trainer-1", "trainer-profile-1")
    member = make_member(db_session, "member-1", "member-profile-1", trainer.id, "RVF-0001", "Asha")
    authenticate_as(trainer.profile)
    payload = plan_payload(member.id)
    payload["exercises"][0]["sets"] = 0

    response = client.post("/api/workouts", json=payload)

    assert response.status_code == 422

    payload = plan_payload(member.id)
    payload["title"] = "   "
    response = client.post("/api/workouts", json=payload)

    assert response.status_code == 422


def test_trainer_lookup_fails_without_linked_trainer(client, db_session):
    profile = make_profile(db_session, "orphan-trainer", "trainer", "Orphan")
    authenticate_as(profile)

    response = client.get("/api/workouts")

    assert response.status_code == 403
