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
import os

# Program Arguments
#MAKE NAMED OPTIONS AND THEN REQUIRED.
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dataCenter", help="Qualtrics Data Center", required=True)
parser.add_argument("-a", "--apiToken", help="Qualtrics API Token", required=True)
parser.add_argument("-s", "--surveyId", help="Qualtrics Survey ID", required=True)
parser.add_argument('-f', "--fileFormat", default = "json", help="Qualtrics Export File Format")
parser.add_argument('-p', "--payloadPath", default = str(os.path.dirname(os.path.realpath(__file__)) + "/data/"), help="Qualtrics Output Directory")
args = parser.parse_args()

# Setting user Parameters
dataCenter = args.dataCenter
apiToken = args.apiToken
surveyId = args.surveyId
fileFormat = args.fileFormat
payloadPath = args.payloadPath

# Setting static parameters
#questions = ["Q1", "Q2", "Q3", "Q4", "Q5", "QID188"]
requestCheckProgress = 0
progressStatus = "in progress"
baseUrl = "https://{0}.qualtrics.com/API/v3/responseexports/".format(dataCenter)
headers = {
    "content-type": "application/json",
    "x-api-token": apiToken,
#    "includedQuestionIds": json.dumps(questions),
#    "useLabels": 'True',
    }

# Step 1: Creating Data Export
downloadRequestUrl = baseUrl
downloadRequestPayload = '{"format":"' + fileFormat + '","surveyId":"' + surveyId + '"}'
downloadRequestResponse = requests.request("POST", downloadRequestUrl, data=downloadRequestPayload, headers=headers)
token = downloadRequestResponse.json()["result"]["id"]
print(downloadRequestResponse.text)

# Step 2: Checking on Data Export Progress and waiting until export is ready
while requestCheckProgress < 100 and progressStatus is not "complete":
    requestCheckUrl = baseUrl + token
    requestCheckResponse = requests.request("GET", requestCheckUrl, headers=headers)
    requestCheckProgress = requestCheckResponse.json()["result"]["percentComplete"]
    print("Download is " + str(requestCheckProgress) + " complete")

# Step 3: Downloading file
requestDownloadUrl = baseUrl + token + '/file'
requestDownload = requests.request("GET", requestDownloadUrl, headers=headers, stream=True)

# Step 4: Unzipping the file
zipfile.ZipFile(io.BytesIO(requestDownload.content)).extractall(payloadPath)

questionsUrl = "https://{}.qualtrics.com/API/v3/surveys/{}".format(dataCenter, surveyId)
questionsResponse = requests.request("GET", questionsUrl, headers={"content-type": "application/" + fileFormat, "x-api-token": apiToken,})
surveyFileName = payloadPath + questionsResponse.json()['result']['name'] + "." + fileFormat
# Should I use a buffered reader?
with open(surveyFileName) as jreader:
    surveyData = json.load(jreader)

# Test 1
for child in json.loads(questionsResponse.text)['result']['questions']:
    questionName = json.loads(questionsResponse.text)['result']['questions'][str(child)]['questionName']
    questionText = json.loads(questionsResponse.text)['result']['questions'][str(child)]['questionText']
    print(questionName)
    for child in surveyData['responses']:
        for key, value in child.items():
            if key == questionName:
                print(child['ResponseID'], questionText + ": " + value)

# Test 2
questionDict = {}
for child in json.loads(questionsResponse.text)['result']['questions']:
    questionName = json.loads(questionsResponse.text)['result']['questions'][str(child)]['questionName']
    questionText = json.loads(questionsResponse.text)['result']['questions'][str(child)]['questionText']
    questionDict[questionName] = questionText
for child in surveyData['responses']:
    userData = {}
    userData['ResponseID'] = child['ResponseID']
#    userData['PID'] = child['PID']
    for key, value in child.items():
        if key in questionDict:
            userData[questionDict[key]] = value
    with open (payloadPath + "/" + userData['ResponseID'] + "-" + surveyId + "." + fileFormat, 'w', encoding='utf-8') as jwriter:
        json.dump(userData, jwriter)


print('Complete')