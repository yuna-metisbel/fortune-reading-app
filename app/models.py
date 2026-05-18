from datetime import date, datetime, time, timezone, timedelta

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

JST = timezone(timedelta(hours=9))


def _now_jst() -> datetime:
    return datetime.now(JST).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    browser_id: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now_jst)

    profiles: Mapped[list["Profile"]] = relationship(back_populates="user")
    readings: Mapped[list["Reading"]] = relationship(back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    nickname: Mapped[str] = mapped_column(String(100))
    birth_date: Mapped[date] = mapped_column(Date)
    birth_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    birth_place: Mapped[str | None] = mapped_column(String(200), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    blood_type: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now_jst)

    user: Mapped["User"] = relationship(back_populates="profiles")


class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(20))
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id"))
    profile_id_2: Mapped[int | None] = mapped_column(Integer, ForeignKey("profiles.id"), nullable=True)
    relationship_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    met_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    theme: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, default="")
    prompt_used: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    type_badge: Mapped[str | None] = mapped_column(String(50), nullable=True)
    payment_status: Mapped[str] = mapped_column(String(20), default="free")
    stripe_session_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    form_data_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now_jst)

    user: Mapped["User"] = relationship(back_populates="readings")
    profile: Mapped["Profile"] = relationship(foreign_keys=[profile_id])
    profile_2: Mapped["Profile | None"] = relationship(foreign_keys=[profile_id_2])
    chat_sessions: Mapped[list["ChatSession"]] = relationship(back_populates="reading")


class DailyFortune(Base):
    __tablename__ = "daily_fortunes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    birth_date: Mapped[date] = mapped_column(Date)
    fortune_date: Mapped[date] = mapped_column(Date)
    overall_luck: Mapped[int] = mapped_column(Integer)
    lucky_stone: Mapped[str] = mapped_column(String(100))
    stone_message: Mapped[str] = mapped_column(Text)
    lucky_color: Mapped[str] = mapped_column(String(50))
    lucky_number: Mapped[int] = mapped_column(Integer)
    nail_color: Mapped[str] = mapped_column(String(100))
    nail_color_code: Mapped[str] = mapped_column(String(7))
    nail_message: Mapped[str] = mapped_column(Text)
    fashion_base: Mapped[str] = mapped_column(String(50))
    fashion_accent: Mapped[str] = mapped_column(String(50))
    fashion_message: Mapped[str] = mapped_column(Text)
    one_liner: Mapped[str] = mapped_column(Text)
    message: Mapped[str] = mapped_column(Text)
    action_tip: Mapped[str] = mapped_column(Text)
    caution: Mapped[str] = mapped_column(Text)
    prediction: Mapped[str | None] = mapped_column(Text, nullable=True)
    prediction_result: Mapped[str | None] = mapped_column(String(10), nullable=True)
    prediction_checked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now_jst)

    user: Mapped["User"] = relationship()


class WeeklyArc(Base):
    __tablename__ = "weekly_arcs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    birth_date: Mapped[date] = mapped_column(Date)
    week_start: Mapped[date] = mapped_column(Date)
    theme: Mapped[str] = mapped_column(Text)
    story_seed: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now_jst)

    user: Mapped["User"] = relationship()


class DailyCompatibility(Base):
    __tablename__ = "daily_compatibilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    my_birth_date: Mapped[date] = mapped_column(Date)
    partner_birth_date: Mapped[date] = mapped_column(Date)
    partner_nickname: Mapped[str] = mapped_column(String(100))
    relationship_type: Mapped[str] = mapped_column(String(30))
    fortune_date: Mapped[date] = mapped_column(Date)
    compatibility_score: Mapped[int] = mapped_column(Integer)
    one_liner: Mapped[str] = mapped_column(Text)
    today_energy: Mapped[str] = mapped_column(Text)
    communication_tip: Mapped[str] = mapped_column(Text)
    do_this: Mapped[str] = mapped_column(Text)
    avoid_this: Mapped[str] = mapped_column(Text)
    power_word: Mapped[str] = mapped_column(String(100))
    evening_action: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now_jst)

    user: Mapped["User"] = relationship()


class LineSubscription(Base):
    __tablename__ = "line_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    subscribed: Mapped[bool] = mapped_column(Integer, default=1)  # SQLite doesn't have bool
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now_jst)

    user: Mapped["User"] = relationship()


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reading_id: Mapped[int] = mapped_column(Integer, ForeignKey("readings.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now_jst)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now_jst, onupdate=_now_jst)

    reading: Mapped["Reading"] = relationship(back_populates="chat_sessions")
    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="session", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_sessions.id"))
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now_jst)

    session: Mapped["ChatSession"] = relationship(back_populates="messages")
