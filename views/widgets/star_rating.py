from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont


class StarRatingDisplay(QWidget):
    """Только для отображения рейтинга (только чтение)."""
    def __init__(self, value: float = 0.0, size: int = 18, parent=None):
        super().__init__(parent)
        self._size = size
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)
        self._layout.addStretch()
        self._build(value)
        self._layout.addStretch()

    def _build(self, value: float):
        while self._layout.count():
            item = self._layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        full = int(value)
        half = 1 if value - full >= 0.5 else 0
        empty = 5 - full - half

        for _ in range(full):
            self._layout.addWidget(self._make_star("★", "#F59E0B"))
        for _ in range(half):
            self._layout.addWidget(self._make_star("⯨", "#F59E0B"))
        for _ in range(empty):
            self._layout.addWidget(self._make_star("☆", "#CBD5E1"))

        value_label = QLabel(f"{value:.1f}")
        value_label.setFont(QFont("Arial", self._size - 4, QFont.Bold))
        value_label.setStyleSheet("color: #B45309;")
        value_label.setObjectName("RatingValueLabel")
        self._layout.addWidget(value_label)

    def _make_star(self, symbol: str, color: str) -> QLabel:
        lbl = QLabel(symbol)
        lbl.setStyleSheet(f"color: {color};")
        lbl.setFont(QFont("Arial", self._size))
        return lbl

    def update_value(self, value: float):
        """Перерисовать рейтинг без пересоздания виджета."""
        self._layout.addStretch()
        self._build(value)
        self._layout.addStretch()


class StarRatingInput(QWidget):
    """Интерактивный виджет для выставления оценки (1–5)."""
    rating_changed = pyqtSignal(int)

    def __init__(self, value: int = 0, size: int = 28, parent=None):
        super().__init__(parent)
        self._value = value
        self._hover = 0
        self.size_ = size

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.buttons = []
        for i in range(1, 6):
            btn = QPushButton("☆")
            btn.setObjectName("StarButton")
            btn.setFixedSize(size + 6, size + 6)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(QFont("Arial", size))
            btn.enterEvent = self._make_enter(i)
            btn.leaveEvent = self._make_leave()
            btn.clicked.connect(self._make_click(i))
            self.buttons.append(btn)
            layout.addWidget(btn)

        self.hint = QLabel(self._hint_text())
        self.hint.setObjectName("Hint")
        self.hint.setStyleSheet("color: #94A3B8; padding-left: 8px;")
        layout.addWidget(self.hint)
        layout.addStretch()

        self._refresh()

    def _make_enter(self, idx):
        def handler(_):
            self._hover = idx
            self._refresh()
        return handler

    def _make_leave(self):
        def handler(_):
            self._hover = 0
            self._refresh()
        return handler

    def _make_click(self, idx):
        def handler():
            self._value = idx
            self._refresh()
            self.rating_changed.emit(idx)
        return handler

    def _refresh(self):
        display = self._hover or self._value
        for i, btn in enumerate(self.buttons, start=1):
            btn.setText("★" if i <= display else "☆")
            color = "#F59E0B" if i <= display else "#CBD5E1"
            btn.setStyleSheet(
                f"QPushButton#StarButton {{"
                f"  background: transparent; border: none;"
                f"  color: {color}; padding: 0;"
                f"}}"
            )
        self.hint.setText(self._hint_text())

    def _hint_text(self) -> str:
        if not self._value and not self._hover:
            return "Поставьте оценку"
        return {
            1: "Ужасно",
            2: "Плохо",
            3: "Нормально",
            4: "Хорошо",
            5: "Отлично",
        }.get(self._hover or self._value, "")

    def value(self) -> int:
        return self._value

    def set_value(self, v: int):
        """Установить значение БЕЗ эмита сигнала (для синхронизации)."""
        self._value = max(0, min(5, int(v)))
        self._refresh()

    def set_value_silent(self, v: int):
        """Алиас для set_value — на случай явного намерения."""
        self.set_value(v)