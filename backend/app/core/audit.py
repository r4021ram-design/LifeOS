from sqlalchemy.orm import Session
from app.models.models import AuditLog

def log_audit(db: Session, user_id: int, action: str, old_value: str = None, new_value: str = None, ip_address: str = None):
    try:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address
        )
        db.add(log_entry)
        db.commit()
    except Exception:
        # Prevent database issues in logging from blocking primary operations
        db.rollback()
