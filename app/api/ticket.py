from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dependencies import require_support_staff
from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.ticket import Ticket
from app.models.user import User

from app.schemas.ticket import (
    TicketCreate,
    TicketReplace,
    TicketResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/support-ticket",
    tags=["Support Tickets"]
)


# CREATE
@router.post("", response_model=TicketResponse, status_code=201)
def create_ticket(
    request: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    ticket = Ticket(
        customer_name=request.customer_name,
        email=request.email,
        issue=request.issue,
        status="pending",
        user_id=current_user.id
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    logger.info(
        "Ticket created: ticket_id=%s user_id=%s",
        ticket.id,
        current_user.id
    )

    return ticket


# READ ALL: Chỉ xem ticket của chính mình
@router.get("", response_model=list[TicketResponse])
def get_all_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    statement = (
        select(Ticket)
        .where(Ticket.user_id == current_user.id)
        .order_by(Ticket.id)
    )

    return db.scalars(statement).all()


# READ ONE
@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_owned_ticket(ticket_id, db, current_user)


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    request: TicketReplace,
    db: Session = Depends(get_db),
    staff_user: User = Depends(require_support_staff)
):

    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    ticket.customer_name = request.customer_name
    ticket.email = request.email
    ticket.issue = request.issue
    ticket.status = request.status

    db.commit()
    db.refresh(ticket)

    return ticket


@router.delete("/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    staff_user: User = Depends(require_support_staff)
):

    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    db.delete(ticket)
    db.commit()

    return {
        "message": "Ticket deleted successfully",
        "ticket_id": ticket_id
    }


def get_owned_ticket(
    ticket_id: int,
    db: Session,
    current_user: User
):

    ticket = db.scalar(
        select(Ticket).where(
            Ticket.id == ticket_id,
            Ticket.user_id == current_user.id
        )
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return ticket
