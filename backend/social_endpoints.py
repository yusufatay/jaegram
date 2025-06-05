\
from fastapi import APIRouter, Depends, HTTPException, Query # Added Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Dict, List, Any

from models import User, Task, TaskStatus, DailyReward, Leaderboard, CoinTransaction # Imported CoinTransaction
from app import get_current_user, get_db # Assuming app.py will provide these
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

social_router = APIRouter(prefix="/social", tags=["Social Features"])

@social_router.get("/my-rank")
async def get_my_rank(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's rank in leaderboard"""
    try:
        user_coins = current_user.coin_balance or 0
        
        higher_users = db.query(User).filter(User.coin_balance > user_coins).count()
        current_rank = higher_users + 1
        
        total_users = db.query(User).count()
        rank_percentage = (current_rank / total_users * 100) if total_users > 0 else 0
        
        completed_tasks = db.query(Task).filter(
            Task.assigned_user_id == current_user.id,
            Task.status == TaskStatus.completed
        ).count()
        
        if completed_tasks >= 100:
            level = "Elmas"
            level_color = "#E6E6FA"
        elif completed_tasks >= 50:
            level = "Altın"
            level_color = "#FFD700"
        elif completed_tasks >= 25:
            level = "Gümüş"
            level_color = "#C0C0C0"
        else:
            level = "Bronz"
            level_color = "#CD7F32"
        
        rank_data = {
            "current_rank": current_rank,
            "total_users": total_users,
            "rank_percentage": round(rank_percentage, 1),
            "user_coins": int(user_coins or 0),
            "diamondBalance": int(user_coins or 0),  # Add for frontend compatibility
            "totalCoins": int(user_coins or 0),      # Add for frontend compatibility
            "completed_tasks": int(completed_tasks or 0),
            "level": level,
            "level_color": level_color,
            "next_level_requirement": {
                "Bronz": 25,
                "Gümüş": 50, 
                "Altın": 100,
                "Elmas": 100
            }.get(level, 100),
            "progress_to_next": min(100, (completed_tasks % 25) * 4) if level != "Elmas" else 100
        }
        
        return {
            "success": True,
            "rank": rank_data
        }
        
    except Exception as e:
        logger.error(f"Rank calculation error: {e}")
        raise HTTPException(status_code=500, detail=f"Sıralama hesaplanamadı: {str(e)}")

@social_router.get("/leaderboard")
async def get_leaderboard_data(
    period: str = Query("weekly", enum=["weekly", "monthly", "all"]),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leaderboard data based on period"""
    try:
        query = db.query(
            User.id.label("user_id"),
            User.username,
            User.full_name,
            User.profile_pic_url,
            User.coin_balance.label("score")
        ).filter(User.is_banned == False)

        if period == "weekly":
            start_date = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
            query = query.join(CoinTransaction, CoinTransaction.user_id == User.id)\
                         .filter(CoinTransaction.created_at >= start_date)\
                         .group_by(User.id)\
                         .order_by(desc(func.sum(CoinTransaction.amount)))
        elif period == "monthly":
            start_date = datetime.utcnow().replace(day=1)
            query = query.join(CoinTransaction, CoinTransaction.user_id == User.id)\
                         .filter(CoinTransaction.created_at >= start_date)\
                         .group_by(User.id)\
                         .order_by(desc(func.sum(CoinTransaction.amount)))
        else: # all time
            query = query.order_by(desc(User.coin_balance))

        leaderboard_users = query.limit(limit).all()

        # Get current user's rank for this period
        # This is a simplified rank; a more robust solution might use window functions
        # or a dedicated leaderboard table updated periodically.
        
        # For simplicity, we'll fetch all users for ranking in the period if not 'all'
        # This can be inefficient for large datasets.
        user_rank = -1
        if leaderboard_users: # only calculate if there are users
            if period != "all":
                all_period_users_query = db.query(
                    User.id, func.sum(CoinTransaction.amount).label("period_score")
                ).join(CoinTransaction, CoinTransaction.user_id == User.id)
                if period == "weekly":
                     all_period_users_query = all_period_users_query.filter(CoinTransaction.created_at >= (datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())))
                elif period == "monthly":
                     all_period_users_query = all_period_users_query.filter(CoinTransaction.created_at >= datetime.utcnow().replace(day=1))
                
                all_period_users = all_period_users_query.group_by(User.id).order_by(desc("period_score")).all()
                
                for i, u_data in enumerate(all_period_users):
                    if u_data.id == current_user.id:
                        user_rank = i + 1
                        break
            else: # all time rank
                 all_time_users = db.query(User.id, User.coin_balance).order_by(desc(User.coin_balance)).all()
                 for i, u_data in enumerate(all_time_users):
                    if u_data.id == current_user.id:
                        user_rank = i + 1
                        break


        return {
            "success": True,
            "period": period,
            "leaderboard": [{
                "rank": idx + 1,
                "user_id": u.user_id,
                "username": u.username,
                "full_name": u.full_name,
                "profile_pic_url": u.profile_pic_url or f"https://ui-avatars.com/api/?name={u.username}&background=random",
                "score": u.score if period == "all" else (db.query(func.sum(CoinTransaction.amount))
                                .filter(CoinTransaction.user_id == u.user_id,
                                        CoinTransaction.created_at >= (datetime.utcnow() - timedelta(days=datetime.utcnow().weekday()) if period == 'weekly'
                                                                      else datetime.utcnow().replace(day=1)))
                                .scalar() or 0),
                "total_coins": u.score if period == "all" else (db.query(func.sum(CoinTransaction.amount))
                                .filter(CoinTransaction.user_id == u.user_id,
                                        CoinTransaction.created_at >= (datetime.utcnow() - timedelta(days=datetime.utcnow().weekday()) if period == 'weekly'
                                                                      else datetime.utcnow().replace(day=1)))
                                .scalar() or 0),
                "diamondBalance": u.score if period == "all" else (db.query(func.sum(CoinTransaction.amount))
                                .filter(CoinTransaction.user_id == u.user_id,
                                        CoinTransaction.created_at >= (datetime.utcnow() - timedelta(days=datetime.utcnow().weekday()) if period == 'weekly'
                                                                      else datetime.utcnow().replace(day=1)))
                                .scalar() or 0),
                "is_current_user": u.user_id == current_user.id
            } for idx, u in enumerate(leaderboard_users)],
            "user_rank": user_rank, # User's rank in this specific leaderboard
            "total_participants": db.query(User).filter(User.is_banned == False).count() # Total active users
        }
    except Exception as e:
        logger.error(f"Leaderboard fetch error for period {period}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lider tablosu alınamadı: {str(e)}")

# You might want to add other social features here, e.g., user profiles, friend requests, etc.

def init_app(app): # Added colon
    app.include_router(social_router)

