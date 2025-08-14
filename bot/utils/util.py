import os
import tempfile
from datetime import datetime
from typing import Optional
import uuid

from aiogram.types import Message, FSInputFile


def append_text_to_file(file_path: str, text: str, ensure_newline: bool = True) -> str:
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(text)
        if ensure_newline and not text.endswith("\n"):
            f.write("\n")
    return file_path


def write_text_to_new_file(text: str, filename: Optional[str] = None, directory: Optional[str] = None) -> str:
    if filename is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcript_{ts}.txt"
    if directory is None:
        directory = tempfile.gettempdir()
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
        if not text.endswith("\n"):
            f.write("\n")
    return path


async def send_file_and_delete(message: Message, file_path: str, caption: Optional[str] = None) -> None:
    try:
        file = FSInputFile(file_path)
        await message.answer_document(document=file, caption=caption)
    finally:
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass


async def send_text_as_file_then_delete(
    message: Message,
    text: str,
    filename: Optional[str] = None,
    caption: Optional[str] = None,
) -> None:
    temp_file = None
    try:
        # Use NamedTemporaryFile to avoid name collisions but keep file for sending
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
            if filename:
                # If a custom filename requested, we'll still write to tmp and pass explicit filename to FSInputFile
                pass
            tmp.write(text)
            if not text.endswith("\n"):
                tmp.write("\n")
            temp_file = tmp.name
        generated_name = filename or f"{uuid.uuid4().hex}.txt"
        file = FSInputFile(temp_file, filename=generated_name)
        await message.answer_document(document=file, caption=caption)
    finally:
        if temp_file:
            try:
                os.remove(temp_file)
            except FileNotFoundError:
                pass


