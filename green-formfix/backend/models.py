from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, UniqueConstraint
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    username = Column(String(40), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class WorkoutDayProgress(Base):
    __tablename__ = "workout_day_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    plan_id = Column(String(120), index=True, nullable=False)
    day_id = Column(String(120), index=True, nullable=False)
    day_name = Column(String(255), nullable=False)
    total_exercises = Column(Integer, default=0)
    completed_exercises = Column(Integer, default=0)
    status = Column(String(40), default="in_progress", index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class WorkoutExerciseProgress(Base):
    __tablename__ = "workout_exercise_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    plan_id = Column(String(120), index=True, nullable=False)
    day_id = Column(String(120), index=True, nullable=False)
    exercise_id = Column(String(120), index=True, nullable=False)
    exercise_name = Column(String(255), nullable=False)
    reps = Column(Integer, default=0)
    completed = Column(Boolean, default=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class WorkoutExerciseStatus(Base):
    __tablename__ = "workout_exercise_status"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    plan_id = Column(String(120), index=True, nullable=False)
    day_id = Column(String(120), index=True, nullable=False)
    exercise_id = Column(String(120), index=True, nullable=False)
    exercise_name = Column(String(255), nullable=False)
    status = Column(String(40), default="in_progress", index=True)
    reps = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)


class NutritionProfile(Base):
    __tablename__ = "nutrition_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    age = Column(Integer, nullable=True)
    sex = Column(String(20), default="unspecified")
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    target_weight_kg = Column(Float, nullable=True)
    body_fat_percent = Column(Float, nullable=True)
    activity_level = Column(String(40), default="moderate")
    goal_type = Column(String(40), default="maintain")
    dietary_preference = Column(String(40), default="balanced")
    meals_per_day = Column(Integer, default=3)
    allergies = Column(Text, default="")
    target_calories = Column(Integer, default=2200)
    target_protein = Column(Integer, default=130)
    target_carbs = Column(Integer, default=220)
    target_fat = Column(Integer, default=70)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    ingredients = Column(Text, default="")
    instructions = Column(Text, default="")
    meal_type = Column(String(40), default="lunch")
    calories = Column(Integer, default=0)
    protein = Column(Integer, default=0)
    carbs = Column(Integer, default=0)
    fat = Column(Integer, default=0)
    image_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class MealEntry(Base):
    __tablename__ = "meal_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    date_key = Column(String(20), index=True, nullable=False)
    meal_type = Column(String(40), default="lunch")
    source = Column(String(40), default="manual")
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    calories = Column(Integer, default=0)
    protein = Column(Integer, default=0)
    carbs = Column(Integer, default=0)
    fat = Column(Integer, default=0)
    image_data = Column(Text, nullable=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=True)
    consumed_at_label = Column(String(40), default="")
    confidence_score = Column(Float, nullable=True)
    portion_basis = Column(String(255), default="")
    recognized_items = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class ExerciseSessionReport(Base):
    __tablename__ = "exercise_session_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    plan_id = Column(String(120), index=True, default="")
    day_id = Column(String(120), index=True, default="")
    exercise_id = Column(String(120), index=True, default="")
    exercise_name = Column(String(255), index=True, nullable=False)
    reps = Column(Integer, default=0)
    accuracy = Column(Integer, default=0)
    perfect_reps = Column(Integer, default=0)
    corrected_reps = Column(Integer, default=0)
    poor_reps = Column(Integer, default=0)
    average_rep_quality = Column(Integer, default=0)
    consistency_score = Column(Integer, default=0)
    common_mistakes = Column(Text, default="")
    report_json = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class FitnessGame(Base):
    __tablename__ = "fitness_game_profiles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    xp = Column(Integer, default=0, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    best_streak = Column(Integer, default=0, nullable=False)
    last_workout_date = Column(String(10), nullable=True)
    last_checkin_date = Column(String(10), nullable=True)


class XpEvent(Base):
    __tablename__ = "fitness_xp_events"
    __table_args__ = (UniqueConstraint("user_id", "event_key", name="uq_xp_user_event"),)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    event_key = Column(String(180), nullable=False)
    amount = Column(Integer, nullable=False)
    reason = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class FitnessBadge(Base):
    __tablename__ = "fitness_badges"
    __table_args__ = (UniqueConstraint("user_id", "badge_key", name="uq_badge_user_key"),)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    badge_key = Column(String(60), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)


class FitnessActivity(Base):
    __tablename__ = "fitness_activities"
    __table_args__ = (UniqueConstraint("user_id", "event_key", name="uq_activity_user_event"),)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    event_key = Column(String(180), nullable=False)
    kind = Column(String(40), nullable=False)
    detail = Column(String(255), default="")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class FitnessFollow(Base):
    __tablename__ = "fitness_follows"
    __table_args__ = (UniqueConstraint("follower_id", "following_id", name="uq_follow_pair"),)
    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    following_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class FitnessFriendRequest(Base):
    __tablename__ = "fitness_friend_requests"
    __table_args__ = (UniqueConstraint("sender_id", "recipient_id", name="uq_friend_pair"),)
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    status = Column(String(20), default="pending", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CustomWorkoutPlan(Base):
    __tablename__ = "custom_workout_plans"
    plan_id = Column(String(120), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    plan_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class ActiveWorkoutPlan(Base):
    __tablename__ = "active_workout_plans"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    plan_id = Column(String(120), nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
