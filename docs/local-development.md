# JiraPilot AI - Local Development & Developer Onboarding Guide
**Fictional Organization:** Northstar Digital Systems (`northstar-labs`)  
**Product:** JiraPilot AI

---

## 1. Prerequisites

Ensure the following runtimes are installed on your machine:

* **Java Development Kit (JDK):** Version 21 (Temurin / OpenJDK)
* **Build Tool:** Apache Maven 3.9+
* **Python:** Version 3.12+ with `pip`
* **Node.js:** Version 18+ or 20+ with `npm`
* **Git:** Version 2.30+

---

## 2. Directory Structure

```text
RUNTIME_Terrors/
├── ai-service/             # Python 3.12 FastAPI microservice (Port 8000)
│   ├── app/                # Main application package
│   ├── tests/              # Pytest test suite
│   └── requirements.txt    # Python dependencies
├── backend/                # Java 21 Spring Boot 3 microservice (Port 8080)
│   ├── src/                # Spring Boot source code
│   └── pom.xml             # Maven dependencies
├── frontend/               # React 18 / TypeScript / Vite application (Port 3000)
│   ├── src/                # UI components and pages
│   └── package.json        # NPM dependencies
├── demo-data/              # Synthetic fixtures & sample application logs
│   ├── service-catalog.json# 12 Northstar services across 4 groups
│   ├── incidents.json      # 22 rich synthetic incident records (NOVA-101 .. NOVA-122)
│   └── logs/               # Raw log samples (JSON, Spring stack traces)
├── docs/                   # Architecture, API contracts, data dictionary
├── schemas/                # Shared JSON Schema validation contracts
└── scripts/                # Development, generator, and compliance utilities
```

---

## 3. Quick Start: Running the Full Stack Locally

### Step 1: Start Python AI Service (Port 8000)
```powershell
cd ai-service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Health check:* [http://localhost:8000/health](http://localhost:8000/health)  
*Swagger Docs:* [http://localhost:8000/docs](http://localhost:8000/docs)

### Step 2: Start Java Spring Boot Backend (Port 8080)
```powershell
cd backend
mvn clean spring-boot:run
```
*Health check:* [http://localhost:8080/actuator/health](http://localhost:8080/actuator/health)  
*Tickets API:* [http://localhost:8080/api/tickets](http://localhost:8080/api/tickets)

### Step 3: Start React Vite Frontend (Port 3000)
```powershell
cd frontend
npm install
npm run dev -- --port 3000
```
*Open Console:* [http://localhost:3000](http://localhost:3000)

---

## 4. Running Tests & Quality Verification

### 4.1 Python Test Suite
```powershell
cd ai-service
pytest tests/ -v
```

### 4.2 Java Backend Test Suite
```powershell
cd backend
mvn test
```

### 4.3 Validate Synthetic Data Fixtures
Ensure all JSON fixtures conform to the formal JSON Schema definitions:
```powershell
python scripts/validate_fixtures.py
```

### 4.4 Generate Additional Synthetic Incidents
Regenerate or expand the synthetic dataset reproducibly:
```powershell
python scripts/generate_synthetic_incidents.py
```

### 4.5 Confidentiality & Secret Scanner
Run the pre-commit compliance scanner across the entire codebase:
```powershell
python scripts/scan_secrets_and_compliance.py
```

---

## 5. Dockerized Deployment (Optional)

You can launch the entire stack using Docker Compose:
```powershell
docker-compose up --build -d
```
All services will initialize with isolated networking and synthetic sample data automatically preloaded.
