from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.hygiene_products import User
from app.core.security import SECRET_KEY, ALGORITHM
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db, get_redis

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not bool(user.is_active):
        raise HTTPException(status_code=401, detail="Inactive user")
    return user

async def get_current_facility_id(
    facility_id: Optional[str] = None
) -> Optional[str]:
    """Get current facility ID from request parameters"""
    return facility_id

async def validate_facility_access(
    facility_id: str,
    db: Session = Depends(get_db)
) -> str:
    """Validate that facility exists and user has access"""
    # In production, add proper facility access validation
    return facility_id