import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from .db import get_db
from .models import Session, User, SupplierUser

bearer = HTTPBearer(auto_error=False)


def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.scrypt(
        password.encode(), salt=salt.encode(), n=16384, r=8, p=1
    ).hex()
    return f"scrypt${salt}${digest}"


def verify_password(password, stored):
    _, salt, expected = stored.split("$")
    actual = hashlib.scrypt(
        password.encode(), salt=salt.encode(), n=16384, r=8, p=1
    ).hex()
    return hmac.compare_digest(actual, expected)


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def issue_token(db, user):
    token = secrets.token_urlsafe(48)
    db.add(
        Session(
            token_hash=token_hash(token),
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=12),
        )
    )
    db.commit()
    return {"access_token": token, "token_type": "bearer", "user": user_dict(user)}


def user_dict(user):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "supplier_id": user.supplier_id,
    }


def current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer), db=Depends(get_db)
):
    if not credentials:
        raise HTTPException(401, "Authentication required")
    session = db.scalar(
        select(Session).where(Session.token_hash == token_hash(credentials.credentials))
    )
    if not session or session.expires_at.replace(tzinfo=timezone.utc) <= datetime.now(
        timezone.utc
    ):
        raise HTTPException(401, "Session expired or invalid")
    return db.get(User, session.user_id)


def supplier_user(user=Depends(current_user), db=Depends(get_db)):
    if user.role != "supplier":
        raise HTTPException(403, "Supplier account required")
    if not db.get(SupplierUser, (user.supplier_id, user.id)):
        raise HTTPException(403, "Supplier membership required")
    return user


def admin_user(user=Depends(current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Administrator account required")
    return user
