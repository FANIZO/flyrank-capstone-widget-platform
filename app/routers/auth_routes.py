from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import Owner
from app.schemas import Credentials, OwnerResponse, TokenResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=OwnerResponse, status_code=status.HTTP_201_CREATED)
def signup(credentials: Credentials, database: Session = Depends(get_db)):
    email = credentials.email.lower()
    if database.scalar(select(Owner).where(Owner.email == email)):
        raise HTTPException(status_code=409, detail="Email already registered")
    owner = Owner(email=email, password_hash=hash_password(credentials.password))
    database.add(owner)
    database.commit()
    database.refresh(owner)
    return owner


@router.post("/login", response_model=TokenResponse)
def login(credentials: Credentials, database: Session = Depends(get_db)):
    owner = database.scalar(select(Owner).where(Owner.email == credentials.email.lower()))
    if owner is None or not verify_password(credentials.password, owner.password_hash):
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    return TokenResponse(access_token=create_access_token(owner))
