from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    product_id: uuid.UUID
    rating: int = Field(ge=1, le=5)
    title: str | None = Field(default=None, max_length=160)
    comment: str = Field(min_length=2, max_length=2000)


class ReviewUpdateRequest(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    title: str | None = Field(default=None, max_length=160)
    comment: str | None = Field(default=None, min_length=2, max_length=2000)


class ReviewModerateRequest(BaseModel):
    is_approved: bool


class ReviewResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    user_id: uuid.UUID
    author_name: str
    rating: int
    title: str | None
    comment: str
    is_verified_purchase: bool
    is_approved: bool
    created_at: datetime


class MessageCreateRequest(BaseModel):
    subject: str = Field(min_length=2, max_length=200)
    message: str = Field(min_length=2, max_length=3000)


class MessageReplyRequest(BaseModel):
    body: str = Field(min_length=1, max_length=3000)
    status: str | None = Field(default=None, pattern="^(OPEN|IN_PROGRESS|RESOLVED|CLOSED)$")


class MessageReplyResponse(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    body: str
    is_admin_reply: bool
    created_at: datetime


class CustomerMessageResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    customer_email: str
    subject: str
    message: str
    status: str
    replies: list[MessageReplyResponse]
    created_at: datetime


class NotificationResponse(BaseModel):
    id: uuid.UUID
    title: str
    body: str
    category: str
    is_read: bool
    created_at: datetime

