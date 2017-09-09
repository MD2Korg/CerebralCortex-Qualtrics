FROM python:3-alpine
MAINTAINER Ryan Graves rgraves6@memphis.edu

WORKDIR /usr/arc/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python3", "./qualtrics.py" ]
CMD [ "dataCenter apiToken surveyId" ]
