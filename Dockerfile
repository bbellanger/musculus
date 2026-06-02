FROM python:3.11-slim

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
#USER appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "settings.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
