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

FACE_SYSTEM_PROMPT = """あなたは人相学（面相学）の専門家です。
顔写真から、その人の性格・運勢・才能を読み取ります。

以下のJSON形式のみで回答してください。JSON以外のテキストは一切出力しないでください。

{
  "face_type": "(顔の形の分類: 丸顔/面長/逆三角/四角/卵型 から1つ)",
  "overall_impression": "(第一印象を1文で。20文字以内)",
  "personality": "(人相から読み取れる性格を2文で。合計60文字以内)",
  "hidden_talent": "(顔に表れている隠れた才能を1文で。30文字以内)",
  "love_tendency": "(恋愛傾向を1文で。30文字以内)",
  "career_fit": "(向いている仕事を具体的に2-3個。30文字以内)",
  "lucky_point": "(この顔の最も運気が高いパーツとその意味。30文字以内)",
  "advice": "(人相に基づく具体的アドバイス1つ。40文字以内)",
  "fortune_score": (1-100の整数。顔相の総合運)
}

ルール:
- 顔の各パーツ（額、眉、目、鼻、口、耳、輪郭）を観察して判断する
- 東洋人相学の知識を使う（額=知性、眉=感情、目=意志、鼻=金運、口=愛情、耳=健康運）
- 全フィールド合計300文字以内。短く断定的に
- ポジティブなトーンを基本とする
- 「かもしれません」は禁止。断定する
- JSONのみ出力"""

FACE_USER_PROMPT = """この顔写真を人相学の観点から分析してください。
額の広さ、眉の形、目の大きさと形、鼻の高さ、口元、輪郭の形を観察し、
性格・運勢・才能をJSON形式で出力してください。"""


@router.get("/face-reading")
async def face_reading_page(request: Request):
    return templates.TemplateResponse("face_reading.html", {"request": request})


@router.post("/api/face-reading/analyze")
async def analyze_face(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
):
    body = await request.json()
    image_data = body.get("image", "")
    if not image_data:
        return JSONResponse({"error": "画像がありません"}, status_code=400)

    # Strip data URL prefix if present
    if "," in image_data:
        image_data = image_data.split(",", 1)[1]

    media_type = "image/jpeg"
    if body.get("media_type"):
        media_type = body["media_type"]

    for attempt in range(2):
        try:
            raw = await generate_vision_message(FACE_SYSTEM_PROMPT, FACE_USER_PROMPT, image_data, media_type)
        except Exception:
            if attempt == 1:
                return JSONResponse({"error": "画像を処理できませんでした。顔がはっきり写った写真を使ってください"}, status_code=400)
            continue
        try:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            data = json.loads(match.group()) if match else json.loads(raw)
            break
        except (json.JSONDecodeError, ValueError, AttributeError):
            if attempt == 1:
                return JSONResponse({"error": "分析に失敗しました"}, status_code=500)

    return JSONResponse(data)
