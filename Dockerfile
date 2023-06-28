FROM python:3.10
ENV OPENAI_API_KEY=<Insert your API Key here>
ENV OPENAI_API_BASE=<Insert your API endpoint. It should look something like: https://nrknordopenai.openai.azure.com/
ENV OPENAI_API_TYPE=azure
ENV OPENAI_API_VERSION=2022-12-01

COPY . /srv/texthelper_app
WORKDIR /srv/texthelper_app

COPY ./requirements.txt //srv/texthelper_app/requirements.txt

RUN pip install -r requirements.txt

COPY . /srv/texthelper_app

ENTRYPOINT [ "python" ]
CMD ["texthelper.py" ]



