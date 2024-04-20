FROM python:3.12.3-slim-bullseye
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /usr/src/app/

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
COPY ./requirements.txt /usr/src/app/requirements.txt
COPY . /usr/src/app/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]