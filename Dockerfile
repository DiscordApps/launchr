FROM python:3.7-alpine3.10
RUN apk add rsync

RUN pip install cookiecutter==1.6.0 colorama==0.4.1 pytz

RUN mkdir /out
ADD . /template

ENTRYPOINT ["python", "/template/generate.py"]
CMD ["new"]


