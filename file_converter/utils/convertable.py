from __future__ import annotations
import aiofiles
from file_converter.utils.commands import run
import random
from PyPDF4 import PdfFileReader
from PyPDF4.utils import PyPdfError
import io
from os.path import splitext
import string
import time
from fastapi import File
from os.path import exists
from abc import ABC, abstractmethod
import re

SUPPORTED_TYPES: list[str] = []
TYPES: dict[str, type[Convertable]] = dict()


class Convertable(ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        TYPES[cls.get_name()] = cls
        SUPPORTED_TYPES.append(cls.get_name())

    @classmethod
    def get_name(cls) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

    @staticmethod
    @abstractmethod
    def convert(file_name: str):
        pass


class Doc(Convertable):
    @staticmethod
    async def convert(file_name: str):
        await run(f"cd static; libreoffice --headless --convert-to pdf {file_name}")


class Docx(Convertable):
    @staticmethod
    async def convert(file_name: str):
        await run(f"cd static; libreoffice --headless --convert-to pdf {file_name}")


def random_str(n):
    alph = string.ascii_letters
    s = ""
    for i in range(n):
        s += alph[random.randint(0, len(alph) - 1)]
    return s


async def convert(file: File, ext: str, static_folder: str):
    memory_file = await file.read()
    name = str(time.time()) + "_" + random_str(10) + "." + splitext(file.filename)[1].replace('.', '')
    path = static_folder + '/' + name
    async with aiofiles.open(path, 'wb') as saved_file:
        await saved_file.write(memory_file)
    await file.close()
    file_name, extension = splitext(path)  # [0] - путь + имя, [1] - расширение
    extension = extension.lower()[1:]  # убрать точку перед расширением
    if not ext == extension:
        await TYPES[extension].convert(name)
        await run(f"rm static/{name} ")
    return f"{file_name}.{ext}"


async def check_pdf_ok(full_file: str):
    if not exists(full_file):
        return False
    async with aiofiles.open(full_file, 'rb') as f:
        try:
            f = await f.read()
            pdf = PdfFileReader(io.BytesIO(f))
            info = pdf.getDocumentInfo()
            return bool(info)
        except PyPdfError:
            return False
