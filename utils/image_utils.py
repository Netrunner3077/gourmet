import os

from PIL import Image

from PyQt5.QtGui import (
    QPixmap, QPainter, QPainterPath, QBrush, QColor, QFont
)
from PyQt5.QtCore import Qt

from config import AVATARS_DIR


def make_circular_pixmap(source, size: int = 140) -> QPixmap | None:
    """
        Принимает путь (str) или QPixmap → возвращает круглый QPixmap.
        Центральный кроп + круглая маска. Возвращает None, если не удалось.
    """
    if isinstance(source, QPixmap):
        pix = source
    elif isinstance(source, str):
        if not os.path.exists(source):
            return None
        pix = QPixmap(source)
    else:
        return None

    if pix.isNull():
        return None

    pix = pix.scaled(
        size, size,
        Qt.KeepAspectRatioByExpanding,
        Qt.SmoothTransformation
    )
    if pix.width() > size or pix.height() > size:
        x = (pix.width() - size) // 2
        y = (pix.height() - size) // 2
        pix = pix.copy(x, y, size, size)

    rounded = QPixmap(size, size)
    rounded.fill(Qt.transparent)

    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pix)
    painter.end()
    return rounded


def save_avatar(user_id, source_path: str) -> str | None:
    """Копирует выбранное изображение в ресурсы под именем user_id.png."""

    if not os.path.exists(source_path):
        return None

    os.makedirs(AVATARS_DIR, exist_ok=True)
    dest = os.path.join(AVATARS_DIR, f"{user_id}.png")

    try:
        img = Image.open(source_path).convert("RGB")
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img = img.resize((400, 400), Image.LANCZOS)
        img.save(dest, "PNG", optimize=True)
        return dest
    except Exception as e:
        print(f"[AVATAR] Ошибка сохранения: {e}")
        return None


def get_avatar_path(avatar_field: str | None,
                    size: int = 140) -> QPixmap | None:
    """
        Возвращает круглый QPixmap аватара по сохранённому пути.
        Если путь пустой/битый — возвращает None (вызывающая сторона подставит placeholder).
    """
    if avatar_field and os.path.exists(avatar_field):
        pix = make_circular_pixmap(avatar_field, size)
        if pix:
            return pix
    return None


def make_placeholder_avatar(letter: str, size: int = 140,
                            bg: str = "#0284C7") -> QPixmap:
    """Круглый placeholder с буквой (первая буква логина)."""
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)

    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(QColor(bg)))
    painter.drawEllipse(0, 0, size, size)

    painter.setPen(QColor("#FFFFFF"))
    font = QFont("Segoe UI", int(size * 0.42), QFont.Bold)
    painter.setFont(font)
    painter.drawText(pix.rect(), Qt.AlignCenter, (letter or "?").upper())
    painter.end()
    return pix