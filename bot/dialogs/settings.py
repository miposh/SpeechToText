from typing import Any

from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery

from aiogram_dialog import Dialog, DialogManager, Window, ShowMode
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Select
from aiogram_dialog.widgets.text import Const, Format

from speech.core import STTOptions


class SettingsSG(StatesGroup):
    main = State()
    language = State()
    model = State()


LANGUAGE_CHOICES: list[tuple[str, str]] = [
    ("Русский (ru)", "ru"),
    ("Английский (en)", "en"),
    ("Испанский (es)", "es"),
]

MODEL_CHOICES: list[tuple[str, str]] = [
    ("Nova 3", "nova-3"),
    ("Base", "base"),
]


async def on_dialog_start(start_data: Any, manager: DialogManager):
    opts = STTOptions()
    manager.dialog_data["opts"] = {
        "model": opts.model,
        "language": opts.language,
        "smart_format": opts.smart_format,
        "punctuate": opts.punctuate,
        "paragraphs": opts.paragraphs,
        "utterances": opts.utterances,
    }


async def getter(dialog_manager: DialogManager, **kwargs):
    opts: dict[str, Any] = dialog_manager.dialog_data.get("opts", {})
    return {
        "opts": opts,
        "languages": LANGUAGE_CHOICES,
        "models": MODEL_CHOICES,
    }


async def toggle_option(_: CallbackQuery, widget: Button, manager: DialogManager):
    key = getattr(widget, "widget_id", None)
    opts: dict[str, Any] = manager.dialog_data.get("opts", {})
    if key and key in opts and isinstance(opts[key], bool):
        opts[key] = not opts[key]
    manager.dialog_data["opts"] = opts


async def set_language(_: CallbackQuery, __: Any, manager: DialogManager, item_id: str):
    opts: dict[str, Any] = manager.dialog_data.get("opts", {})
    opts["language"] = item_id
    manager.dialog_data["opts"] = opts
    await manager.switch_to(SettingsSG.main)


async def set_model(_: CallbackQuery, __: Any, manager: DialogManager, item_id: str):
    opts: dict[str, Any] = manager.dialog_data.get("opts", {})
    opts["model"] = item_id
    manager.dialog_data["opts"] = opts
    await manager.switch_to(SettingsSG.main)


async def close_dialog(callback: CallbackQuery, _: Button, manager: DialogManager):
    if callback.message:
        await callback.message.delete()
    await manager.done(show_mode=ShowMode.NO_UPDATE)


main_window = Window(
    Const("⚙️ Настройки речевого распознавания"),
    Format(
        "\n<b>Модель</b>: {opts[model]}\n"
        "<b>Язык</b>: {opts[language]}\n\n"
        "<b>Опции</b>:\n"
        "• smart_format: {opts[smart_format]}\n"
        "• punctuate: {opts[punctuate]}\n"
        "• paragraphs: {opts[paragraphs]}\n"
        "• utterances: {opts[utterances]}\n"
    ),
    SwitchTo(Const("🌐 Язык"), id="to_language", state=SettingsSG.language),
    SwitchTo(Const("🧠 Модель"), id="to_model", state=SettingsSG.model),
    Button(Const("smart_format"), id="smart_format", on_click=toggle_option),
    Button(Const("punctuate"), id="punctuate", on_click=toggle_option),
    Button(Const("paragraphs"), id="paragraphs", on_click=toggle_option),
    Button(Const("utterances"), id="utterances", on_click=toggle_option),
    Button(Const("Закрыть"), id="close", on_click=close_dialog),
    state=SettingsSG.main,
    getter=getter,
)


language_window = Window(
    Const("Выберите язык"),
    Select(
        Format("{item[0]}"),
        id="lang_select",
        items="languages",
        item_id_getter=lambda x: x[1],
        on_click=set_language,
    ),
    SwitchTo(Const("← Назад"), id="back_to_main_from_language", state=SettingsSG.main),
    state=SettingsSG.language,
    getter=getter,
)


model_window = Window(
    Const("Выберите модель"),
    Select(
        Format("{item[0]}"),
        id="model_select",
        items="models",
        item_id_getter=lambda x: x[1],
        on_click=set_model,
    ),
    SwitchTo(Const("← Назад"), id="back_to_main_from_model", state=SettingsSG.main),
    state=SettingsSG.model,
    getter=getter,
)


settings_dialog = Dialog(
    main_window,
    language_window,
    model_window,
    on_start=on_dialog_start,
)


