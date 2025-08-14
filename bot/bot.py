import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram_dialog import setup_dialogs

from handlers.user_handlers import user_router
from handlers.menu_handlers import menu_router
from dialogs.settings import settings_dialog

from config.logging_config import get_logger

logger = get_logger(__name__)


server = TelegramAPIServer.from_base("95.181.167.217:8081")
session = AiohttpSession(api=server)


token = "7154028425:AAFGX2ua5izWNluSE4Lk9-3LbqOiawKC0yE"


async def on_startup(bot: Bot):
    logger.info("Bot is starting...")

async def on_shutdown(bot: Bot):
    logger.info("Bot is shutting down...")


async def start_polling(dp, bot):
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def main():
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True),
        # session=session,
    )
    dp = Dispatcher()
    dp.include_router(user_router)
    dp.include_router(menu_router)
    dp.include_router(settings_dialog)

    setup_dialogs(dp)

    try:
        await on_startup(bot)
        await start_polling(dp, bot)
    finally:
        await on_shutdown(bot)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())