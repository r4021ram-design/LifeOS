import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.api.v1.auth import get_current_user
from app.models.models import User, DeviceToken
from app.schemas.schemas import DeviceTokenCreate, DeviceTokenResponse

router = APIRouter(prefix="/devices", tags=["devices"])

@router.post("/register", response_model=DeviceTokenResponse)
def register_device(
    device_in: DeviceTokenCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if this token is already registered (anywhere/for anyone)
    existing_device = db.query(DeviceToken).filter(DeviceToken.token == device_in.token).first()
    
    if existing_device:
        # Token rotation or switching users on same device
        existing_device.user_id = current_user.id
        existing_device.platform = device_in.platform
        existing_device.device_name = device_in.device_name
        existing_device.updated_at = datetime.datetime.now(datetime.UTC)
        db.commit()
        db.refresh(existing_device)
        return existing_device
    else:
        # Register new device token
        new_device = DeviceToken(
            user_id=current_user.id,
            token=device_in.token,
            platform=device_in.platform,
            device_name=device_in.device_name
        )
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        return new_device
