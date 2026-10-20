from PyQt5.QtWidgets import (
    QGraphicsDropShadowEffect, QFrame, QLabel, QWidget, QHBoxLayout
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt


def add_shadow(widget, blur=28, offset=6, alpha=28):
    """Мягкая тень под виджетом."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, offset)
    c = QColor("#0F172A")
    c.setAlpha(alpha)
    shadow.setColor(c)
    widget.setGraphicsEffect(shadow)
    return shadow


def make_divider(horizontal=True) -> QFrame:
    line = QFrame()
    line.setObjectName("Divider")
    if horizontal:
        line.setFixedHeight(1)
    else:
        line.setFixedWidth(1)
    return line


def badge(text: str, bg: str, fg: str = "#FFFFFF") -> QLabel:
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(
        f"background:{bg}; color:{fg}; border-radius: 9px;"
        f"padding: 2px 9px; font-size: 11px; font-weight: 700;"
    )
    return lbl


def section_header(title: str, subtitle: str = "") -> QWidget:
    """Заголовок секции с опциональным подзаголовком."""
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(10)

    t = QLabel(title)
    t.setObjectName("SectionTitleLarge")
    lay.addWidget(t)

    if subtitle:
        s = QLabel(subtitle)
        s.setObjectName("Hint")
        lay.addWidget(s)
    lay.addStretch()
    return w