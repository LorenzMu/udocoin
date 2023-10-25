FROM python:3.10

ENV SKIP_ENV_INPUT="yes"

WORKDIR /application

COPY ./requirements.txt /application

RUN pip install -r requirements.txt

RUN pip install "Werkzeug==2.2.2"

RUN pip install gunicorn

COPY . .

CMD ["flask", "run", "--host", "0.0.0.0"]