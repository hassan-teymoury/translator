# Translator API for en-fa

## Get started

### Python Setup

To launch the API with python script provided here, first install __python__ for your OS using its [official document](https://www.python.org/downloads/). Then install clone the repo and run the following command to install required packages:

```shell
pip install --no-cache-dir --upgrade -r requirements.txt
```
After installation finished, execute the python code located in __apps/main.py__:

```shell
cd translator
python3 app/main.py
```
After running the API, you should see the following output messages in your terminal:
```shell
INFO:     Started server process [43425]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8090 (Press CTRL+C to quit)
```

#### Request and Response

A GET method has been used for translator root that is __/translate/{phrase}__. Here __{phrase}__ is your __input text__. Here is an example to show the API response to an input text in Postman:

##### Request
input text = Data is most valueable asset in computer world

request url = http://0.0.0.0:8888/translate/Data is most valueable asset in computer world.

##### Response

```json
{
    "translate": {
        "words_list": [
            {
                "word": "Data",
                "lemmatized": "data",
                "meaning": [
                    "داده ها"
                ],
                "lemmatized_meaning": [
                    "داده ها"
                ],
                "upos_tag": "اسم",
                "number": "مفرد"
            },
            {
                "word": "is",
                "lemmatized": "be",
                "meaning": [
                    "این است که"
                ],
                "lemmatized_meaning": [
                    "باید"
                ],
                "upos_tag": "فعل کمکی",
                "number": ""
            },
            {
                "word": "most",
                "lemmatized": "most",
                "meaning": [
                    "بیشتر"
                ],
                "lemmatized_meaning": [
                    "بیشتر"
                ],
                "upos_tag": "قید حالت",
                "number": ""
            },
            {
                "word": "valueable",
                "lemmatized": "valueable",
                "meaning": [
                    "ارزشمند"
                ],
                "lemmatized_meaning": [
                    "ارزشمند"
                ],
                "upos_tag": "صفت",
                "number": ""
            },
            {
                "word": "asset",
                "lemmatized": "asset",
                "meaning": [
                    "مامور مالی"
                ],
                "lemmatized_meaning": [
                    "مامور مالی"
                ],
                "upos_tag": "اسم",
                "number": "مفرد"
            },
            {
                "word": "in",
                "lemmatized": "in",
                "meaning": [
                    "در داخل"
                ],
                "lemmatized_meaning": [
                    "در داخل"
                ],
                "upos_tag": "قید زمان یا مکان",
                "number": ""
            },
            {
                "word": "computer",
                "lemmatized": "computer",
                "meaning": [
                    "کامپوتر"
                ],
                "lemmatized_meaning": [
                    "کامپوتر"
                ],
                "upos_tag": "اسم",
                "number": "مفرد"
            },
            {
                "word": "world",
                "lemmatized": "world",
                "meaning": [
                    "جهان"
                ],
                "lemmatized_meaning": [
                    "جهان"
                ],
                "upos_tag": "اسم",
                "number": "مفرد"
            }
        ],
        "sent_meaning": [
            "داده ها ارزشمندترین دارایی در دنیای کامپیوتر هستند."
        ]
    }
}
```

### Docker 

To launch the API using docker first create an image with the following command:

```shell
docker build -t fastapi_translator:0.0.0 .
```

Then run the following command to create and execute the docker container:

```shell
docker run -d --name translator_container -p 8090:8090 fastapi_translator:0.0.0

```

