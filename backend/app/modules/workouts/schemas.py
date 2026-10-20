from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExerciseWrite(BaseModel):
    workout_day: str = Field(min_length=1, max_length=50)
    exercise_name: str = Field(min_length=1, max_length=200)
    muscle_group: str | None = Field(default=None, max_length=100)
    sets: int | None = Field(default=None, gt=0)
    reps: str | None = Field(default=None, max_length=50)
    duration: str | None = Field(default=None, max_length=50)
    rest_time: str | None = Field(default=None, max_length=50)
    instructions: str | None = None

    @field_validator("workout_day", "exercise_name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value


class WorkoutPlanWrite(BaseModel):
    member_id: str = Field(min_length=1)
    trainer_id: str | None = Field(default=None, min_length=1)
    title: str = Field(min_length=1, max_length=200)
    notes: str | None = None
    exercises: list[ExerciseWrite] = Field(min_length=1, max_length=100)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Enter a plan title.")
        return value


class WorkoutExerciseRead(ExerciseWrite):
    model_config = ConfigDict(from_attributes=True)

    id: str


class WorkoutPlanRead(BaseModel):
    id: str
    member_id: str
    member_name: str
    member_code: str
    trainer_id: str
    title: str
    notes: str | None
    created_at: datetime
    exercises: list[WorkoutExerciseRead]


class WorkoutPlanPage(BaseModel):
    items: list[WorkoutPlanRead]
    page: int
    page_size: int
    total: int


class WorkoutMemberOption(BaseModel):
    id: str
    member_code: str
    full_name: str
    trainer_id: str | None


class WorkoutTrainerOption(BaseModel):
    id: str
    full_name: str


class WorkoutOptions(BaseModel):
    members: list[WorkoutMemberOption]
    trainers: list[WorkoutTrainerOption]


class WorkoutMeRead(BaseModel):
    id: str
    full_name: str
    role: str
    member_id: str | None
    trainer_id: str | None
