FROM python:3.7

WORKDIR /code

COPY . .
RUN pip install -r requirements.txt
RUN python -m pip install flake8

ENV PYTHONPATH "${PYTHONPATH}:/code/"
