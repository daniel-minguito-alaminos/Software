import re
from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, select

from auth_session import CurrentUser
from database import get_session
from models import PartnerCheck, User
from vies import check_vat_number

router = APIRouter(tags=["partner-checks"])
SessionDep = Annotated[Session, Depends(get_session)]


class PartnerCheckRequest(BaseModel):
    identifier: str


class SourceResult(BaseModel):
    name: str
    status: Literal["checked", "unavailable", "not_implemented"]
    valid: bool | None = None


class PartnerCheckResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    identifier: str
    organization_id: int
    checked_at: datetime
    sources: list[SourceResult]


def require_organization(user: User) -> int:
    if user.organization_id is None:
        raise HTTPException(
            status_code=403,
            detail="Your account must be linked to an organization.",
        )
    return user.organization_id


@router.post(
    "/partner-check",
    response_model=PartnerCheckResult,
    response_model_exclude_none=True,
)
async def check_partner(
    body: PartnerCheckRequest,
    current_user: CurrentUser,
    session: SessionDep,
):
    organization_id = require_organization(current_user)
    identifier = "".join(body.identifier.split()).upper()

    if not re.fullmatch(r"ATU[0-9]{8}", identifier):
        raise HTTPException(
            status_code=422,
            detail="Enter an Austrian VAT / UID number: ATU followed by eight digits.",
        )

    try:
        valid = await check_vat_number(identifier)
    except HTTPException as exc:
        if exc.status_code != 503:
            raise
        vies_result = SourceResult(name="VIES", status="unavailable")
    else:
        vies_result = SourceResult(name="VIES", status="checked", valid=valid)

    sources = [
        vies_result,
        SourceResult(name="BMF Fake Company List", status="not_implemented"),
        SourceResult(name="HFU List", status="not_implemented"),
        SourceResult(name="Firmenbuch", status="not_implemented"),
        SourceResult(name="GISA", status="not_implemented"),
    ]

    check = PartnerCheck(
        identifier=identifier,
        organization_id=organization_id,
        initiated_by_user_id=current_user.id,
        sources=[source.model_dump(exclude_none=True) for source in sources],
    )
    session.add(check)
    session.commit()
    session.refresh(check)
    return check


@router.get(
    "/partner-checks",
    response_model=list[PartnerCheckResult],
    response_model_exclude_none=True,
)
def list_partner_checks(current_user: CurrentUser, session: SessionDep):
    organization_id = require_organization(current_user)
    statement = (
        select(PartnerCheck)
        .where(PartnerCheck.organization_id == organization_id)
        .order_by(PartnerCheck.checked_at.desc(), PartnerCheck.id.desc())
    )
    return session.exec(statement).all()


@router.get(
    "/partner-checks/{check_id}",
    response_model=PartnerCheckResult,
    response_model_exclude_none=True,
)
def get_partner_check(
    check_id: int,
    current_user: CurrentUser,
    session: SessionDep,
):
    organization_id = require_organization(current_user)
    statement = select(PartnerCheck).where(
        PartnerCheck.id == check_id,
        PartnerCheck.organization_id == organization_id,
    )
    check = session.exec(statement).first()
    if check is None:
        raise HTTPException(status_code=404, detail="Partner check not found.")
    return check