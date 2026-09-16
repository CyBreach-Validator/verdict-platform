\# CyBreach Validator Deployment Guide



\## 1. Purpose



This document explains how to set up, run, verify, and troubleshoot the CyBreach Validator platform.



The platform consists of:



\* FastAPI backend

\* React/Vite frontend dashboard

\* PostgreSQL database

\* Apache Kafka

\* Apache Zookeeper

\* Kong API Gateway

\* Verdict Publisher service

\* WebSocket-based live verdict updates



\---



\## 2. Project Location



The project root directory is:



```text

D:\\Validator Project\\verdict-platform

```



Main project folders:



```text

api-gateway

backend

contracts

docs

frontend-dashboard

verdict-publisher

```



\---



\## 3. System Requirements



The following software is required for local deployment:



\* Windows 10/11

\* Python 3.x

\* Node.js and npm

\* PostgreSQL

\* Docker Desktop

\* Git

\* A modern web browser such as Chrome or Microsoft Edge



Docker Desktop is used for Kafka, Zookeeper, and Kong.



\---



\## 4. Backend Deployment



\### 4.1 Navigate to the backend



From the project root:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\backend"

```



\### 4.2 Activate the Python virtual environment



```cmd

venv\\Scripts\\activate

```



The command prompt should show:



```text

(venv)

```



\### 4.3 Install backend dependencies



If dependencies have not already been installed:



```cmd

pip install -r requirements.txt

```



\### 4.4 Start the FastAPI backend



Run:



```cmd

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

```



The backend is available at:



```text

http://127.0.0.1:8000

```



Swagger API documentation:



```text

http://127.0.0.1:8000/docs

```



OpenAPI specification:



```text

http://127.0.0.1:8000/openapi.json

```



\---



\## 5. Backend Health Verification



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



If these endpoints respond correctly, the FastAPI backend is running.



\---



\## 6. PostgreSQL Database



The application uses PostgreSQL.



Database name:



```text

verdict\_db

```



The backend database configuration should point to the PostgreSQL instance configured for the project.



Before starting the backend, verify that PostgreSQL is running and that the configured database is available.



\---



\## 7. Database Migrations



The project uses Alembic for database migrations.



Navigate to:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\backend"

```



Activate the virtual environment:



```cmd

venv\\Scripts\\activate

```



Check the current migration revision:



```cmd

alembic current

```



Check migration history:



```cmd

alembic history

```



To upgrade the database to the latest migration:



```cmd

alembic upgrade head

```



The migration head should correspond to the latest migration in the project.



\---



\## 8. Kafka and Zookeeper



Kafka and Zookeeper are used for event-based verdict processing.



The local Docker deployment uses:



\* Kafka: port `9092`

\* Zookeeper: port `2181`



The Kafka topic used by the platform is:



```text

verdict-events

```



The verdict publisher consumer group is:



```text

verdict-publisher-group

```



\---



\## 9. Start Docker Services



Navigate to the project root:



```cmd

cd /d "D:\\Validator Project\\verdict-platform"

```



Start the Docker services:



```cmd

docker compose up -d

```



Check running containers:



```cmd

docker ps

```



The deployment should include the required services such as:



\* Kong

\* Kafka

\* Zookeeper



The exact container names may vary depending on the Docker Compose configuration.



\---



\## 10. Verify Kafka



List Kafka topics:



```cmd

docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list

```



The following topic should be present:



```text

verdict-events

```



If the container name differs, use the Kafka container name displayed by:



```cmd

docker ps

```



\---



\## 11. Kong API Gateway



Kong provides API gateway routing in front of the backend.



Local Kong proxy:



```text

http://127.0.0.1:8002

```



Kong administrative interface:



```text

http://127.0.0.1:8001

```



The Kong configuration is stored in:



```text

D:\\Validator Project\\verdict-platform\\api-gateway\\kong.yml

```



The Kong upstream forwards requests to the FastAPI backend on:



```text

http://127.0.0.1:8000

```



\---



\## 12. Verify Kong Routing



From CMD:



```cmd

curl http://127.0.0.1:8002/

```



Expected response:



```json

{

&#x20; "message": "Backend is working"

}

```



A successful response confirms that Kong can route traffic to the FastAPI backend.



\---



\## 13. Kong Rate Limiting



The gateway uses rate limiting.



The validated Kong configuration exposes rate-limit headers such as:



```text

X-RateLimit-Limit-Minute

X-RateLimit-Remaining-Minute

```



The gateway configuration used during validation included a limit of:



```text

50 requests per minute

```



Backend endpoint-specific rate limits may differ.



For example, the verdict list endpoint currently uses:



```text

5 requests per minute

```



The API reference should be consulted for endpoint-specific limits.



\---



\## 14. Frontend Deployment



The frontend is a Vite application.



Navigate to:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\frontend-dashboard"

```



Install dependencies:



```cmd

npm install

```



Start the development server:



```cmd

npm run dev

```



The frontend is normally available at:



```text

http://localhost:5173

```



or:



```text

http://127.0.0.1:5173

```



\---



\## 15. Frontend Production Build



To create a production build:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\frontend-dashboard"

```



Run:



```cmd

npm run build

```



A successful build generates the Vite `dist` directory.



The build should complete without TypeScript or Vite errors.



\---



\## 16. Frontend Backend Connection



The frontend API service is configured to communicate with:



```text

http://127.0.0.1:8000

```



The frontend uses the JWT access token stored in browser local storage for authenticated API requests.



The WebSocket endpoint is:



```text

ws://127.0.0.1:8000/ws/verdicts

```



The WebSocket connection provides live verdict updates to the dashboard.



\---



\## 17. CORS Configuration



The backend allows the frontend development and preview origins used by the project.



Configured origins include:



```text

http://localhost:5173

http://127.0.0.1:5173

http://localhost:5174

http://127.0.0.1:5174

http://localhost:4173

http://127.0.0.1:4173

```



If the frontend is moved to a different origin, the backend CORS configuration must be updated accordingly.



\---



\## 18. Verdict Publisher



The verdict publisher is located at:



```text

D:\\Validator Project\\verdict-platform\\verdict-publisher

```



Navigate to the directory:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\verdict-publisher"

```



Run the publisher:



```cmd

python publisher.py

```



If the project uses a different publisher entry point configured in the repository, use that entry point instead.



The publisher consumes events from:



```text

verdict-events

```



using the consumer group:



```text

verdict-publisher-group

```



\---



\## 19. Publisher Monitoring



The publisher monitoring script is:



```text

D:\\Validator Project\\verdict-platform\\verdict-publisher\\monitor.py

```



Run:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\verdict-publisher"

python monitor.py

```



A healthy result should report zero Kafka consumer lag, for example:



```text

Kafka Consumer Monitoring

Group: verdict-publisher-group

Topic: verdict-events



Total Lag: 0

Lag Alert: False

```



\---



\## 20. Complete Local Startup Order



For a complete local deployment, use the following order.



\### Step 1 — Start PostgreSQL



Verify that PostgreSQL is running and `verdict\_db` is available.



\### Step 2 — Start Docker services



From:



```cmd

cd /d "D:\\Validator Project\\verdict-platform"

```



run:



```cmd

docker compose up -d

```



Verify:



```cmd

docker ps

```



\### Step 3 — Start the backend



Open a new CMD window:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\backend"

venv\\Scripts\\activate

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

```



\### Step 4 — Start the verdict publisher



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



Open:



```text

http://localhost:5173

```



\---



\## 21. Deployment Verification Checklist



After startup, verify:



\* \[ ] PostgreSQL is running

\* \[ ] `verdict\_db` is available

\* \[ ] Docker Desktop is running

\* \[ ] Kafka container is running

\* \[ ] Zookeeper container is running

\* \[ ] Kong container is running

\* \[ ] Kafka topic `verdict-events` exists

\* \[ ] FastAPI backend starts successfully

\* \[ ] `/` returns the backend working message

\* \[ ] `/health` returns `{"status":"ok"}`

\* \[ ] Swagger documentation opens

\* \[ ] Frontend starts successfully

\* \[ ] Login page loads

\* \[ ] Authenticated API requests work

\* \[ ] Dashboard loads

\* \[ ] Verdict data is displayed

\* \[ ] WebSocket live updates connect

\* \[ ] Kong routes requests to the backend

\* \[ ] Publisher consumes verdict events

\* \[ ] Publisher monitoring reports healthy Kafka lag



\---



\## 22. Common Startup Problems



\### Backend connection refused



If the frontend displays:



```text

ERR\_CONNECTION\_REFUSED

```



verify that the backend is running on:



```text

http://127.0.0.1:8000

```



Start it with:



```cmd

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

```



\---



\### Kafka connection failure



If the backend or publisher reports a Kafka timeout, verify:



```cmd

docker ps

```



Make sure Kafka and Zookeeper are running.



Then inspect Kafka logs:



```cmd

docker logs kafka

```



Use the actual Kafka container name if it differs.



\---



\### Frontend cannot connect to backend



Verify the frontend API base URL points to:



```text

http://127.0.0.1:8000

```



Also verify that the backend CORS configuration includes the frontend origin.



\---



\### Database migration error



From the backend directory:



```cmd

cd /d "D:\\Validator Project\\verdict-platform\\backend"

venv\\Scripts\\activate

alembic current

```



Then:



```cmd

alembic upgrade head

```



\---



\### Kong routing failure



Verify Kong is running:



```cmd

docker ps

```



Then test:



```cmd

curl http://127.0.0.1:8002/

```



If routing fails, inspect the Kong configuration:



```text

D:\\Validator Project\\verdict-platform\\api-gateway\\kong.yml

```



and check Kong logs:



```cmd

docker logs kong

```



Use the actual container name if it differs.



\---



\## 23. Shutdown Procedure



Stop the frontend, backend, and publisher using:



```text

Ctrl + C

```



To stop Docker Compose services:



```cmd

cd /d "D:\\Validator Project\\verdict-platform"

docker compose down

```



\---



\## 24. Source Control



Before deployment or handoff, check repository status:



```cmd

cd /d "D:\\Validator Project\\verdict-platform"

git status

```



Review changes:



```cmd

git diff

```



After verifying the documentation and code changes:



```cmd

git add .

git commit -m "Week 12 - Complete deployment documentation"

git push origin main

```



Only commit changes that have been reviewed and tested.



\---



\## 25. Security Considerations



For production deployment:



\* Do not commit passwords, API keys, JWT secrets, or database credentials.

\* Use environment variables or a secure secrets manager.

\* Use HTTPS instead of plain HTTP.

\* Use secure WebSocket connections (`wss://`) where applicable.

\* Restrict CORS origins to trusted frontend domains.

\* Use production PostgreSQL credentials and access controls.

\* Secure Kong administrative endpoints.

\* Review rate limits before production use.

\* Keep Docker images and application dependencies updated.

\* Enable appropriate logging and monitoring.

\* Back up the PostgreSQL database regularly.



\---



\## 26. Production Deployment Notes



The configuration documented in this guide is primarily intended for local development and validation.



Before production deployment, review:



\* Database connection settings

\* JWT secret configuration

\* CORS origins

\* Kafka broker configuration

\* Kong routes and upstreams

\* TLS/HTTPS configuration

\* Rate limits

\* Logging

\* Monitoring

\* Database backups

\* Container resource limits

\* Environment-specific configuration



Production infrastructure should not rely on development settings such as FastAPI `--reload`.



\---



\## 27. Deployment Architecture



The local deployment flow is:



```text

User Browser

&#x20;    |

&#x20;    v

React/Vite Dashboard

&#x20;    |

&#x20;    v

Kong API Gateway

&#x20;    |

&#x20;    v

FastAPI Backend

&#x20;    |

&#x20;    +------> PostgreSQL

&#x20;    |

&#x20;    +------> Kafka

&#x20;                 |

&#x20;                 v

&#x20;         Verdict Publisher

&#x20;                 |

&#x20;                 v

&#x20;            Verdict Events

```



The dashboard also maintains a WebSocket connection with the FastAPI backend for live verdict updates.



\---



\## 28. Final Verification



A deployment is considered ready for handoff when:



1\. PostgreSQL is available.

2\. Docker services are running.

3\. Kafka and Zookeeper are healthy.

4\. Kong routes traffic to the backend.

5\. FastAPI starts successfully.

6\. `/health` returns a healthy response.

7\. Swagger documentation is accessible.

8\. Frontend builds successfully.

9\. Frontend can authenticate with the backend.

10\. Dashboard data loads correctly.

11\. WebSocket updates function.

12\. Verdict events can be processed.

13\. Publisher monitoring reports healthy consumer lag.

14\. Documentation is stored in the `docs` directory.



\---



\## 29. Related Documentation



Additional documentation is available in:



```text

D:\\Validator Project\\verdict-platform\\docs

```



API documentation:



```text

D:\\Validator Project\\verdict-platform\\docs\\API\_REFERENCE.md

```



Swagger:



```text

http://127.0.0.1:8000/docs

```



OpenAPI:



```text

http://127.0.0.1:8000/openapi.json

```



\---



\## 30. Document Status



Document:



```text

CyBreach Validator Deployment Guide

```



Week:



```text

Week 12

```



Purpose:



```text

Deployment, startup, verification, troubleshooting, and handoff reference

```
