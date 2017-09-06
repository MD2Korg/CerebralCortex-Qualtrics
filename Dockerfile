FROM python:3-alpine
MAINTAINER Ryan Graves rgraves6@memphis.edu

WORKDIR /usr/arc/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements

COPY . .

CMD [ "python", "./qualtrics.py"]
