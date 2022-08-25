FROM python:3.10-slim-bullseye

WORKDIR /usr/src/app


COPY main.py main.py
COPY database.py database.py
COPY bot_commands bot_commands
COPY anime anime
COPY .env .env
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN touch db.sqlite

CMD [ "python","-u","./main.py" ]
