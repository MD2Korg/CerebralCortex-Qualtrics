# Copyright (c) 2017, MD2K Center of Excellence
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import requests
import zipfile
import json
import io
import csv

# Program Arguments
parser = argparse.ArgumentParser()
parser.add_argument("dataCenter", help="Qualtrics Data Center")
parser.add_argument("apiToken", help="Qualtrics API Token")
parser.add_argument("surveyId", help="Qualtrics Survey ID")
parser.add_argument('-f', "--fileFormat", default = "json", help="Qualtrics Export File Format")
args = parser.parse_args()

# Setting user Parameters
dataCenter = args.dataCenter
apiToken = args.apiToken
surveyId = args.surveyId
fileFormat = args.fileFormat

headers = {"content-type": "application/" + fileFormat, "x-api-token": apiToken,
#    "-o": "response.zip"
}

questionnaireUrl = "https://{}.qualtrics.com/API/v3/surveys/{}".format(dataCenter, surveyId)
questionnaireResponse = requests.request("GET", questionnaireUrl, headers=headers)
exportFileName = questionnaireResponse.json()['result']['name']

# Downloading export
downloadRequestUrl = "https://{0}.qualtrics.com/API/v3/responseexports/".format(dataCenter)
downloadRequestPayload = '{"format":"' + fileFormat + '","surveyId":"' + surveyId + '"}'
downloadRequestResponse = requests.request("POST", downloadRequestUrl, data=downloadRequestPayload, headers=headers)
token = downloadRequestResponse.json()["result"]["id"]
requestDownloadUrl = downloadRequestUrl + token + '/file'
requestDownload = requests.request("GET", requestDownloadUrl, headers=headers, stream=True)
zipfile.ZipFile(io.BytesIO(requestDownload.content)).extractall("data")
with open("data/" + exportFileName + "." + fileFormat) as f:
    creader = csv.reader(f)
    for row in creader:
        print(row)

#qfile = zipfile.ZipFile(io.BytesIO(requestDownload.content))
#jsonResponse = json.loads(qfile.read(qfile.filelist[0].orig_filename).decode('utf-8'))
#qfile.close()
#for child in jsonResponse['responses']:
#    print (child['ResponseID'], child['participantID'], child['Q1'], child['Q2'], child['Q3'], child['Q4'], child['Q5'])
