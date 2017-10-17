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

# Program Arguments
parser = argparse.ArgumentParser()
parser.add_argument("dataCenter", help="Qualtrics Data Center")
parser.add_argument("apiToken", help="Qualtrics API Token")
parser.add_argument("surveyId", help="Qualtrics Survey ID")
parser.add_argument('-f', "--fileFormat", default = "json", help="Qualtrics Export File Format")
args = parser.parse_args()

# Setting user Parameters
dataCenter=''
apiToken=''
surveyId=''
fileFormat = args.fileFormat

# Setting static parameters
requestCheckProgress = 0
progressStatus = "in progress"
baseUrl = "https://{0}.qualtrics.com/API/v3/responseexports/".format(dataCenter)
headers = {
    "content-type": "application/json",
    "x-api-token": apiToken,
    "-o": "response.zip"
    }

# Step 1: Creating Data Export
downloadRequestUrl = baseUrl
downloadRequestPayload = '{"format":"' + fileFormat + '","surveyId":"' + surveyId + '"}'
downloadRequestResponse = requests.request("POST", downloadRequestUrl, data=downloadRequestPayload, headers=headers)
progressId = downloadRequestResponse.json()["result"]["id"]
print(downloadRequestResponse.text)

# Step 2: Checking on Data Export Progress and waiting until export is ready
while requestCheckProgress < 100 and progressStatus is not "complete":
    requestCheckUrl = baseUrl + progressId
    requestCheckResponse = requests.request("GET", requestCheckUrl, headers=headers)
    requestCheckProgress = requestCheckResponse.json()["result"]["percentComplete"]
    print("Download is " + str(requestCheckProgress) + " complete")

# Step 3: Downloading file
requestDownloadUrl = baseUrl + progressId + '/file'
requestDownload = requests.request("GET", requestDownloadUrl, headers=headers, stream=True)

# Step 4: Unzipping the file
#qfile = zipfile.ZipFile(io.BytesIO(requestDownload.content)).read("mPerf integration test.json")
qfile = zipfile.ZipFile(io.BytesIO(requestDownload.content))


# Reading the file
jsonResponse = json.loads(qfile.read(qfile.filelist[0].orig_filename).decode('utf-8'))
for child in jsonResponse['responses']:
    print (child['ResponseID'], child['participantID'], child['Q1'], child['Q2'], child['Q3'], child['Q4'], child['Q5'])

print('Complete')
