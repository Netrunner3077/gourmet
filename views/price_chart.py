from datetime import timedelta

import matplotlib
matplotlib.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
)
from PyQt5.QtCore import Qt

from utils.time_utils import utcnow

matplotlib.rcParams["font.family"] = "DejaVu Sans"
matplotlib.rcParams["axes.unicode_minus"] = False


class PriceChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._history = []
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        bar = QHBoxLayout()
        bar.setSpacing(8)

        lbl = QLabel("Период:")
        lbl.setObjectName("Hint")
        bar.addWidget(lbl)

        self.range_combo = QComboBox()
        self.range_combo.addItem("7 дней", 7)
        self.range_combo.addItem("30 дней", 30)
        self.range_combo.addItem("90 дней", 90)
        self.range_combo.addItem("Всё время", None)
        self.range_combo.setCurrentIndex(1)
        self.range_combo.currentIndexChanged.connect(self._redraw)
        bar.addWidget(self.range_combo)
        bar.addStretch()

        root.addLayout(bar)

        self.figure = Figure(figsize=(8, 3.2), dpi=100)
        self.figure.patch.set_facecolor("#FFFFFF")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background: #FFFFFF; border-radius: 12px;")
        self.canvas.setMinimumHeight(280)
        root.addWidget(self.canvas)

    def set_history(self, history: list[dict]):
        self._history = history or []
        self._redraw()

    def _redraw(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.set_facecolor("#FFFFFF")
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        for spine in ("left", "bottom"):
            ax.spines[spine].set_color("#E2E8F0")
        ax.tick_params(colors="#64748B", labelsize=9)
        ax.grid(True, color="#F1F5F9", linewidth=1)

        days = self.range_combo.currentData()
        history = self._history
        if days:
            cutoff = utcnow() - timedelta(days=days)
            history = [h for h in history if h["date"] >= cutoff]

        if not history:
            ax.text(0.5, 0.5, "Нет данных за выбранный период", ha="center", va="center", color="#94A3B8", fontsize=12, transform=ax.transAxes)
            self.canvas.draw()
            return

        history = sorted(history, key=lambda h: h["date"])
        dates = [h["date"] for h in history]
        prices = [h["price"] for h in history]

        ax.plot(
            dates, prices,
            color="#059669", linewidth=2.2,
            marker="o", markersize=4,
            markerfacecolor="#FFFFFF",
            markeredgecolor="#059669",
            markeredgewidth=1.6,
            zorder=3,
        )
        ax.fill_between(dates, prices, min(prices) * 0.98, сolor="#10B981", alpha=0.12, zorder=1,)

        min_p = min(prices)
        max_p = max(prices)
        mid_p = (min_p + max_p) / 2

        ax.axhline(mid_p, color="#0EA5E9", linewidth=1, linestyle="--", alpha=0.6, zorder=2)
        ax.text(dates[0], mid_p, f"  средняя ≈ {mid_p:.0f} ₽", color="#0284C7", fontsize=9, va="bottom", ha="left")

        ax.scatter([dates[-1]], [prices[-1]], color="#047857", s=70, zorder=4, edgecolor="#FFFFFF", linewidth=2)

        ax.set_ylabel("Цена, ₽", color="#64748B", fontsize=10)
        ax.margins(x=0.03, y=0.12)

        self.figure.autofmt_xdate(rotation=25, ha="right")
        self.figure.tight_layout()
        self.canvas.draw()