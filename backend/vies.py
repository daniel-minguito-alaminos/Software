import httpx
from fastapi import HTTPException

VIES_URL = "https://ec.europa.eu/taxation_customs/vies/rest-api/check-vat-number"


async def check_vat_number(vat_number: str) -> bool:
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
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail="VIES is temporarily unavailable. Please try again later.",
        ) from exc

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

    return result["valid"]
