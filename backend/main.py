import re
import httpx
from fastapi import FastAPI
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from database import engine
from routers import auth

app = FastAPI(title="BizPartnerCheck API")
app.include_router(auth.router)


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

VIES_URL = "https://ec.europa.eu/taxation_customs/vies/rest-api/check-vat-number"


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

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                VIES_URL,
                json={
                    "countryCode": vat_number[:2],
                    "vatNumber": vat_number[2:],
                },
            )
            response.raise_for_status()
            result = response.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(
            status_code=503,
            detail="VIES is temporarily unavailable. Please try again later.",
        )

    if (
        not isinstance(result, dict)
        or result.get("actionSucceed") is False
        or result.get("errorWrappers")
        or not isinstance(result.get("valid"), bool)
    ):
        raise HTTPException(
            status_code=503,
            detail="VIES could not complete the check. Please try again later.",
        )

    return {"vat_number": vat_number, "valid": result["valid"]}