from datetime import datetime, timezone
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
    x_user_name: str | None = Header(default=None, alias="X-User-Name"),
) -> User:
    if not x_user_email:
        raise HTTPException(status_code=401, detail="Missing X-User-Email header (MVP auth).")

    user = db.query(User).filter(User.email == x_user_email).one_or_none()
    if not user:
        user = User(email=x_user_email, name=x_user_name)
        db.add(user)
        db.commit()
        db.refresh(user)

    user.last_login = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    return user
