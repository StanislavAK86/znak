FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements из папки beckend
COPY beckend/requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Копируем весь backend
COPY beckend/ .

# Создаем папки для статики
RUN mkdir -p static media

EXPOSE 8000

# Запускаем Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "znak.wsgi:application"]
