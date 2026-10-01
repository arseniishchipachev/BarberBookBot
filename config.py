import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

def get_admin_ids() -> list[int]:
    raw_ids = os.getenv("ADMIN_IDS") or ""
    return [int(x) for x in raw_ids.split(",") if x.isdigit()]

@dataclass
class DbConfig:
    user: str = field(default_factory=lambda: os.getenv("POSTGRES_USER", "Barber_admin"))
    password:  str = field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD", "secret_password"))
    database: str = field(default_factory=lambda: os.getenv("POSTGRES_DB", "barbershop_db"))
    host: str = field(default_factory=lambda: os.getenv("POSTGRES_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("POSTGRES_PORT", "5432")))

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

@dataclass
class TgBot:
    token: str = os.getenv("BOT_TOKEN")
    admin_ids: list[int] = field(default_factory=get_admin_ids)
@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig


config = Config(tg_bot=TgBot(),db=DbConfig())