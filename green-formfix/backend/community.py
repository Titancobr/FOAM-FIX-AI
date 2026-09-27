from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
import models, database

router = APIRouter(prefix="/community", tags=["fitness community"])

BADGES = {
    "first_workout": ("First Rep", "Complete your first workout"),
    "week_streak": ("On a Roll", "Reach a 7 day workout streak"),
    "level_5": ("Rising Athlete", "Reach level 5"),
    "five_workouts": ("Consistent", "Complete five workouts"),
}

WORKOUT_XP = 50

def username(user):
    return user.username or (user.email.split("@")[0] if user.email else f"athlete{user.id}")

def level_for(xp):
    return xp // 100 + 1

def game_for(db, user_id):
    game = db.query(models.FitnessGame).filter_by(user_id=user_id).first()
    if not game:
        game = models.FitnessGame(user_id=user_id, xp=0, current_streak=0, best_streak=0)
        db.add(game); db.flush()
    return game

def log_activity(db, user_id, event_key, kind, detail):
    exists = db.query(models.FitnessActivity).filter_by(user_id=user_id, event_key=event_key).first()
    if not exists:
        db.add(models.FitnessActivity(user_id=user_id, event_key=event_key, kind=kind, detail=detail))

def award(db, user_id, key, amount, reason):
    event = db.query(models.XpEvent).filter_by(user_id=user_id, event_key=key).first()
    if event:
        return 0
    db.add(models.XpEvent(user_id=user_id, event_key=key, amount=amount, reason=reason))
    game = game_for(db, user_id)
    game.xp += amount
    return amount

def award_badges(db, user_id):
    db.flush()
    game = game_for(db, user_id)
    workouts = db.query(models.FitnessActivity).filter_by(user_id=user_id, kind="workout").count()
    earned = {b.badge_key for b in db.query(models.FitnessBadge).filter_by(user_id=user_id).all()}
    candidates = []
    if workouts >= 1: candidates.append("first_workout")
    if workouts >= 5: candidates.append("five_workouts")
    if game.current_streak >= 7: candidates.append("week_streak")
    if level_for(game.xp) >= 5: candidates.append("level_5")
    fresh = []
    for key in candidates:
        if key not in earned:
            db.add(models.FitnessBadge(user_id=user_id, badge_key=key)); fresh.append(key)
            log_activity(db, user_id, f"badge:{key}", "badge", BADGES[key][0])
    return fresh

def bump_streak(game, today):
    if game.last_workout_date == today:
        return
    yesterday = (date.fromisoformat(today) - timedelta(days=1)).isoformat()
    game.current_streak = (game.current_streak or 0) + 1 if game.last_workout_date == yesterday else 1
    game.best_streak = max(game.best_streak or 0, game.current_streak)
    game.last_workout_date = today

def record_completed_workout(db, user_id, plan_id, day_id, day_name):
    game = game_for(db, user_id)
    level_before = level_for(game.xp)
    today = date.today().isoformat()
    event_key = f"workout:{plan_id}:{day_id}"
    label = day_name or "Workout completed"
    xp_earned = award(db, user_id, event_key, WORKOUT_XP, "workout_completed")
    bump_streak(game, today)
    log_activity(db, user_id, event_key, "workout", label)
    new_badges = award_badges(db, user_id)
    return {"xp_earned": xp_earned, "new_badges": new_badges, "level_before": level_before,
            "level_after": level_for(game.xp), "current_streak": game.current_streak,
            "best_streak": game.best_streak}

def public_user(db, user_id):
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user: return None
    game = game_for(db, user_id)
    return {"user_id": user.id, "username": username(user), "level": level_for(game.xp), "xp": game.xp,
            "current_streak": game.current_streak, "best_streak": game.best_streak}

@router.get("/dashboard/{user_id}")
def dashboard(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user: raise HTTPException(404, "User not found")
    game = game_for(db, user_id); db.commit()
    today = date.today().isoformat()
    workout_today = db.query(models.FitnessActivity).filter_by(user_id=user_id, kind="workout").filter(func.date(models.FitnessActivity.created_at) == today).count() > 0
    badges = db.query(models.FitnessBadge).filter_by(user_id=user_id).order_by(models.FitnessBadge.earned_at.desc()).all()
    followed_ids = [row.following_id for row in db.query(models.FitnessFollow).filter_by(follower_id=user_id).all()]
    accepted = db.query(models.FitnessFriendRequest).filter(models.FitnessFriendRequest.status == "accepted", or_(models.FitnessFriendRequest.sender_id == user_id, models.FitnessFriendRequest.recipient_id == user_id)).all()
    friend_ids = [row.sender_id if row.recipient_id == user_id else row.recipient_id for row in accepted]
    visible_ids = set([user_id, *followed_ids, *friend_ids])
    activities = (db.query(models.FitnessActivity, models.User).join(models.User, models.User.id == models.FitnessActivity.user_id)
        .filter(models.FitnessActivity.user_id.in_(visible_ids))
        .order_by(models.FitnessActivity.created_at.desc()).limit(30).all())
    return {"user": {**public_user(db, user_id), "checked_in": game.last_checkin_date == today},
            "tasks": [{"id":"checkin", "title":"Daily check-in", "xp":10, "done":game.last_checkin_date == today},
                      {"id":"workout", "title":"Complete a workout", "xp":25, "done":workout_today}],
            "badges":[{"key":b.badge_key,"name":BADGES.get(b.badge_key,(b.badge_key,""))[0],"description":BADGES.get(b.badge_key,("",""))[1]} for b in badges],
            "activities":[{"username":username(u),"kind":a.kind,"detail":a.detail,"created_at":a.created_at.isoformat()} for a,u in activities]}

@router.post("/check-in/{user_id}")
def check_in(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user: raise HTTPException(404, "User not found")
    game = game_for(db,user_id); today=date.today().isoformat()
    gained = 0
    if game.last_checkin_date != today:
        gained = award(db,user_id,f"checkin:{today}",10,"daily_checkin")
        game.last_checkin_date=today
        log_activity(db,user_id,f"checkin:{today}","checkin","checked in for today")
    db.commit()
    return {"xp_earned":gained,"user":public_user(db,user_id)}

@router.post("/task/{user_id}/{task_id}")
def complete_task(user_id:int, task_id:str, db:Session=Depends(database.get_db)):
    if task_id == "checkin": return check_in(user_id,db)
    if task_id != "workout": raise HTTPException(404,"Task not found")
    start=datetime.combine(date.today(), datetime.min.time())
    report=db.query(models.ExerciseSessionReport).filter(models.ExerciseSessionReport.user_id==user_id, models.ExerciseSessionReport.created_at>=start, models.ExerciseSessionReport.reps>0).first()
    completed=db.query(models.WorkoutDayProgress).filter(models.WorkoutDayProgress.user_id==user_id, models.WorkoutDayProgress.completed_at>=start, models.WorkoutDayProgress.status=="completed").first()
    if not report and not completed: raise HTTPException(400,"Complete a workout first")
    gain=award(db,user_id,f"task:workout:{date.today().isoformat()}",25,"daily_workout_task")
    db.commit()
    return {"xp_earned":gain,"user":public_user(db,user_id)}

@router.get("/leaderboard")
def leaderboard(db:Session=Depends(database.get_db), limit:int=Query(50,ge=1,le=100)):
    rows=db.query(models.FitnessGame).order_by(models.FitnessGame.xp.desc(), models.FitnessGame.user_id.asc()).limit(limit).all()
    result=[]
    for i,g in enumerate(rows,1):
        u=db.query(models.User).filter_by(id=g.user_id).first()
        if u: result.append({"rank":i,"user_id":u.id,"username":username(u),"level":level_for(g.xp),"xp":g.xp})
    return result

@router.get("/search")
def search_users(q:str=Query("", min_length=1, max_length=40), viewer_id:int|None=None, db:Session=Depends(database.get_db)):
    users=db.query(models.User).filter(or_(models.User.username.ilike(f"%{q}%"),models.User.email.ilike(f"%{q}%"))).limit(20).all()
    result=[]
    for u in users:
        if u.id == viewer_id: continue
        profile=public_user(db,u.id)
        profile["following"] = bool(viewer_id and db.query(models.FitnessFollow).filter_by(follower_id=viewer_id,following_id=u.id).first())
        request=db.query(models.FitnessFriendRequest).filter(or_(models.FitnessFriendRequest.sender_id==viewer_id,models.FitnessFriendRequest.recipient_id==viewer_id),or_(models.FitnessFriendRequest.sender_id==u.id,models.FitnessFriendRequest.recipient_id==u.id),models.FitnessFriendRequest.status=="pending").first() if viewer_id else None
        profile["friend_status"] = "friends" if db.query(models.FitnessFriendRequest).filter(or_(models.FitnessFriendRequest.sender_id==viewer_id,models.FitnessFriendRequest.recipient_id==viewer_id),or_(models.FitnessFriendRequest.sender_id==u.id,models.FitnessFriendRequest.recipient_id==u.id),models.FitnessFriendRequest.status=="accepted").first() else ("pending" if request else "none")
        result.append(profile)
    return result

@router.get("/profile/{user_id}")
def profile(user_id:int, viewer_id:int|None=None, db:Session=Depends(database.get_db)):
    result=public_user(db,user_id)
    if not result: raise HTTPException(404,"User not found")
    follower_rows = db.query(models.FitnessFollow).filter_by(following_id=user_id).all()
    following_rows = db.query(models.FitnessFollow).filter_by(follower_id=user_id).all()
    result["followers"] = [public_user(db, r.follower_id) for r in follower_rows]
    result["following"] = [public_user(db, r.following_id) for r in following_rows]
    result["is_following"] = bool(viewer_id and db.query(models.FitnessFollow).filter_by(follower_id=viewer_id,following_id=user_id).first())
    result["badges"] = [b.badge_key for b in db.query(models.FitnessBadge).filter_by(user_id=user_id).all()]
    return result

class RelationPayload(BaseModel):
    actor_id:int
    target_id:int

@router.post("/follow")
def follow(payload:RelationPayload, db:Session=Depends(database.get_db)):
    if payload.actor_id==payload.target_id: raise HTTPException(400,"Cannot follow yourself")
    if not db.query(models.User).filter_by(id=payload.target_id).first(): raise HTTPException(404,"User not found")
    row=db.query(models.FitnessFollow).filter_by(follower_id=payload.actor_id,following_id=payload.target_id).first()
    if row: db.delete(row); following=False
    else: db.add(models.FitnessFollow(follower_id=payload.actor_id,following_id=payload.target_id)); following=True
    db.commit(); return {"following":following}

@router.get("/friends/{user_id}")
def friends(user_id:int, db:Session=Depends(database.get_db)):
    rows=db.query(models.FitnessFriendRequest).filter(models.FitnessFriendRequest.status=="pending",models.FitnessFriendRequest.recipient_id==user_id).all()
    outgoing=db.query(models.FitnessFriendRequest).filter(models.FitnessFriendRequest.status=="pending",models.FitnessFriendRequest.sender_id==user_id).all()
    follower_rows=db.query(models.FitnessFollow).filter_by(following_id=user_id).all()
    following_rows=db.query(models.FitnessFollow).filter_by(follower_id=user_id).all()
    accepted=db.query(models.FitnessFriendRequest).filter(models.FitnessFriendRequest.status=="accepted",or_(models.FitnessFriendRequest.sender_id==user_id,models.FitnessFriendRequest.recipient_id==user_id)).all()
    return {"incoming":[{"request_id":r.id,"user":public_user(db,r.sender_id)} for r in rows],
        "outgoing":[public_user(db,r.recipient_id) for r in outgoing],
        "friends":[public_user(db, (r.sender_id if r.recipient_id==user_id else r.recipient_id)) for r in accepted],
        "followers":[public_user(db,r.follower_id) for r in follower_rows],
        "following":[public_user(db,r.following_id) for r in following_rows]}

@router.post("/friend-request")
def friend_request(payload:RelationPayload, db:Session=Depends(database.get_db)):
    if payload.actor_id==payload.target_id: raise HTTPException(400,"Cannot friend yourself")
    existing=db.query(models.FitnessFriendRequest).filter(or_(models.FitnessFriendRequest.sender_id==payload.actor_id,models.FitnessFriendRequest.recipient_id==payload.actor_id),or_(models.FitnessFriendRequest.sender_id==payload.target_id,models.FitnessFriendRequest.recipient_id==payload.target_id)).first()
    if existing:
        if existing.status=="pending" and existing.recipient_id==payload.actor_id: existing.status="accepted"
        else: raise HTTPException(409,"Friend request already exists")
    else: db.add(models.FitnessFriendRequest(sender_id=payload.actor_id,recipient_id=payload.target_id,status="pending"))
    db.commit(); return {"status":"accepted" if existing and existing.status=="accepted" else "pending"}

@router.post("/workout-event/{user_id}")
def workout_event(user_id:int, plan_id:str, day_id:str, db:Session=Depends(database.get_db)):
    day=db.query(models.WorkoutDayProgress).filter_by(user_id=user_id,plan_id=plan_id,day_id=day_id,status="completed").first()
    if not day: raise HTTPException(400,"Workout day is not complete")
    result=record_completed_workout(db,user_id,plan_id,day_id,day.day_name)
    db.commit()
    result["user"]=public_user(db,user_id)
    return result
