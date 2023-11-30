FROM python:3.11-slim-bookworm

WORKDIR /python_app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod a+x /python_app/docker/*.sh