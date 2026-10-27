# Cross-Account Access Grant Display
## Test Cases and Results

### 1. Introduction

This document records the functional tests performed on the Cross-Account Access Grant Display prototype. The tests cover MQTT request processing, AWS Lambda execution, S3 result storage, error-handling behavior, and dashboard functionality.

### 2. Test Environment

| Component | Configuration |
|---|---|
| Cloud Platform | Amazon Web Services (AWS) |
| AWS Region | us-east-1 |
| Messaging Service | AWS IoT Core MQTT |
| Processing Service | AWS Lambda |
| Storage Service | Amazon S3 |
| Dashboard | Python Streamlit |
| Data Format | JSON |
| Dashboard Refresh Interval | 30 seconds |

### 3. Functional Test Cases

| Test ID | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-01 | Publish a valid MQTT request | Lambda processes the request and generates a result | Request processing completed successfully | PASS |
| TC-02 | Submit requests with different request IDs | Each request is processed with its corresponding ID | Different request IDs were processed successfully | PASS |
| TC-03 | Submit a request without a request ID | The application generates a fallback request ID | A fallback ID was generated and the request was processed | PASS |
| TC-04 | Submit an empty JSON object `{}` | The application handles missing fields using its configured defaults | The request was processed using a fallback ID | PASS — Observed behavior |
| TC-05 | Submit malformed JSON | Invalid input should be rejected or handled without producing a valid request result | No new Lambda execution was observed; the exact rejection point was not confirmed | INCONCLUSIVE |
| TC-06 | Test S3 access-denied handling | The application displays or records an appropriate error | Error-handling code was inspected, but an actual access-denied condition was not tested | NOT EXECUTED |
| TC-07 | Verify automatic dashboard refresh | The dashboard reruns at approximately 30-second intervals | Automatic refresh was verified | PASS |
| TC-08 | Process multiple requests | Multiple request results can be stored and displayed | Multiple requests were processed successfully | PASS |
| TC-09 | Perform final end-to-end validation | A request is processed, stored, and displayed in the dashboard | Request `FINAL-TEST-001` with message `Final end-to-end validation` was verified successfully | PASS |

### 4. End-to-End Test

**Test Request ID:** `FINAL-TEST-001`

**Input message:** `Final end-to-end validation`

The final validation checked the request-processing workflow, JSON result storage in Amazon S3, and visibility of the resulting data in the Streamlit dashboard.

**Observed outcome:** The user confirmed that the final end-to-end test worked across MQTT, S3, and the dashboard.

### 5. Dashboard Validation

The dashboard was verified for the following features:

- Displaying request summary metrics.
- Showing request history.
- Inspecting individual request details.
- Displaying request and S3 status information.
- Exporting request history as a CSV file.
- Automatically refreshing every 30 seconds.

### 6. Test Summary

| Status | Count |
|---|---:|
| Passed | 7 |
| Inconclusive | 1 |
| Not Executed | 1 |
| Total Test Cases | 9 |

The seven passed tests are TC-01, TC-02, TC-03, TC-04, TC-07, TC-08, and TC-09. TC-04 is marked as passed for the observed fallback behavior; it does not establish that every missing-field scenario is handled correctly.

### 7. Known Limitations

1. Malformed JSON rejection was observed indirectly, but the exact component responsible for rejecting the request was not established.
2. S3 access-denied behavior was reviewed in code but not verified through a live denial test.
3. Successful cross-account role assumption into the intended target AWS account has not been verified.
4. The prototype's current AWS identity and S3 access checks should not be interpreted as proof of complete cross-account authorization.

### 8. Conclusion

The performed tests demonstrate that the prototype supports MQTT request processing, Lambda-based processing, S3 JSON result storage, and dashboard monitoring with automatic refresh. The recorded limitations identify the functionality that requires additional verification before the system can be considered a complete cross-account authorization solution.