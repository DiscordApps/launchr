FROM python:3.7-alpine

RUN pip install cookiecutter==1.6.0

RUN mkdir /out
ADD . /template

CMD cookiecutter /template --output-dir /out


