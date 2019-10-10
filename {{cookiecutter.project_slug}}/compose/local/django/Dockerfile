FROM python:3.7-alpine3.10

ENV PYTHONUNBUFFERED 1

RUN apk update \
  # psycopg2 dependencies
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add postgresql-dev \
  # Pillow dependencies
  && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
  # CFFI dependencies
  && apk add libffi-dev py-cffi \
  # Translations dependencies
  && apk add gettext \
  # https://docs.djangoproject.com/en/dev/ref/django-admin/#dbshell
  && apk add postgresql-client

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install -r /requirements/local.txt

COPY ./compose/local/django /scripts

RUN mv /scripts/entrypoint /entrypoint \
    && mv /scripts/start /start \
    && mv /scripts/celery/worker/start /start-celeryworker \
    && mv /scripts/celery/beat/start /start-celerybeat \
    && mv /scripts/celery/flower/start /start-flower \
    && rm -r /scripts \
    && sed -i 's/\r$//g' /entrypoint \
    && chmod +x /entrypoint \
    && sed -i 's/\r$//g' /start \
    && chmod +x /start \
    && sed -i 's/\r$//g' /start-celeryworker \
    && chmod +x /start-celeryworker \
    && sed -i 's/\r$//g' /start-celerybeat \
    && chmod +x /start-celerybeat \
    && sed -i 's/\r$//g' /start-flower \
    && chmod +x /start-flower

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
