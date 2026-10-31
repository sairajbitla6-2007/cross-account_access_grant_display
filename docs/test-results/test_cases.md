# Cross-Account Access Grant Display

## Final Test Cases and Results

### 1. Introduction

This document records the functional testing performed on the Cross-Account Access Grant Display prototype. Testing covers MQTT request processing, AWS Lambda execution, request validation, Amazon S3 result storage, dashboard functionality, CSV export, and end-to-end workflow verification.

The test results reflect the behavior observed during the testing sessions. Tests that were not performed or remain inconclusive are explicitly identified.

### 2. Test Environment

| Component                  | Configuration             |
| -------------------------- | ------------------------- |
| Cloud Platform             | Amazon Web Services (AWS) |
| AWS Region                 | us-east-1                 |
| Messaging Service          | AWS IoT Core MQTT         |
| Processing Service         | AWS Lambda                |
| Storage Service            | Amazon S3                 |
| Dashboard                  | Python Streamlit          |
| Data Format                | JSON                      |
| Dashboard Refresh Interval | 30 seconds                |
| Result Storage Prefix      | `access-results/`         |

### 3. Functional Test Cases

| Test ID | Test Scenario                                            | Expected Result                                                                      | Actual Result                                                                                                                                                | Status                                                                       |
| ------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| TC-01   | Publish a valid MQTT request                             | Lambda processes the request and generates a result                                  | Valid request processing was verified successfully                                                                                                           | PASS                                                                         |
| TC-02   | Submit requests with different request IDs               | Each request is processed with its corresponding ID                                  | Requests with different IDs were processed successfully                                                                                                      | PASS                                                                         |
| TC-03   | Submit a request without a request ID                    | The request is rejected by application validation, with a failure result recorded    | The request was rejected; the request ID remained null, S3 access was not tested, and the failure result was stored successfully                             | PASS                                                                         |
| TC-04   | Submit an empty JSON object `{}`                         | The request is rejected if the required request ID is absent                         | Published `{}` to `crossaccount/request`; Lambda returned `requestId: null`, `status: FAILURE`, `s3Access: NOT_TESTED`, the expected validation message, and `storageStatus: SUCCESS`. The failure report was saved under a unique invalid-request S3 key. | PASS |
| TC-05   | Submit malformed JSON                                    | Invalid input should be rejected or handled without producing a valid request result | Two malformed JSON publishes produced no observed Lambda invocation or MQTT response. AWS IoT logging was disabled; `ParseError` was not available in the inspected CloudWatch Rule Metrics view. `TopicMatch` was listed, but its time-series value was not inspected. The observations are consistent with rejection before Lambda, but do not prove that the IoT Rules Engine rejected the payload or identify the precise rejection point. | INCONCLUSIVE |
| TC-06   | Test S3 access-denied handling                           | The application displays or records an appropriate error                             | Error-handling code was inspected, but an actual access-denied condition was not tested                                                                      | NOT EXECUTED                                                                 |
| TC-07   | Verify automatic dashboard refresh                       | The dashboard updates at approximately 30-second intervals                           | A newly submitted request appeared without manually refreshing the dashboard                                                                                 | PASS                                                                         |
| TC-08   | Process multiple requests                                | Multiple request results can be stored and displayed                                 | Multiple valid requests were processed successfully and appeared in the dashboard                                                                            | PASS                                                                         |
| TC-09   | Perform end-to-end validation                            | A request is processed, stored, and displayed in the dashboard                       | MQTT response, S3 result storage, and dashboard display were verified successfully                                                                           | PASS                                                                         |
| TC-10   | Submit a request with a missing request ID               | Validation returns a failure result without performing the S3 access check           | The request was rejected; `s3Access` was `NOT_TESTED` and `storageStatus` was `SUCCESS`                                                                      | PASS                                                                         |
| TC-11   | Submit a request with an empty request ID                | An empty request ID is rejected                                                      | The request was rejected with a failure result, and the result was stored successfully                                                                       | PASS                                                                         |
| TC-12   | Submit a numeric request ID                              | A numeric request ID is rejected because the ID must be a non-empty string           | The request was rejected with a failure result, and the result was stored successfully                                                                       | PASS                                                                         |
| TC-13   | Verify independent processing of multiple valid requests | Each valid request is processed and associated with its own ID                       | Two valid requests were processed and verified in the dashboard                                                                                              | PASS                                                                         |
| TC-14   | Verify dashboard auto-refresh using a new request        | The new request appears without manual browser refresh                               | Automatic appearance of the new request was verified                                                                                                         | PASS                                                                         |
| TC-15   | Export request history to CSV                            | The dashboard generates a downloadable CSV containing request data                   | CSV export succeeded, and the downloaded data was inspected                                                                                                  | PASS                                                                         |
| TC-16   | Inspect historical request details                       | Individual successful and failed requests display their relevant details             | Both successful and failed request details were verified in the dashboard                                                                                    | PASS                                                                         |
| TC-17   | Perform final end-to-end verification                    | The MQTT, Lambda, S3, and dashboard workflow operates as expected                    | The user confirmed that the MQTT response, S3 result, and dashboard record matched                                                                           | PASS                                                                         |
| TC-18   | Repeated request ID / duplicate-ID storage               | Two requests with the same request ID were processed                                  | Unique S3 object keys preserved both results; MQTT responses and both dashboard records were confirmed                                                        | PASS                                                                         |

**Test execution note:** TC-04 was retested with an empty JSON object and passed. The additional validation tests were confirmed by the user during the final validation session.

### 4. Final End-to-End Validation

The final end-to-end test verified the main workflow:

1. A JSON request was published to the AWS IoT Core MQTT request topic.
2. The IoT rule triggered the Lambda processing workflow.
3. Lambda validated and processed the request.
4. The processing result was saved as a JSON object in Amazon S3.
5. The MQTT response was received.
6. The Streamlit dashboard displayed the corresponding result.

**Request topic:** `crossaccount/request`

**Response topic:** `crossaccount/response`

**S3 result prefix:** `access-results/`

**Observed outcome:** The final validation succeeded across MQTT, S3, and the deployed dashboard.

The final end-to-end test establishes that the configured workflow operates successfully for the tested request. It does not establish that cross-account role assumption into a separate target AWS account is working.

### 5. Request Validation and Error Handling

The updated Lambda validation behavior was tested with the following invalid request-ID scenarios:

| Input Scenario                     | Expected Application Behavior | Observed Result |
| ---------------------------------- | ----------------------------- | --------------- |
| `requestId` omitted                | Reject request                | FAILURE         |
| `requestId` set to `null`          | Reject request                | FAILURE         |
| `requestId` set to an empty string | Reject request                | FAILURE         |
| `requestId` set to a numeric value | Reject request                | FAILURE         |

For invalid request IDs, the expected result is:

* `status`: `FAILURE`
* `s3Access`: `NOT_TESTED`
* `storageStatus`: `SUCCESS` when the failure report is successfully saved
* `processingMessage`: An explanation of the request validation failure

**Important distinction:** `storageStatus: SUCCESS` means the failure report was saved successfully. It does not mean the original request succeeded.

A missing request ID should remain null in the stored result. The dashboard may display this as `Missing` when the deployed dashboard includes the corresponding display change.

### 6. Duplicate Request ID Verification (TC-18)

The test used the same logical `requestId` for two separate MQTT requests, with different message values. The Lambda function generated a unique storage identifier for each result while retaining the original request ID in the result data.

Expected and verified behavior:
1. Both requests were processed.
2. Both MQTT responses were received.
3. Each result was stored as a separate JSON object under `access-results/`.
4. The two results retained the same logical request ID but had different S3 storage keys.
5. Both records appeared separately in the Streamlit dashboard.

This test confirms that repeated request IDs no longer cause earlier S3 results to be overwritten in the tested workflow.


### 7. Dashboard Validation

The following dashboard features were verified:

* Displaying request summary information and metrics.
* Showing request history.
* Inspecting individual successful and failed request details.
* Displaying request IDs and processing statuses.
* Showing S3 access and result-storage statuses.
* Displaying processing messages.
* Exporting request history as a CSV file.
* Automatically refreshing approximately every 30 seconds.
* Displaying newly processed requests without requiring manual browser refresh.

The dashboard reads stored results from Amazon S3. Its displayed data therefore depends on successful result storage, valid AWS credentials, and access to the configured S3 bucket.

### 8. Test Summary

The previously recorded nine-test summary is no longer sufficient because additional validation tests have been performed.

| Category                                                                  | Count |
| ------------------------------------------------------------------------- | ----: |
| Confirmed PASS: TC-01 through TC-04 and TC-07 through TC-18               |    16 |
| INCONCLUSIVE: TC-05                                                       |     1 |
| NOT EXECUTED: TC-06                                                       |     1 |
| **Total test cases**                                                      | **18** |

TC-05 did not produce an observed Lambda invocation or MQTT response, but the available evidence does not prove which AWS IoT component rejected or dropped the malformed payload. TC-06 did not include a live S3 access-denied scenario.

The duplicate request ID test (TC-18) was confirmed by checking MQTT responses, separate S3 objects, and separate dashboard records. TC-04 was retested with an empty JSON object and passed.

TC-04 was retested with an empty JSON object and passed: Lambda returned the expected validation failure and the failure report was successfully stored in S3. The duplicate request ID test (TC-18) was confirmed by checking MQTT responses, separate S3 objects, and separate dashboard records.

### 9. Known Limitations

1. **Malformed JSON handling:** The exact component responsible for rejecting malformed JSON has not been confirmed.
2. **S3 access-denied handling:** Error-handling code was inspected, but a live access-denied test has not been performed.
3. **Cross-account authorization:** Successful assumption of a role in the intended target AWS account has not been verified.
4. **AWS Academy restrictions:** IAM limitations restrict the ability to configure and validate the intended cross-account role arrangement.
5. **Temporary AWS credentials:** The deployed dashboard uses temporary AWS credentials for the demonstration. These credentials expire and must be refreshed according to the applicable AWS Academy workflow.
6. **Authorization scope:** Successful STS identity checks and S3 access checks do not independently prove that the intended cross-account authorization flow is configured correctly.

### 10. Conclusion

The testing demonstrates that the prototype supports valid MQTT request processing, Lambda-based validation, JSON result storage in Amazon S3, dashboard monitoring, automatic refresh, CSV export, and inspection of historical request details.

The updated validation logic rejects the tested invalid request-ID scenarios and records failure results without incorrectly reporting the requests as successful.

The implementation demonstrates an operational cloud-based monitoring workflow. However, successful cross-account role assumption remains unverified, and additional testing is required for malformed JSON rejection and live S3 access-denied handling.

The prototype should therefore be described as an access-monitoring and request-processing prototype, not as a fully verified cross-account authorization system.

These limitations should be addressed before the prototype is presented as a fully verified cross-account authorization solution.
