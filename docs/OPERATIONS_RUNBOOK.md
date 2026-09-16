\# CyBreach Validator Operations Runbook



\## 1. Purpose



This runbook provides operational procedures for starting, stopping, monitoring, troubleshooting, and validating the CyBreach Validator platform.



It is intended to provide a repeatable reference for development, testing, maintenance, and handoff activities.



\---



\## 2. Platform Components



The CyBreach Validator platform consists of:



\* FastAPI backend

\* React/Vite frontend dashboard

\* PostgreSQL database

\* Apache Kafka

\* Apache Zookeeper

\* Kong API Gateway

\* Verdict Publisher

\* WebSocket live verdict updates



Project root:



```text

D:\\Validator Project\\verdict-platform

```



\---



\## 3. Service Locations



\### Backend



```text

D:\\Validator Project\\verdict-platform\\backend

```



\### Frontend



```text

D:\\Validator Project\\verdict-platform\\frontend-dashboard

```



\### API Gateway



```text

D:\\Validator Project\\verdict-platform\\api-gateway

```



\### Verdict Publisher



```text

D:\\Validator Project\\verdict-platform\\verdict-publisher

```



\### Documentation



```text

D:\\Validator Project\\verdict-platform\\docs

```



\---



\## 4. Normal Startup Procedure



Use the following order for a normal local startup.



\### Step 1 — Start PostgreSQL



Verify that PostgreSQL is running and the application database is available.



Database:



```text

verdict\_db

```



\### Step 2 — Start Docker services



Open CMD and run:



```cmd

cd /d "D:\\Validator Project\\verdict-platform"

docker compose up -d

```



Verify:



```cmd

docker ps

```



Confirm that Kafka, Zookeeper, and Kong are running.



\### Step 3 — Start the backend



Open a new CMD window:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\backend"

venv\\Scripts\\activate

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

```



\### Step 4 — Start the Verdict Publisher



Open another CMD window:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\verdict-publisher"

python publisher.py

```



\### Step 5 — Start the frontend



Open another CMD window:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\frontend-dashboard"

npm run dev

```



\### Step 6 — Open the dashboard



Use:



```text

http://localhost:5173

```



\---



\## 5. Basic Health Checks



\### Backend root



Open:



```text

http://127.0.0.1:8000/

```



Expected response:



```json

{

&#x20; "message": "Backend is working"

}

```



\### Backend health



Open:



```text

http://127.0.0.1:8000/health

```



Expected response:



```json

{

&#x20; "status": "ok"

}

```



\### Swagger



Open:



```text

http://127.0.0.1:8000/docs

```



Swagger should load without an application startup error.



\---



\## 6. Docker Service Check



Run:



```cmd

docker ps

```



Check that the required containers are running.



For more information:



```cmd

docker ps -a

```



If a container has stopped, inspect its logs:



```cmd

docker logs <container-name>

```



\---



\## 7. Kafka Health Check



List Kafka topics:



```cmd

docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list

```



The application topic should include:



```text

verdict-events

```



If the Kafka container has a different name, identify it with:



```cmd

docker ps

```



and use the displayed Kafka container name.



\---



\## 8. Kafka Consumer Monitoring



The Verdict Publisher uses:



```text

Consumer Group:

verdict-publisher-group

```



Topic:



```text

verdict-events

```



Run the monitoring script:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\verdict-publisher"

python monitor.py

```



A healthy result should report:



```text

Total Lag: 0

Lag Alert: False

```



A non-zero lag indicates that the consumer has not processed all available Kafka events.



\---



\## 9. Consumer Lag Response



If Kafka consumer lag is detected:



1\. Run the publisher monitoring script.

2\. Confirm the Kafka container is running.

3\. Check Kafka logs.

4\. Check Verdict Publisher logs.

5\. Confirm the consumer group is active.

6\. Restart the publisher if necessary.

7\. Run the monitor again.

8\. Confirm the lag returns to the expected healthy state.



Check Docker status:



```cmd

docker ps

```



Check Kafka logs:



```cmd

docker logs kafka

```



Restart the publisher by stopping it with:



```text

Ctrl + C

```



and starting it again:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\verdict-publisher"

python publisher.py

```



Then monitor:



```cmd

python monitor.py

```



\---



\## 10. Kong Gateway Health Check



Kong proxy:



```text

http://127.0.0.1:8002

```



Test routing:



```cmd

curl http://127.0.0.1:8002/

```



Expected response:



```json

{

&#x20; "message": "Backend is working"

}

```



If this works, Kong is successfully forwarding the request to the backend.



\---



\## 11. Kong Rate-Limit Check



The gateway may return rate-limit headers including:



```text

X-RateLimit-Limit-Minute

X-RateLimit-Remaining-Minute

```



Check the response headers using:



```cmd

curl -i http://127.0.0.1:8002/

```



Review the rate-limit headers in the response.



The validated gateway configuration used a limit of:



```text

50 requests per minute

```



Endpoint-specific backend limits may be different.



\---



\## 12. Backend Rate Limiting



The backend uses SlowAPI.



For example, the verdict list endpoint is configured for:



```text

5 requests per minute

```



The endpoint is:



```text

GET /verdicts

```



When a rate limit is exceeded, the API may return an HTTP `429 Too Many Requests` response.



When investigating rate-limit behavior, check both:



\* Kong gateway limits

\* Backend endpoint limits



\---



\## 13. Database Health Check



Confirm PostgreSQL is running.



Confirm that the database exists:



```text

verdict\_db

```



If database connectivity errors appear in the backend, check:



1\. PostgreSQL service status.

2\. Database credentials.

3\. Database host and port.

4\. Database name.

5\. Backend environment configuration.

6\. Alembic migration status.



From the backend directory:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\backend"

venv\\Scripts\\activate

alembic current

```



Check migrations:



```cmd

alembic history

```



Apply pending migrations:



```cmd

alembic upgrade head

```



\---



\## 14. Backend Troubleshooting



\### Symptom: Backend does not start



Run:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\backend"

venv\\Scripts\\activate

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

```



Review the terminal output for:



\* Python import errors

\* Database connection errors

\* Kafka connection errors

\* Configuration errors

\* Missing dependencies



\---



\### Symptom: Port 8000 is unavailable



Check whether another process is using port 8000:



```cmd

netstat -ano | findstr :8000

```



If another application is using the port, identify the process before taking any corrective action.



\---



\### Symptom: Frontend shows connection refused



Verify that the backend is running:



```text

http://127.0.0.1:8000/health

```



Then verify the frontend API configuration points to:



```text

http://127.0.0.1:8000

```



\---



\## 15. Frontend Troubleshooting



Navigate to:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\frontend-dashboard"

```



Install dependencies if required:



```cmd

npm install

```



Start development mode:



```cmd

npm run dev

```



Build the application:



```cmd

npm run build

```



A successful production build should complete without TypeScript or Vite errors.



\---



\## 16. WebSocket Health Check



The dashboard uses:



```text

ws://127.0.0.1:8000/ws/verdicts

```



for live verdict updates.



If live updates are not appearing:



1\. Confirm the backend is running.

2\. Confirm the WebSocket endpoint is available.

3\. Open browser Developer Tools.

4\. Select the \*\*Network\*\* tab.

5\. Filter for \*\*WS\*\*.

6\. Check the `/ws/verdicts` connection.

7\. Review browser console errors.

8\. Confirm the frontend is using port `8000`, not an old backend port.



\---



\## 17. Authentication Troubleshooting



The authentication endpoint is:



```text

POST /auth/login

```



If login fails:



1\. Confirm the backend is running.

2\. Confirm the user exists.

3\. Verify the submitted credentials.

4\. Check the browser Network tab.

5\. Inspect the API response status.

6\. Confirm the JWT access token is returned after successful login.



The frontend stores the access token in:



```text

localStorage

```



under:



```text

access\_token

```



\---



\## 18. Rule Workflow Check



Rules can move through supported workflow states.



The operational workflow includes actions such as:



```text

Draft

&#x20; |

&#x20; v

Pending

&#x20; |

&#x20; +----> Approved

&#x20; |

&#x20; +----> Rejected

```



Relevant endpoints include:



```text

POST /rules

GET /rules

PUT /rules/{rule\_id}

PUT /rules/{rule\_id}/submit

PUT /rules/{rule\_id}/approve

PUT /rules/{rule\_id}/reject

DELETE /rules/{rule\_id}

```



When troubleshooting rule workflow problems, verify the current rule status before attempting the next workflow operation.



\---



\## 19. Verdict Troubleshooting



Important verdict endpoints include:



```text

GET /verdicts

GET /verdicts/{verdict\_id}

GET /verdicts/rule/{rule\_id}

PUT /verdicts/{verdict\_id}/correct

GET /verdicts/{verdict\_id}/chain

POST /verdicts/{verdict\_id}/revalidate

```



Supported verdict states include:



```text

Detected

Missed

Partial

No Data

```



If a verdict cannot be found, verify:



1\. The verdict ID.

2\. The associated rule.

3\. Database connectivity.

4\. Authentication status.

5\. API response status.



\---



\## 20. Verdict Revalidation



Revalidation can be initiated through:



```text

POST /verdicts/{verdict\_id}/revalidate

```



The revalidation workflow creates a new verdict and handles the superseding relationship with the previous verdict.



When troubleshooting:



1\. Verify the verdict exists.

2\. Verify the associated rule exists.

3\. Trigger revalidation.

4\. Check the new verdict.

5\. Verify the previous verdict's superseded state.

6\. Review the audit log.

7\. Check Kafka event processing if applicable.



\---



\## 21. Audit Log Verification



Audit logs provide an operational record of important actions.



Relevant endpoints include:



```text

GET /audit-logs

GET /audit-logs/{audit\_log\_id}

GET /audit-logs/verify/{verdict\_id}

```



When investigating a verdict correction or revalidation, review the corresponding audit log entries.



\---



\## 22. Dashboard Health Check



After login, verify that the dashboard displays:



\* Verdict data

\* Rule information

\* Coverage information

\* MITRE-related information

\* Connector status

\* Verdict timeline information

\* Revalidation functionality



Check browser Developer Tools if any dashboard component fails to load.



\---



\## 23. Connector Health



The dashboard displays connector status information.



The validated test seed included connector states such as:



```text

Healthy

Connecting

Disconnected

```



If connector information is missing:



1\. Check the backend.

2\. Check the connectors API.

3\. Review browser Network requests.

4\. Confirm the API returns connector data.

5\. Refresh the dashboard.



\---



\## 24. Export Troubleshooting



The platform provides:



```text

GET /verdicts/export/csv

GET /verdicts/export/pdf

```



If CSV or PDF export fails:



1\. Confirm the backend is running.

2\. Confirm authenticated access.

3\. Verify verdict records exist.

4\. Check the backend terminal for errors.

5\. Retry the export.

6\. Confirm the downloaded file opens correctly.



\---



\## 25. Logging



When investigating an incident, collect information from:



\### Backend



The terminal running Uvicorn.



\### Frontend



Browser Developer Tools:



\* Console

\* Network

\* WebSocket



\### Kafka



```cmd

docker logs kafka

```



\### Kong



```cmd

docker logs kong

```



\### Zookeeper



```cmd

docker logs zookeeper

```



Use the actual container names displayed by:



```cmd

docker ps

```



\---



\## 26. Incident Investigation Procedure



When a failure is reported:



\### Step 1 — Identify the affected component



Determine whether the issue is related to:



\* Frontend

\* Backend

\* Database

\* Kafka

\* Verdict Publisher

\* Kong

\* WebSocket



\### Step 2 — Check service availability



Run:



```cmd

docker ps

```



and verify the backend health endpoint.



\### Step 3 — Check logs



Review the relevant service logs.



\### Step 4 — Reproduce the problem



Use the affected UI operation or API endpoint.



\### Step 5 — Record the error



Capture:



\* Timestamp

\* Endpoint

\* HTTP status

\* Error message

\* Relevant service logs



\### Step 6 — Apply the smallest corrective action



Restart only the affected development service when practical.



\### Step 7 — Re-test



Repeat the failed operation.



\### Step 8 — Verify related components



Confirm that the corrective action did not affect other platform services.



\---



\## 27. Normal Shutdown Procedure



Stop the frontend, backend, and publisher with:



```text

Ctrl + C

```



Stop Docker services:



```cmd

cd /d "D:\\Validator Project\\verdict-platform"

docker compose down

```



Confirm containers have stopped:



```cmd

docker ps

```



\---



\## 28. Restart Procedure



For a complete restart:



```cmd

cd /d "D:\\Validator Project\\verdict-platform"

docker compose down

docker compose up -d

```



Then start the backend:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\backend"

venv\\Scripts\\activate

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

```



Start the publisher:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\verdict-publisher"

python publisher.py

```



Start the frontend:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\frontend-dashboard"

npm run dev

```



\---



\## 29. Database Backup Considerations



Before destructive database operations:



\* Confirm that a current backup exists.

\* Do not delete production data without authorization.

\* Verify the target database before running administrative commands.

\* Test restoration procedures periodically in a controlled environment.



Database backup and restoration procedures should be adapted to the organization's PostgreSQL infrastructure.



\---



\## 30. Documentation Maintenance



Update the documentation when any of the following change:



\* API routes

\* Authentication behavior

\* Database schema

\* Kafka topics

\* Consumer groups

\* Kong routes

\* Rate limits

\* Frontend API URLs

\* WebSocket endpoints

\* Deployment commands

\* Environment variables

\* Operational procedures



Relevant documentation files:



```text

docs\\API\_REFERENCE.md

docs\\DEPLOYMENT\_GUIDE.md

docs\\OPERATIONS\_RUNBOOK.md

```



\---



\## 31. Operational Checklist



\### Startup



\* \[ ] PostgreSQL running

\* \[ ] Docker Desktop running

\* \[ ] Kafka running

\* \[ ] Zookeeper running

\* \[ ] Kong running

\* \[ ] Backend running

\* \[ ] Verdict Publisher running

\* \[ ] Frontend running



\### Health



\* \[ ] Backend `/` responds

\* \[ ] Backend `/health` responds

\* \[ ] Swagger loads

\* \[ ] Kong routes correctly

\* \[ ] Kafka topic exists

\* \[ ] Consumer lag is healthy

\* \[ ] Dashboard loads

\* \[ ] Login works

\* \[ ] WebSocket connects



\### Functional



\* \[ ] Rules can be viewed

\* \[ ] Rules can be managed according to workflow

\* \[ ] Verdicts can be viewed

\* \[ ] Verdict correction works

\* \[ ] Verdict causal chain loads

\* \[ ] Verdict revalidation works

\* \[ ] Audit records are available

\* \[ ] CSV export works

\* \[ ] PDF export works



\---



\## 32. Handoff Verification



Before handing over the environment, verify:



1\. Source code is available.

2\. Documentation is present under `docs`.

3\. API reference matches the backend routes.

4\. Deployment instructions have been tested.

5\. Operational procedures are documented.

6\. Backend health checks pass.

7\. Frontend build passes.

8\. Kafka services are operational.

9\. Kong routing works.

10\. Verdict Publisher monitoring is available.

11\. WebSocket functionality has been tested.

12\. Known troubleshooting procedures are documented.



\---



\## 33. Document Status



Document:



```text

CyBreach Validator Operations Runbook

```



Week:



```text

Week 12

```



Purpose:



```text

Operational startup, monitoring, troubleshooting, recovery, and handoff reference

```



Status:



```text

Prepared for Week 12 documentation handoff

```
