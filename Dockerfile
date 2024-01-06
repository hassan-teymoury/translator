FROM python:3.10.12

WORKDIR /translator

ADD . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8090

CMD [ "python3", "app/main.py" ]