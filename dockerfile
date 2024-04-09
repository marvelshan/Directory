FROM python:3.10

WORKDIR /app

RUN python3 -m pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["sh", "-c", "celery -A directory worker -l info & gunicorn directory.wsgi:application --bind 0.0.0.0:8000"]