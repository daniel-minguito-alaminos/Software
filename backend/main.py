import re

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from api_token_auth import ApiTokenOrganization
from database import engine
from routers import api_tokens, auth, partner_checks
from vies import check_vat_number

app = FastAPI(title="BizPartnerCheck API")
app.include_router(auth.router)
app.include_router(api_tokens.router)
app.include_router(partner_checks.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/database")
def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1")).scalar_one()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        ) from exc

    return {"database": "connected"}


class VatCheckRequest(BaseModel):
    vat_number: str


@app.post("/checks/vat")
async def check_vat(body: VatCheckRequest):
    vat_number = "".join(body.vat_number.split()).upper()

    if not re.fullmatch(r"[A-Z]{2}[A-Z0-9]{2,12}", vat_number):
        raise HTTPException(
            status_code=422,
            detail="Enter a VAT number with a country prefix, for example ATU12345678.",
        )

    valid = await check_vat_number(vat_number)
    return {"vat_number": vat_number, "valid": valid}


@app.get("/test/api-token")
def test_api_token(organization_id: ApiTokenOrganization):
    return {"organization_id": organization_id}