"""
app/models/all_models.py
ALL SQLAlchemy models for RV Fitness.
Person B owns this file. Everyone else imports models from here.

Column naming: snake_case, same names as the DB schema in the spec.
Money columns use Numeric(10, 2) — never Float.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ---------------------------------------------------------------------------
# Helper: default UUID primary key
# ---------------------------------------------------------------------------
def _uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# profiles  (mirrors Supabase auth.users)
# ---------------------------------------------------------------------------
class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("admin", "trainer", "member", name="user_role"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships (back-populated by child tables)
    member: Mapped["Member"] = relationship("Member", back_populates="profile", uselist=False)
    trainer: Mapped["Trainer"] = relationship("Trainer", back_populates="profile", uselist=False)


# ---------------------------------------------------------------------------
# trainers
# ---------------------------------------------------------------------------
class Trainer(Base):
    __tablename__ = "trainers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    profile_id: Mapped[str] = mapped_column(String, ForeignKey("profiles.id"), unique=True, nullable=False)
    mobile: Mapped[str] = mapped_column(String(10), nullable=False)
    experience: Mapped[str | None] = mapped_column(String(255))
    specialization: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        Enum("active", "inactive", name="trainer_status"), default="active", nullable=False
    )
    photo_url: Mapped[str | None] = mapped_column(String)

    profile: Mapped["Profile"] = relationship("Profile", back_populates="trainer")
    members: Mapped[list["Member"]] = relationship("Member", back_populates="trainer")


# ---------------------------------------------------------------------------
# members
# ---------------------------------------------------------------------------
class Member(Base):
    __tablename__ = "members"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    member_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # RVF-0001
    profile_id: Mapped[str] = mapped_column(String, ForeignKey("profiles.id"), unique=True, nullable=False)
    dob: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(Enum("male", "female", "other", name="gender_enum"))
    mobile: Mapped[str] = mapped_column(String(10), nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    emergency_contact: Mapped[str | None] = mapped_column(String(200))
    joining_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("pending", "active", "inactive", name="member_status"), default="pending", nullable=False
    )
    trainer_id: Mapped[str | None] = mapped_column(String, ForeignKey("trainers.id"), nullable=True)
    weight: Mapped[float | None] = mapped_column(Numeric(5, 2))
    height: Mapped[float | None] = mapped_column(Numeric(5, 2))
    photo_url: Mapped[str | None] = mapped_column(String)

    profile: Mapped["Profile"] = relationship("Profile", back_populates="member")
    trainer: Mapped["Trainer"] = relationship("Trainer", back_populates="members")
    memberships: Mapped[list["Membership"]] = relationship("Membership", back_populates="member")
    invoices: Mapped[list["Invoice"]] = relationship("Invoice", back_populates="member")
    workout_plans: Mapped[list["WorkoutPlan"]] = relationship("WorkoutPlan", back_populates="member")
    diet_plans: Mapped[list["DietPlan"]] = relationship("DietPlan", back_populates="member")
    progress_records: Mapped[list["ProgressRecord"]] = relationship("ProgressRecord", back_populates="member")


# ---------------------------------------------------------------------------
# membership_plans
# ---------------------------------------------------------------------------
class MembershipPlan(Base):
    __tablename__ = "membership_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    benefits: Mapped[str | None] = mapped_column(Text)  # store as JSON string or newline-separated
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    memberships: Mapped[list["Membership"]] = relationship("Membership", back_populates="plan")


# ---------------------------------------------------------------------------
# memberships
# ---------------------------------------------------------------------------
class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    member_id: Mapped[str] = mapped_column(String, ForeignKey("members.id"), nullable=False)
    plan_id: Mapped[str] = mapped_column(String, ForeignKey("membership_plans.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("active", "expired", "cancelled", name="membership_status"), default="active", nullable=False
    )

    member: Mapped["Member"] = relationship("Member", back_populates="memberships")
    plan: Mapped["MembershipPlan"] = relationship("MembershipPlan", back_populates="memberships")
    invoices: Mapped[list["Invoice"]] = relationship("Invoice", back_populates="membership")


# ---------------------------------------------------------------------------
# invoices
# ---------------------------------------------------------------------------
class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    invoice_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    member_id: Mapped[str] = mapped_column(String, ForeignKey("members.id"), nullable=False)
    membership_id: Mapped[str | None] = mapped_column(String, ForeignKey("memberships.id"), nullable=True)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    tax: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    final_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("pending", "partially_paid", "paid", "overdue", "cancelled", name="invoice_status"),
        default="pending",
        nullable=False,
    )

    member: Mapped["Member"] = relationship("Member", back_populates="invoices")
    membership: Mapped["Membership"] = relationship("Membership", back_populates="invoices")
    items: Mapped[list["InvoiceItem"]] = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="invoice")


# ---------------------------------------------------------------------------
# invoice_items
# ---------------------------------------------------------------------------
class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    invoice_id: Mapped[str] = mapped_column(String, ForeignKey("invoices.id"), nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")


# ---------------------------------------------------------------------------
# payments
# ---------------------------------------------------------------------------
class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    invoice_id: Mapped[str] = mapped_column(String, ForeignKey("invoices.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    method: Mapped[str] = mapped_column(
        Enum("cash", "upi", "bank_transfer", "card", "other", name="payment_method"), nullable=False
    )
    reference_no: Mapped[str | None] = mapped_column(String(100))
    paid_on: Mapped[date] = mapped_column(Date, nullable=False)
    received_by: Mapped[str | None] = mapped_column(String, ForeignKey("profiles.id"), nullable=True)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payments")
    receipt: Mapped["Receipt"] = relationship("Receipt", back_populates="payment", uselist=False)


# ---------------------------------------------------------------------------
# receipts
# ---------------------------------------------------------------------------
class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    receipt_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    payment_id: Mapped[str] = mapped_column(String, ForeignKey("payments.id"), unique=True, nullable=False)
    issued_on: Mapped[date] = mapped_column(Date, nullable=False)

    payment: Mapped["Payment"] = relationship("Payment", back_populates="receipt")


# ---------------------------------------------------------------------------
# workout_plans
# ---------------------------------------------------------------------------
class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    member_id: Mapped[str] = mapped_column(String, ForeignKey("members.id"), nullable=False)
    trainer_id: Mapped[str] = mapped_column(String, ForeignKey("trainers.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    member: Mapped["Member"] = relationship("Member", back_populates="workout_plans")
    exercises: Mapped[list["WorkoutExercise"]] = relationship("WorkoutExercise", back_populates="plan", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# workout_exercises
# ---------------------------------------------------------------------------
class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    plan_id: Mapped[str] = mapped_column(String, ForeignKey("workout_plans.id"), nullable=False)
    workout_day: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "Monday", "Day 1"
    exercise_name: Mapped[str] = mapped_column(String(200), nullable=False)
    muscle_group: Mapped[str | None] = mapped_column(String(100))
    sets: Mapped[int | None] = mapped_column(Integer)
    reps: Mapped[str | None] = mapped_column(String(50))  # "10-12" or "failure"
    duration: Mapped[str | None] = mapped_column(String(50))  # "30 min"
    rest_time: Mapped[str | None] = mapped_column(String(50))  # "60 sec"
    instructions: Mapped[str | None] = mapped_column(Text)

    plan: Mapped["WorkoutPlan"] = relationship("WorkoutPlan", back_populates="exercises")


# ---------------------------------------------------------------------------
# diet_plans
# ---------------------------------------------------------------------------
class DietPlan(Base):
    __tablename__ = "diet_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    member_id: Mapped[str] = mapped_column(String, ForeignKey("members.id"), nullable=False)
    trainer_id: Mapped[str] = mapped_column(String, ForeignKey("trainers.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    member: Mapped["Member"] = relationship("Member", back_populates="diet_plans")
    items: Mapped[list["DietItem"]] = relationship("DietItem", back_populates="plan", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# diet_items
# ---------------------------------------------------------------------------
class DietItem(Base):
    __tablename__ = "diet_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    plan_id: Mapped[str] = mapped_column(String, ForeignKey("diet_plans.id"), nullable=False)
    meal: Mapped[str] = mapped_column(String(100), nullable=False)  # Breakfast, Lunch, …
    food_items: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[str | None] = mapped_column(String(100))
    calories: Mapped[int | None] = mapped_column(Integer)
    timing: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)

    plan: Mapped["DietPlan"] = relationship("DietPlan", back_populates="items")


# ---------------------------------------------------------------------------
# progress_records
# ---------------------------------------------------------------------------
class ProgressRecord(Base):
    __tablename__ = "progress_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    member_id: Mapped[str] = mapped_column(String, ForeignKey("members.id"), nullable=False)
    recorded_by: Mapped[str] = mapped_column(String, ForeignKey("profiles.id"), nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    weight: Mapped[float | None] = mapped_column(Numeric(5, 2))
    height: Mapped[float | None] = mapped_column(Numeric(5, 2))
    measurements: Mapped[str | None] = mapped_column(Text)  # JSON string: {"chest": 90, ...}
    observations: Mapped[str | None] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(String)

    member: Mapped["Member"] = relationship("Member", back_populates="progress_records")


# ---------------------------------------------------------------------------
# notices
# ---------------------------------------------------------------------------
class Notice(Base):
    __tablename__ = "notices"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    audience: Mapped[str] = mapped_column(
        Enum("all", "members", "trainers", name="notice_audience"), default="all", nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum("active", "archived", name="notice_status"), default="active", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ---------------------------------------------------------------------------
# events
# ---------------------------------------------------------------------------
class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    event_time: Mapped[str | None] = mapped_column(String(50))  # "10:00 AM"
    location: Mapped[str | None] = mapped_column(String(300))
    image_url: Mapped[str | None] = mapped_column(String)
    status: Mapped[str] = mapped_column(
        Enum("upcoming", "completed", "cancelled", name="event_status"), default="upcoming", nullable=False
    )


# ---------------------------------------------------------------------------
# posts  (blog / news)
# ---------------------------------------------------------------------------
class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))
    created_by: Mapped[str] = mapped_column(String, ForeignKey("profiles.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ---------------------------------------------------------------------------
# gym_status
# ---------------------------------------------------------------------------
class GymStatus(Base):
    __tablename__ = "gym_status"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    status: Mapped[str] = mapped_column(
        Enum("OPEN", "CLOSED", "HOLIDAY", "TEMPORARILY CLOSED", name="gym_status_enum"),
        nullable=False,
        default="OPEN",
    )
    updated_by: Mapped[str | None] = mapped_column(String, ForeignKey("profiles.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ---------------------------------------------------------------------------
# audit_logs
# ---------------------------------------------------------------------------
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = mapped_column(String, ForeignKey("profiles.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)   # CREATE, UPDATE, DELETE
    entity: Mapped[str] = mapped_column(String(100), nullable=False)   # "Member", "Invoice", …
    entity_id: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
