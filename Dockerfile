# syntax=docker/dockerfile:1

FROM node:latest as node_base
FROM python:latest

WORKDIR /root/Opportunity

RUN apt-get update
RUN apt-get install nano -y

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY --from=node_base / /
RUN npm install lzutf8

COPY . .

CMD [ "python", "opportunity/opportunity.py" ]
