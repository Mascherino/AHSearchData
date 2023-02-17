# syntax=docker/dockerfile:1

FROM node:latest as node_base
FROM python:latest

VOLUME ["/app/data", "/app/data/json"]

WORKDIR /app/
COPY --from=node_base / /
RUN npm install lzutf8

WORKDIR /root/Opportunity
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "python" ]

CMD [ "opportunity/opportunity.py" ]
