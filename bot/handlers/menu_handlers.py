from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from aiogram_dialog import DialogManager, StartMode

from dialogs.settings import SettingsSG


menu_router = Router()


@menu_router.message(Command("settings"))
async def settings_command(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(SettingsSG.main, mode=StartMode.RESET_STACK)
    await message.delete()
