import base64
import json
import traceback
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Reading, User

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

PRICES = {
    "personal": {"amount": 2000, "label": "魂のリーディング（個人鑑定）"},
    "compatibility": {"amount": 3000, "label": "相性リーディング（二人の鑑定）"},
}


def _paypal_base_url() -> str:
    if settings.paypal_mode == "live":
        return "https://api-m.paypal.com"
    return "https://api-m.sandbox.paypal.com"


async def _paypal_access_token() -> str:
    credentials = base64.b64encode(
        f"{settings.paypal_client_id}:{settings.paypal_client_secret}".encode()
    ).decode()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_paypal_base_url()}/v1/oauth2/token",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "client_credentials"},
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


class CheckoutRequest(BaseModel):
    reading_type: str
    form_data: dict


@router.post("/api/payment/create-checkout")
async def create_checkout(
    body: CheckoutRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    if body.reading_type not in PRICES:
        raise HTTPException(status_code=400, detail="Invalid reading type")

    try:
        price = PRICES[body.reading_type]

        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(name="default")
            db.add(user)
            await db.flush()

        reading = Reading(
            user_id=user.id,
            type=body.reading_type,
            profile_id=0,
            theme=body.form_data.get("theme", ""),
            payment_status="pending",
            form_data_json=json.dumps(body.form_data, ensure_ascii=False),
        )
        db.add(reading)
        await db.commit()
        await db.refresh(reading)

        token = await _paypal_access_token()
        base = settings.base_url

        order_payload = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "reference_id": str(reading.id),
                "description": price["label"],
                "amount": {
                    "currency_code": "JPY",
                    "value": str(price["amount"]),
                },
            }],
            "application_context": {
                "brand_name": "Educatelling",
                "locale": "ja-JP",
                "return_url": f"{base}/payment/success",
                "cancel_url": f"{base}/payment/cancel?reading_type={body.reading_type}",
                "user_action": "PAY_NOW",
            },
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{_paypal_base_url()}/v2/checkout/orders",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=order_payload,
            )
            resp.raise_for_status()
            order = resp.json()

        approval_url = next(
            link["href"] for link in order["links"] if link["rel"] == "approve"
        )

        reading.stripe_session_id = order["id"]
        await db.commit()

        return JSONResponse({"checkout_url": approval_url})
    except Exception as e:
        return JSONResponse({"error": str(e), "trace": traceback.format_exc()}, status_code=500)


@router.get("/payment/success")
async def payment_success(
    request: Request,
    token: str = "",
    PayerID: str = "",
    session_id: str = "",
    db: AsyncSession = Depends(get_db),
):
    order_id = token or session_id
    if not order_id:
        raise HTTPException(status_code=400, detail="Missing order ID")

    try:
        access_token = await _paypal_access_token()

        async with httpx.AsyncClient() as client:
            capture_resp = await client.post(
                f"{_paypal_base_url()}/v2/checkout/orders/{order_id}/capture",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
            )
            capture_resp.raise_for_status()
            capture_data = capture_resp.json()

        if capture_data["status"] != "COMPLETED":
            raise HTTPException(status_code=400, detail="Payment not completed")

        reading_id = int(capture_data["purchase_units"][0]["reference_id"])
        reading = await db.get(Reading, reading_id)
        if reading is None:
            raise HTTPException(status_code=404, detail="Reading not found")

        reading.payment_status = "paid"
        await db.commit()

        form_data = json.loads(reading.form_data_json) if reading.form_data_json else {}

        return templates.TemplateResponse(
            "payment_success.html",
            {
                "request": request,
                "reading": reading,
                "form_data": form_data,
            },
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail=f"PayPal error: {e.response.text}")


@router.get("/payment/cancel")
async def payment_cancel(
    request: Request,
    reading_type: str = "personal",
):
    redirect_url = "/reading/new" if reading_type == "personal" else "/compatibility/new"
    return templates.TemplateResponse(
        "payment_cancel.html",
        {"request": request, "redirect_url": redirect_url},
    )
