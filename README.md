# MD2K Cerebral Cortex - Qualtric Integration
## usage:
```docker build -t qualtrics . && docker run qualtrics:latest $data_center $api_token $survey_id```

or

```python3 qualtrics.py $data_center $api_token $survey_id```

## cURL API Tests
**Required Vars**:

```data_center="" && api_token="" && survey_id=""```

###### Managing Surveys - [Qualtrics Doc](https://api.qualtrics.com/docs/managing-surveys)
**Get Survey** - individual survey's design, does not include details about how people answered questions

```curl -H "X-API-TOKEN: ${api_token}" "https://${data_center}.qualtrics.com/API/v3/surveys/${survey_id}"```

**Get Survey Responses Export** (Part 1) - POST for ID used in asynchronous export request. ID only valid for one week.

```curl -X POST -H "X-API-TOKEN: ${api_token}" -H 'Content-Type: application/json' -d '{ "surveyId": "${survey_id}", "format": "json" }' "https://${data_center}.qualtrics.com/API/v3/responseexports"```

**Get Survey Responses Export** (Part 2) -

```curl -H "X-API-TOKEN: ${api_token}" "https://${data_center}.qualtrics.com/API/v3/responseexports/${export_id}/file"```

###### Get Organization - [Qualtrics Doc](https://api.qualtrics.com/docs/get-brand-info)

```curl -H "X-API-TOKEN: ${api_token}" "https://${data_center}.qualtrics.com/API/v3/organizations/exampleorganization"```
>**error** - "httpStatus":"401 - Unauthorized","error":{"errorMessage":"Insufficient permissions."
