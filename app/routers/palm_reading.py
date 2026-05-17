import json
import re
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_browser_user
from app.models import User
from app.services.claude_client import generate_vision_message

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

PALM_SYSTEM_PROMPT = """あなたは手相学の専門家です。
手のひらの写真から、主要な手相線を読み取り運勢を占います。

以下のJSON形式のみで回答してください。JSON以外のテキストは一切出力しないでください。

{
  "hand_type": "(手の形の分類: 火の手/地の手/風の手/水の手 から1つ)",
  "life_line": "(生命線の特徴と意味。30文字以内)",
  "head_line": "(頭脳線の特徴と意味。30文字以内)",
  "heart_line": "(感情線の特徴と意味。30文字以内)",
  "fate_line": "(運命線の特徴と意味。30文字以内。見えない場合は「自分で道を切り拓くタイプ」等)",
  "special_sign": "(特殊な相があれば。スター線、仏眼、ますかけ線等。30文字以内。なければ最も特徴的な点)",
  "overall_fortune": "(手相から読み取れる総合運を1文で。30文字以内)",
  "love_fortune": "(恋愛運を1文で。30文字以内)",
  "money_fortune": "(金運を1文で。30文字以内)",
  "advice": "(手相に基づくアドバイスを1文で。40文字以内)",
  "fortune_score": (1-100の整数。手相の総合運)
}

ルール:
- 手のひらの線（生命線、頭脳線、感情線、運命線、太陽線など）を観察する
- 線の長さ、深さ、カーブ、分岐に言及する
- 全フィールド合計350文字以内
- 断定する。「かもしれません」は禁止
- ポジティブなトーン基本
- JSONのみ出力"""

PALM_USER_PROMPT = """この手のひらの写真を手相学の観点から分析してください。
生命線、頭脳線、感情線、運命線、その他の特殊な線や印を観察し、
運勢をJSON形式で出力してください。"""


@router.get("/palm-reading")
async def palm_reading_page(request: Request):
    return templates.TemplateResponse("palm_reading.html", {"request": request})


@router.post("/api/palm-reading/analyze")
async def analyze_palm(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
):
    body = await request.json()
    image_data = body.get("image", "")
    if not image_data:
        return JSONResponse({"error": "画像がありません"}, status_code=400)

    if "," in image_data:
        image_data = image_data.split(",", 1)[1]

    media_type = body.get("media_type", "image/jpeg")

    for attempt in range(2):
        raw = await generate_vision_message(PALM_SYSTEM_PROMPT, PALM_USER_PROMPT, image_data, media_type)
        try:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            data = json.loads(match.group()) if match else json.loads(raw)
            break
        except (json.JSONDecodeError, ValueError, AttributeError):
            if attempt == 1:
                return JSONResponse({"error": "分析に失敗しました"}, status_code=500)

    return JSONResponse(data)
