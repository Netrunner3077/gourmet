# Используем официальный легковесный образ Python
FROM python:3.11-slim

# Устанавливаем системные библиотеки, необходимые для работы PyQt5 (GUI)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libfontconfig1 \
    libxi6 \
    libxtst6 \
    libdbus-1-3 \
    libegl1 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxcb-xinput0 \
    libxcb-xrm0 \
    libxkbcommon-x11-0 \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Запрещаем Python создавать .pyc файлы и включаем вывод логов в консоль без буферизации
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Сначала копируем только requirements.txt (для кэширования слоев Docker)
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Команда для запуска
CMD ["python", "gourmet.py"]