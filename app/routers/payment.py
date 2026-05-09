import json
import traceback
from pathlib import Path

import stripe
from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models import Reading, User

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

PRICES = {
    "personal": {"amount": 2000, "label": "魂のリーディング（個人鑑定）"},
    "compatibility": {"amount": 3000, "label": "相性リーディング（二人の鑑定）"},
}


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

        stripe.api_key = settings.stripe_secret_key
        base = settings.base_url

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "jpy",
                    "product_data": {"name": price["label"]},
                    "unit_amount": price["amount"],
                },
                "quantity": 1,
            }],
            mode="payment",
            client_reference_id=str(reading.id),
            success_url=f"{base}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base}/payment/cancel?reading_type={body.reading_type}",
        )

        reading.stripe_session_id = session.id
        await db.commit()

        return JSONResponse({"checkout_url": session.url})
    except Exception as e:
        return JSONResponse({"error": str(e), "trace": traceback.format_exc()}, status_code=500)


@router.get("/payment/success")
async def payment_success(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    stripe.api_key = settings.stripe_secret_key

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.StripeError:
        raise HTTPException(status_code=400, detail="Invalid session")

    if session.payment_status != "paid":
        raise HTTPException(status_code=400, detail="Payment not completed")

    reading_id = int(session.client_reference_id)
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
