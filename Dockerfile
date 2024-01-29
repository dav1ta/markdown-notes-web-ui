FROM python:3.10-alpine


COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "manage.py", "runserver","--host", "0.0.0.0"]

