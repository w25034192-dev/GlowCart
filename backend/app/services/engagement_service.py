import uuid
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models import (
    CustomerMessage,
    MessageReply,
    Notification,
    Order,
    OrderItem,
    Product,
    Review,
    User,
)
from app.schemas.engagement import (
    CustomerMessageResponse,
    MessageCreateRequest,
    MessageReplyRequest,
    MessageReplyResponse,
    NotificationResponse,
    ReviewCreateRequest,
    ReviewResponse,
    ReviewUpdateRequest,
)


def _serialize_review(r: Review) -> ReviewResponse:
    return ReviewResponse(
        id=r.id,
        product_id=r.product_id,
        user_id=r.user_id,
        author_name=r.user.full_name if r.user else "Customer",
        rating=r.rating,
        title=r.title,
        comment=r.comment,
        is_verified_purchase=r.is_verified_purchase,
        is_approved=r.is_approved,
        created_at=r.created_at,
    )


def _serialize_message(m: CustomerMessage) -> CustomerMessageResponse:
    return CustomerMessageResponse(
        id=m.id,
        user_id=m.user_id,
        customer_email=m.user.email if m.user else "",
        subject=m.subject,
        message=m.message,
        status=m.status,
        replies=[
            MessageReplyResponse(
                id=rep.id,
                sender_id=rep.sender_id,
                body=rep.body,
                is_admin_reply=rep.is_admin_reply,
                created_at=rep.created_at,
            )
            for rep in m.replies
        ],
        created_at=m.created_at,
    )


class EngagementService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_review(self, user: User, payload: ReviewCreateRequest) -> ReviewResponse:
        if not self.db.query(Product).filter(Product.id == payload.product_id).first():
            raise NotFoundError("Product not found.")
        existing = (
            self.db.query(Review)
            .filter(Review.product_id == payload.product_id, Review.user_id == user.id)
            .first()
        )
        if existing is not None:
            raise ConflictError("You have already reviewed this product.")

        purchased = (
            self.db.query(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(
                Order.user_id == user.id,
                OrderItem.product_id == payload.product_id,
                Order.status.in_(["PAID", "CONFIRMED", "PROCESSING", "SHIPPED", "DELIVERED"]),
            )
            .first()
        )
        review = Review(
            product_id=payload.product_id,
            user_id=user.id,
            rating=payload.rating,
            title=payload.title,
            comment=payload.comment.strip(),
            is_verified_purchase=(purchased is not None),
            is_approved=True,
        )
        self.db.add(review)
        self.db.commit()
        loaded = (
            self.db.query(Review)
            .options(joinedload(Review.user))
            .filter(Review.id == review.id)
            .one()
        )
        return _serialize_review(loaded)

    def list_product_reviews(self, product_id: uuid.UUID) -> list[ReviewResponse]:
        rows = (
            self.db.query(Review)
            .options(joinedload(Review.user))
            .filter(Review.product_id == product_id, Review.is_approved.is_(True))
            .order_by(Review.created_at.desc())
            .all()
        )
        return [_serialize_review(r) for r in rows]

    def list_all_reviews_admin(self) -> list[ReviewResponse]:
        rows = (
            self.db.query(Review)
            .options(joinedload(Review.user))
            .order_by(Review.created_at.desc())
            .all()
        )
        return [_serialize_review(r) for r in rows]

    def update_review(
        self, review_id: uuid.UUID, user: User, payload: ReviewUpdateRequest
    ) -> ReviewResponse:
        review = (
            self.db.query(Review)
            .options(joinedload(Review.user))
            .filter(Review.id == review_id)
            .first()
        )
        if review is None:
            raise NotFoundError("Review not found.")
        if review.user_id != user.id:
            raise ForbiddenError("You can only edit your own reviews.")
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(review, k, v)
        self.db.commit()
        self.db.refresh(review)
        return _serialize_review(review)

    def delete_review(self, review_id: uuid.UUID, user: User) -> None:
        review = self.db.query(Review).filter(Review.id == review_id).first()
        if review is None:
            raise NotFoundError("Review not found.")
        role = user.role.name if user.role else "customer"
        if review.user_id != user.id and role not in {"admin", "super_admin"}:
            raise ForbiddenError("You cannot delete this review.")
        self.db.delete(review)
        self.db.commit()

    def moderate_review(self, review_id: uuid.UUID, is_approved: bool) -> ReviewResponse:
        review = (
            self.db.query(Review)
            .options(joinedload(Review.user))
            .filter(Review.id == review_id)
            .first()
        )
        if review is None:
            raise NotFoundError("Review not found.")
        review.is_approved = is_approved
        self.db.commit()
        self.db.refresh(review)
        return _serialize_review(review)

    def create_message(
        self, user: User, payload: MessageCreateRequest
    ) -> CustomerMessageResponse:
        msg = CustomerMessage(
            user_id=user.id,
            subject=payload.subject.strip(),
            message=payload.message.strip(),
            status="OPEN",
        )
        self.db.add(msg)
        self.db.commit()
        loaded = (
            self.db.query(CustomerMessage)
            .options(joinedload(CustomerMessage.user), joinedload(CustomerMessage.replies))
            .filter(CustomerMessage.id == msg.id)
            .one()
        )
        return _serialize_message(loaded)

    def list_messages(self, user: User) -> list[CustomerMessageResponse]:
        role = user.role.name if user.role else "customer"
        q = self.db.query(CustomerMessage).options(
            joinedload(CustomerMessage.user), joinedload(CustomerMessage.replies)
        )
        if role not in {"admin", "super_admin"}:
            q = q.filter(CustomerMessage.user_id == user.id)
        rows = q.order_by(CustomerMessage.created_at.desc()).all()
        return [_serialize_message(m) for m in rows]

    def reply_to_message_admin(
        self, message_id: uuid.UUID, admin_user: User, payload: MessageReplyRequest
    ) -> CustomerMessageResponse:
        msg = (
            self.db.query(CustomerMessage)
            .options(joinedload(CustomerMessage.user), joinedload(CustomerMessage.replies))
            .filter(CustomerMessage.id == message_id)
            .first()
        )
        if msg is None:
            raise NotFoundError("Customer message not found.")
        self.db.add(
            MessageReply(
                message_id=msg.id,
                sender_id=admin_user.id,
                body=payload.body.strip(),
                is_admin_reply=True,
            )
        )
        msg.status = payload.status or "IN_PROGRESS"
        self.db.add(
            Notification(
                user_id=msg.user_id,
                title=f"Support reply: {msg.subject}",
                body=payload.body.strip()[:200],
                category="SUPPORT",
            )
        )
        self.db.commit()
        self.db.expire_all()
        refreshed = (
            self.db.query(CustomerMessage)
            .options(joinedload(CustomerMessage.user), joinedload(CustomerMessage.replies))
            .filter(CustomerMessage.id == msg.id)
            .one()
        )
        return _serialize_message(refreshed)

    def list_notifications(self, user: User) -> list[NotificationResponse]:
        rows = (
            self.db.query(Notification)
            .filter(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
            .limit(50)
            .all()
        )
        return [
            NotificationResponse(
                id=n.id,
                title=n.title,
                body=n.body,
                category=n.category,
                is_read=n.is_read,
                created_at=n.created_at,
            )
            for n in rows
        ]

    def mark_notification_read(
        self, notification_id: uuid.UUID, user: User
    ) -> NotificationResponse:
        n = (
            self.db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user.id)
            .first()
        )
        if n is None:
            raise NotFoundError("Notification not found.")
        n.is_read = True
        self.db.commit()
        self.db.refresh(n)
        return NotificationResponse(
            id=n.id,
            title=n.title,
            body=n.body,
            category=n.category,
            is_read=n.is_read,
            created_at=n.created_at,
        )
