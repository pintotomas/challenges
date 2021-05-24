FROM python:3.6

WORKDIR /src
COPY . ./src
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development 
EXPOSE 5000
EXPOSE 27017