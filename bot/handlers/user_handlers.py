from aiogram import Router, F
import asyncio
from aiogram.filters import CommandStart
from aiogram.types import Message
from io import BytesIO

from speech.core import DeepgramSpeech, STTOptions
from utils.util import send_text_as_file_then_delete


user_router = Router()

stt = DeepgramSpeech(api_key="184d88e033362e8347aff7f5238e4d0d7e106a05")

@user_router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Я готов к работе. Используй /settings для настроек.")


async def _download_file_bytes(message: Message, file_id: str) -> bytes:
    file = await message.bot.get_file(file_id)
    buffer = BytesIO()
    await message.bot.download(file, destination=buffer)
    return buffer.getvalue()


@user_router.message(F.voice)
async def handle_voice_message(message: Message):
    notice = await message.answer("⏳ Распознаю голосовое сообщение…")
    try:
        data = await _download_file_bytes(message, message.voice.file_id)
        text = await asyncio.to_thread(stt.transcribe_bytes, data, STTOptions())
        if text:
            await notice.delete()
            # No original filename for voice messages → use UUID-based default name
            await send_text_as_file_then_delete(message, text, filename=None, caption="✅ Готово")
        else:
            await notice.edit_text("Не удалось распознать речь.")
    except Exception as e:
        await notice.edit_text("Ошибка распознавания. Проверьте ключ DEEPGRAM_API_KEY и попробуйте снова.")


@user_router.message(F.audio)
async def handle_audio_message(message: Message):
    notice = await message.reply("⏳ Распознаю аудиофайл…")
    try:
        data = await _download_file_bytes(message, message.audio.file_id)
        text = await asyncio.to_thread(stt.transcribe_bytes, data, STTOptions())
        if text:
            await notice.delete()
            # Use uploaded audio's original filename (base) for transcript file name
            original_name = message.audio.file_name or "audio"
            base_name = original_name.rsplit(".", 1)[0] if "." in original_name else original_name
            transcript_name = f"{base_name}.txt"
            await send_text_as_file_then_delete(message, text, filename=transcript_name, caption="✅ Готово")
        else:
            await notice.edit_text("Не удалось распознать речь.")
    except Exception:
        await notice.edit_text("Ошибка распознавания. Проверьте ключ DEEPGRAM_API_KEY и попробуйте снова.")

