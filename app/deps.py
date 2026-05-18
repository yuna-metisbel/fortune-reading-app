import uuid

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.database import get_db
from app.models import User

COOKIE_NAME = "fortune_bid"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365 * 5  # 5 years


class BrowserIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        browser_id = request.cookies.get(COOKIE_NAME)
        need_set = False
        if not browser_id:
            browser_id = str(uuid.uuid4())
            need_set = True
        request.state.browser_id = browser_id
        request.state.theme = request.cookies.get("luna_theme", "default")
        response = await call_next(request)
        if need_set:
            response.set_cookie(
                COOKIE_NAME,
                browser_id,
                max_age=COOKIE_MAX_AGE,
                httponly=True,
                samesite="lax",
            )
        return response


async def get_browser_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    browser_id = request.state.browser_id

    result = await db.execute(select(User).where(User.browser_id == browser_id))
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(name="user", browser_id=browser_id)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
