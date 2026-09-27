import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import database, models

router = APIRouter(prefix="/workouts", tags=["workout plans"])
BUILT_IN_PLANS = {
    "ppl": ("Push Pull Legs", "A high-efficiency split targeting functional movement patterns."),
    "volume-split": ("Body Part Split", "A focused five-day split for progressive strength and muscle work."),
}

class PlanSelection(BaseModel):
    user_id: int
    plan_id: str = Field(min_length=1, max_length=120)
    plan: dict | None = None


def validate_custom_plan(plan_id: str, plan: dict, user_id: int):
    if not plan_id.startswith(f"custom-{user_id}-"):
        raise HTTPException(400, "Custom plan ID is invalid")
    if not isinstance(plan.get("days"), list) or not plan["days"]:
        raise HTTPException(422, "A custom plan must contain workout days")
    if len(plan["days"]) > 7:
        raise HTTPException(422, "A custom plan can contain at most seven days")
    for day in plan["days"]:
        if not all(isinstance(day.get(key), str) and day[key].strip() for key in ("id", "name")):
            raise HTTPException(422, "Each workout day needs an ID and name")
        if not isinstance(day.get("exercises"), list) or not day["exercises"]:
            raise HTTPException(422, "Each workout day must contain exercises")
        for exercise in day["exercises"]:
            if not all(isinstance(exercise.get(key), str) and exercise[key].strip() for key in ("id", "name")):
                raise HTTPException(422, "Each exercise needs an ID and name")
    if len(json.dumps(plan)) > 250_000:
        raise HTTPException(413, "Custom workout plan is too large")


def plan_info(db, user_id, plan_id):
    if plan_id in BUILT_IN_PLANS:
        name, description = BUILT_IN_PLANS[plan_id]
        return {"plan_id": plan_id, "name": name, "description": description, "is_custom": False, "plan": None}
    saved = db.query(models.CustomWorkoutPlan).filter_by(user_id=user_id, plan_id=plan_id).first()
    if not saved:
        return None
    return {"plan_id": saved.plan_id, "name": saved.name, "description": saved.description,
            "is_custom": True, "plan": json.loads(saved.plan_json), "created_at": saved.created_at.isoformat() if saved.created_at else None}

@router.post("/activate")
def activate_plan(payload: PlanSelection, db: Session = Depends(database.get_db)):
    if not db.query(models.User).filter_by(id=payload.user_id).first():
        raise HTTPException(404, "User not found")
    if payload.plan_id in BUILT_IN_PLANS:
        selected = plan_info(db, payload.user_id, payload.plan_id)
    else:
        existing = db.query(models.CustomWorkoutPlan).filter_by(plan_id=payload.plan_id, user_id=payload.user_id).first()
        if payload.plan is None:
            if not existing:
                raise HTTPException(404, "Saved custom workout plan not found")
            selected = {"plan_id": existing.plan_id, "name": existing.name, "description": existing.description,
                "is_custom": True, "plan": json.loads(existing.plan_json)}
        else:
            validate_custom_plan(payload.plan_id, payload.plan, payload.user_id)
            conflicting = db.query(models.CustomWorkoutPlan).filter_by(plan_id=payload.plan_id).first()
            if conflicting and conflicting.user_id != payload.user_id:
                raise HTTPException(409, "Plan ID already exists")
            if not existing:
                db.add(models.CustomWorkoutPlan(plan_id=payload.plan_id, user_id=payload.user_id,
                    name=str(payload.plan.get("name", "Custom Workout"))[:255],
                    description=str(payload.plan.get("description", ""))[:2000],
                    plan_json=json.dumps(payload.plan)))
            selected = {"plan_id":payload.plan_id,"name":str(payload.plan.get("name","Custom Workout")),
                "description":str(payload.plan.get("description","")),"is_custom":True,"plan":payload.plan}
    active = db.query(models.ActiveWorkoutPlan).filter_by(user_id=payload.user_id).first()
    if not active:
        active = models.ActiveWorkoutPlan(user_id=payload.user_id, plan_id=payload.plan_id, updated_at=datetime.utcnow())
        db.add(active)
    else:
        active.plan_id = payload.plan_id
        active.updated_at = datetime.utcnow()
    db.commit()
    selected["active"] = True
    return selected

@router.get("/profile/{user_id}")
def workout_plan_profile(user_id: int, db: Session = Depends(database.get_db)):
    if not db.query(models.User).filter_by(id=user_id).first():
        raise HTTPException(404, "User not found")
    active_row = db.query(models.ActiveWorkoutPlan).filter_by(user_id=user_id).first()
    active = plan_info(db, user_id, active_row.plan_id) if active_row else None
    if active:
        active["active"] = True
        active["selected_at"] = active_row.updated_at.isoformat() if active_row.updated_at else None
    rows = (db.query(models.WorkoutDayProgress).filter_by(user_id=user_id)
        .order_by(models.WorkoutDayProgress.updated_at.desc()).all())
    groups = {}
    for row in rows:
        group = groups.setdefault(row.plan_id, {"plan_id":row.plan_id,"workout_days":0,"completed_days":0,"last_activity":None,"days":[]})
        group["workout_days"] += 1
        group["completed_days"] += row.status == "completed"
        updated = row.updated_at.isoformat() if row.updated_at else None
        if updated and (group["last_activity"] is None or updated > group["last_activity"]):
            group["last_activity"] = updated
        group["days"].append({"day_id":row.day_id,"day_name":row.day_name,"status":row.status,
            "completed_exercises":row.completed_exercises,"total_exercises":row.total_exercises,"updated_at":updated})
    history=[]
    for plan_id, progress in groups.items():
        info = plan_info(db, user_id, plan_id)
        if info is None:
            info = {"plan_id":plan_id,"name":plan_id,"is_custom":plan_id.startswith(f"custom-{user_id}-"),"description":"Previous workout plan"}
        progress.update({"name":info["name"],"is_custom":info["is_custom"]})
        history.append(progress)
    history.sort(key=lambda item:item["last_activity"] or "", reverse=True)
    latest_custom = db.query(models.CustomWorkoutPlan).filter_by(user_id=user_id).order_by(models.CustomWorkoutPlan.created_at.desc()).first()
    latest_custom_info = plan_info(db, user_id, latest_custom.plan_id) if latest_custom else None
    return {"active_plan":active,"latest_custom_plan":latest_custom_info,"history":history}

@router.get("/custom/{user_id}/{plan_id}")
def get_custom_plan(user_id:int, plan_id:str, db:Session=Depends(database.get_db)):
    saved=db.query(models.CustomWorkoutPlan).filter_by(user_id=user_id,plan_id=plan_id).first()
    if not saved: raise HTTPException(404,"Custom workout plan not found")
    return {"plan_id":saved.plan_id,"name":saved.name,"description":saved.description,"is_custom":True,"plan":json.loads(saved.plan_json)}
