\# CyBreach Validator API Reference



\## 1. Overview



The CyBreach Validator backend provides REST APIs using FastAPI.



\### Base URL



```text

http://127.0.0.1:8000

```



\### API Documentation



Interactive Swagger UI:



```text

http://127.0.0.1:8000/docs

```



OpenAPI specification:



```text

http://127.0.0.1:8000/openapi.json

```



The API is implemented under:



```text

backend/app/api/

```



The application registers the API modules directly in `backend/app/main.py`. No `/api` prefix is applied.



\---



\## 2. Authentication



The application uses JWT-based authentication.



\### Login



\*\*Endpoint\*\*



```http

POST /auth/login

```



\*\*Purpose\*\*



Authenticates a user and returns an access token.



\*\*Example request\*\*



```json

{

&#x20; "username": "admin",

&#x20; "password": "admin123"

}

```



\*\*Example response\*\*



```json

{

&#x20; "access\_token": "<jwt-token>",

&#x20; "token\_type": "bearer"

}

```



Protected endpoints require the token in the HTTP Authorization header:



```text

Authorization: Bearer <access\_token>

```



\---



\## 3. System Health



\### Root



```http

GET /

```



Returns a basic backend status message.



Example response:



```json

{

&#x20; "message": "Backend is working"

}

```



\### Health Check



```http

GET /health

```



Returns the backend health status.



Example response:



```json

{

&#x20; "status": "ok"

}

```



\---



\## 4. User API



Source:



```text

backend/app/api/users.py

```



\### Create User



```http

POST /users

```



Creates a new user.



\### List Users



```http

GET /users

```



Returns the available users.



\### Get User



```http

GET /users/{user\_id}

```



Returns a specific user by ID.



\---



\## 5. Authentication API



Source:



```text

backend/app/api/auth.py

```



\### Login



```http

POST /auth/login

```



Authenticates a user and returns a JWT access token.



\---



\## 6. Rule Management API



Source:



```text

backend/app/api/rules.py

```



Rules define the security checks used by the validator.



\### Create Rule



```http

POST /rules

```



Creates a new validation rule.



\### List Rules



```http

GET /rules

```



Returns the configured rules.



\### Search Rules



```http

GET /rules/search

```



Searches the configured rules.



\### Get Rule



```http

GET /rules/{rule\_id}

```



Returns a specific rule.



\### Update Rule



```http

PUT /rules/{rule\_id}

```



Updates an existing rule.



\### Submit Rule



```http

PUT /rules/{rule\_id}/submit

```



Submits a rule for approval.



\### Approve Rule



```http

PUT /rules/{rule\_id}/approve

```



Approves a pending rule.



\### Reject Rule



```http

PUT /rules/{rule\_id}/reject

```



Rejects a pending rule.



\### Delete Rule



```http

DELETE /rules/{rule\_id}

```



Deletes a rule.



\### Upload Rules



```http

POST /rules/upload

```



Uploads rule definitions for processing.



\### Validate Rule



```http

POST /rules/validate/{rule\_id}

```



Validates a rule definition.



\### Compare Rule



```http

GET /rules/{rule\_id}/compare

```



Returns comparison information for the specified rule.



\### Rule Workflow



The rule management workflow supports states such as:



```text

Draft

Pending

Approved

Rejected

```



The approval workflow is used to control which rules are approved for active validation.



\---



\## 7. Validator API



Source:



```text

backend/app/api/validator.py

```



\### Validate Evidence



```http

POST /validate

```



Processes evidence against configured validation rules and generates a verdict.



The general validation flow is:



```text

Evidence

&#x20;  ↓

Rule Evaluation

&#x20;  ↓

Verdict Generation

&#x20;  ↓

Verdict Storage

&#x20;  ↓

Audit Logging

&#x20;  ↓

Verdict Publication

```



\---



\## 8. Verdict API



Source:



```text

backend/app/api/verdicts.py

```



Verdicts represent the result of validating evidence against a rule.



\### List Verdicts



```http

GET /verdicts

```



Returns verdict records.



\### Get Verdict



```http

GET /verdicts/{verdict\_id}

```



Returns a specific verdict.



\### Export Verdicts as CSV



```http

GET /verdicts/export/csv

```



Exports verdict information in CSV format.



\### Export Verdicts as PDF



```http

GET /verdicts/export/pdf

```



Exports verdict information in PDF format.



\### Rule Verdict Timeline



```http

GET /verdicts/rule/{rule\_id}

```



Returns the verdict history associated with a rule.



\### Verdict Comparison



```http

GET /verdicts/{verdict\_id}/chain
```



Returns the causal chain associated with a verdict.



\### Verdict Correction



```http

PUT /verdicts/{verdict\_id}/correct

```



Updates/corrects a verdict using the supported verdict correction workflow.



\### Revalidate Verdict



```http

POST /verdicts/{verdict\_id}/revalidate

```



Revalidates an existing verdict.



Revalidation creates a new verdict while preserving the previous verdict for traceability. The previous verdict can be marked as superseded and linked to the replacement verdict.



\### Verdict States



The platform supports the following validation results:



```text

Detected

Missed

Partial

No Data

```



\### Verdict Scoring



| Verdict  | Score |

| -------- | ----: |

| Detected |     2 |

| Partial  |     1 |

| Missed   |     0 |

| No Data  |     0 |



\### Verdict Integrity



Verdict records contain a SHA-256 hash used to support integrity verification.



\---



\## 9. Dashboard API



Source:



```text

backend/app/api/dashboard.py

```



\### Dashboard Statistics



```http

GET /dashboard/stats

```



Returns aggregated dashboard statistics.



\### Coverage



```http

GET /dashboard/coverage

```



Returns coverage information used by the dashboard.



\### Revalidation Statistics



```http

GET /dashboard/revalidation

```



Returns revalidation and gap-closure information.



Dashboard revalidation information includes metrics such as:



```text

total\_revalidations

improved

gap\_closed

history

```



\---



\## 10. Connector API



Source:



```text

backend/app/api/connectors.py

```



The connector API provides SIEM connector information.



\### List Connectors



```http

GET /connectors

```



Returns configured connectors and their current status.



\### Get Connector



```http

GET /connectors/{connector\_id}

```



Returns a specific connector.



Example connector integrations used by the project include:



```text

Splunk

Microsoft Sentinel

QRadar

Elastic

```



Example connector states include:



```text

Healthy

Connecting

Disconnected

```



\---



\## 11. Audit Log API



Source:



```text

backend/app/api/audit\_logs.py

```



Audit logs provide traceability for important system operations.



\### List Audit Logs



```http

GET /audit-logs

```



Returns audit log records.



\### Verify Verdict Integrity



```http

GET /audit-logs/verify/{verdict\_id}

```



Verifies the stored verdict hash against a newly calculated hash.



\### Get Audit Log



```http

GET /audit-logs/{audit\_log\_id}

```



Returns a specific audit log record.



Audit information can include:



| Field                | Description                 |

| -------------------- | --------------------------- |

| `action`             | Action performed            |

| `verdict\_id`         | Related verdict             |

| `related\_verdict\_id` | Related/replacement verdict |

| `rule\_id`            | Related rule                |

| `rule\_name`          | Related rule name           |

| `old\_verdict`        | Previous verdict            |

| `new\_verdict`        | New verdict                 |

| `hash`               | Integrity information       |

| `details`            | Additional information      |



Example audit actions include:



```text

REVALIDATED

APPROVED

REJECTED

```



\---



\## 12. WebSocket API



Source:



```text

backend/app/api/websocket.py

```



The platform also provides a WebSocket endpoint for live verdict communication.



\### WebSocket Endpoint



```text

/ws/verdicts

```



Local WebSocket URL:



```text

ws://127.0.0.1:8000/ws/verdicts

```



The frontend dashboard uses this connection for real-time verdict updates.



The WebSocket implementation is also registered directly in:



```text

backend/app/main.py

```



The connection manager is implemented in:



```text

backend/app/websocket/connection\_manager.py

```



\---



\## 13. API Gateway



The project includes a Kong API Gateway.



Local gateway proxy:



```text

http://127.0.0.1:8002

```



Backend service:



```text

http://127.0.0.1:8000

```



The gateway is responsible for routing requests toward backend services and supporting gateway-level security controls.



Gateway validation includes:



\* API routing

\* Authentication enforcement

\* Rate limiting



\---



\## 14. Rate Limiting



The backend uses SlowAPI for request rate limiting.



The configured validation limit used during testing was:



```text

5 requests per minute

```



When the configured limit is exceeded, the API returns an HTTP `429 Too Many Requests` response.



Rate limiting helps protect the API against excessive request traffic.



\---



\## 15. CORS Configuration



The backend configures CORS for the local frontend development and preview environments.



Allowed origins include:



```text

http://localhost:5173

http://127.0.0.1:5173

http://localhost:5174

http://127.0.0.1:5174

http://localhost:4173

http://127.0.0.1:4173

```



The backend allows:



```text

Credentials: enabled

Methods: all

Headers: all

```



\---



\## 16. Common HTTP Status Codes



| Status Code | Meaning                            |

| ----------- | ---------------------------------- |

| `200`       | Request successful                 |

| `201`       | Resource created                   |

| `400`       | Bad request                        |

| `401`       | Authentication required or invalid |

| `403`       | Access forbidden                   |

| `404`       | Resource not found                 |

| `429`       | Rate limit exceeded                |

| `500`       | Internal server error              |



\---



\## 17. Security Controls



The API implements multiple security controls:



\* JWT authentication

\* Protected API endpoints

\* API Gateway authentication enforcement

\* Rate limiting

\* CORS configuration

\* Audit logging

\* Verdict hash verification

\* Verdict revalidation traceability



\---



\## 18. API Testing



The API can be tested using the FastAPI Swagger interface:



```text

http://127.0.0.1:8000/docs

```



The OpenAPI specification is available at:



```text

http://127.0.0.1:8000/openapi.json

```



The frontend dashboard can also be used to validate API integration.



For gateway testing, requests can be directed through:



```text

http://127.0.0.1:8002

```



\---



\## 19. End-to-End API Flow



The main application pipeline is:



```text

Evidence Event

&#x20;     ↓

Validator API

&#x20;     ↓

Rule Evaluation

&#x20;     ↓

Verdict Generation

&#x20;     ↓

PostgreSQL

&#x20;     ↓

Audit Logging

&#x20;     ↓

Kafka

&#x20;     ↓

Verdict Publisher

&#x20;     ↓

WebSocket / Dashboard

```



This flow represents the end-to-end validation pipeline of the CyBreach Validator platform.



\---



\## 20. API Source Files



The primary API implementation files are:



```text

backend/app/api/auth.py

backend/app/api/users.py

backend/app/api/rules.py

backend/app/api/verdicts.py

backend/app/api/dashboard.py

backend/app/api/connectors.py

backend/app/api/validator.py

backend/app/api/audit\_logs.py

backend/app/api/websocket.py

```



The main FastAPI application is:



```text

backend/app/main.py

```



The FastAPI Swagger/OpenAPI interface should be treated as the authoritative source for the complete request and response schemas exposed by the running application.
