import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

def get_admin_ids() -> list[int]:
    raw_ids = os.getenv("ADMIN_IDS") or ""
    return [int(x) for x in raw_ids.split(",") if x.isdigit()]

@dataclass
class DbConfig:
    path: str = "database/barber_book.db"

@dataclass
class TgBot:
    token: str = os.getenv("BOT_TOKEN")
    admin_ids: list[int] = field(default_factory=get_admin_ids)
@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig


config = Config(tg_bot=TgBot(),db=DbConfig())