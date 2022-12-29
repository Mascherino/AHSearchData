# syntax=docker/dockerfile:1

FROM python:latest

WORKDIR /root/Opportunity

RUN apt-get update
RUN apt-get install nano -y

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "opportunity/opportunity.py" ]
