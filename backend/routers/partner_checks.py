import re
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from auth_session import CurrentUser
from vies import check_vat_number

router = APIRouter(tags=["partner-checks"])


class PartnerCheckRequest(BaseModel):
    identifier: str


class SourceResult(BaseModel):
    name: str
    status: Literal["checked", "unavailable", "not_implemented"]
    valid: bool | None = None


class PartnerCheckResult(BaseModel):
    identifier: str
    organization_id: int
    sources: list[SourceResult]


@router.post(
    "/partner-check",
    response_model=PartnerCheckResult,
    response_model_exclude_none=True,
)
async def check_partner(body: PartnerCheckRequest, current_user: CurrentUser):
    organization_id = current_user.organization_id
    if organization_id is None:
        raise HTTPException(
            status_code=403,
            detail="Your account must be linked to an organization to run a partner check.",
        )

    identifier = "".join(body.identifier.split()).upper()
    if not re.fullmatch(r"ATU[0-9]{8}", identifier):
        raise HTTPException(
            status_code=422,
            detail="Enter an Austrian VAT / UID number in the format ATU followed by eight digits.",
        )

    try:
        valid = await check_vat_number(identifier)
    except HTTPException as exc:
        if exc.status_code != 503:
            raise
        vies_result = SourceResult(name="VIES", status="unavailable")
    else:
        vies_result = SourceResult(name="VIES", status="checked", valid=valid)

    return PartnerCheckResult(
        identifier=identifier,
        organization_id=organization_id,
        sources=[
            vies_result,
            SourceResult(name="BMF Fake Company List", status="not_implemented"),
            SourceResult(name="HFU List", status="not_implemented"),
            SourceResult(name="Firmenbuch", status="not_implemented"),
            SourceResult(name="GISA", status="not_implemented"),
        ],
    )
