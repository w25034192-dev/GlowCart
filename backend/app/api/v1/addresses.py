import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AddressCreate, AddressResponse, AddressUpdate
from app.services.auth_service import AuthService

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.get("", response_model=list[AddressResponse])
def list_addresses(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return UserRepository(db).list_addresses(user.id)


@router.post("", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(
    payload: AddressCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AuthService(db).create_address(user, payload)


@router.put("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: uuid.UUID,
    payload: AddressUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AuthService(db).update_address(user, address_id, payload)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AuthService(db).delete_address(user, address_id)

