import asyncio
import logging
import socket

from aiohttp import ClientSession, TCPConnector
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from config import config
from database.engine import init_db
from handlers.admin import admin_router
from handlers.menu import menu_router
from handlers.order import order_router
from handlers.start import start_router


class CustomAiohttpSession(AiohttpSession):
    """Force IPv4 connection to prevent Windows DNS timeout issues with dual-stack."""

    async def create_session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            self._session = ClientSession(
                connector=TCPConnector(family=socket.AF_INET),
                json_serialize=self.json_dumps,
            )
        return self._session


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    logger.info("Initializing database...")
    await init_db()
    logger.info("Database ready")

    session = CustomAiohttpSession()
    bot = Bot(
        token=config.BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(order_router)
    dp.include_router(admin_router)

    logger.info("Starting polling...")
    try:
        await dp.start_polling(bot, drop_pending_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())