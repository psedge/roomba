FROM python:3.7-alpine

ENV FLASK_ENV="development"

COPY . /opt/roomba
WORKDIR /opt/roomba

RUN pip install -r requirements.txt
CMD ["python", "-u", "-m", "flask", "run", "-h 0.0.0.0", "-p 5000"]
