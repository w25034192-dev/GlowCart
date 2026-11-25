import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.engagement import (
    CustomerMessageResponse,
    MessageCreateRequest,
    MessageReplyRequest,
    NotificationResponse,
)
from app.services.engagement_service import EngagementService

router = APIRouter(tags=["Customer Support & Notifications"])


@router.post("/messages", response_model=CustomerMessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(
    payload: MessageCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return EngagementService(db).create_message(user, payload)


@router.get("/messages", response_model=list[CustomerMessageResponse])
def list_messages(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return EngagementService(db).list_messages(user)


@router.post("/admin/messages/{message_id}/reply", response_model=CustomerMessageResponse)
def reply_message(
    message_id: uuid.UUID,
    payload: MessageReplyRequest,
    admin_user: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return EngagementService(db).reply_to_message_admin(message_id, admin_user, payload)


@router.get("/notifications", response_model=list[NotificationResponse])
def list_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return EngagementService(db).list_notifications(user)


@router.patch("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return EngagementService(db).mark_notification_read(notification_id, user)

