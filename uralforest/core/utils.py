"""Утилиты проекта."""

import re

from django.utils.text import slugify

_TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "",
    "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    "×": "x", "х": "h", "+": "-", "№": "n",
}


def translit(value: str) -> str:
    value = value.lower()
    return "".join(_TRANSLIT.get(ch, ch) for ch in value)


def make_slug(value: str, max_length: int = 200) -> str:
    """Слаг в латинице (транслитерация + slugify)."""
    slug = slugify(translit(value))
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug[:max_length] or "item"
