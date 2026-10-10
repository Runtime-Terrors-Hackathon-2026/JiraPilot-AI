# JiraPilot AI — Project A-to-Z Guide & Conceptual Encyclopedia

> **Audience**: Business stakeholders, hackathon judges, enterprise architects, and software engineers seeing JiraPilot AI for the first time.  
> **Structure**: Every letter from A to Z provides:
> 1. **Plain-English Definition**: A concise, 1-sentence explanation free of undefined jargon.
> 2. **Real-World Analogy**: An accessible comparison from everyday life.
> 3. **How It Works in JiraPilot AI**: Specific architectural role and implementation behavior.
> 4. **Implementation Status**: Exact codebase status (Implemented & tested / Implemented unverified / Demo-only / Planned future).

---

### A — API Flow Visualization

* **Plain-English Definition**: A visual map illustrating how an incoming web request travels step-by-step through interconnected software services to fulfill a task.
* **Real-World Analogy**: Like a package tracking roadmap that shows your parcel traveling from the warehouse, to the sorting hub, to the delivery truck, highlighting the exact checkpoint where the truck stopped.
* **How It Works in JiraPilot AI**: JiraPilot inspects error logs and traces the journey of a request from the Client to the API Gateway, to upstream microservices. It renders this on an interactive holographic SVG canvas where healthy hops shine in cyan and the failing node glows in red.
* **Implementation Status**: **Implemented and Tested** (Accessible via `ApiFlowPage.tsx` and route `/api-flow/:issueKey`).

---

### B — Black Box Telemetry

* **Plain-English Definition**: The automated recording of system events, timings, and error logs during normal operation, used to diagnose unexpected malfunctions.
* **Real-World Analogy**: The flight data recorder in commercial airplanes that continuously logs engine temperatures, altitude, and sensor readings so investigators can reconstruct an incident.
* **How It Works in JiraPilot AI**: JiraPilot ingests raw console outputs, server error traces, and status codes attached to Jira tickets, treating them as an objective flight recorder to establish facts rather than human opinions.
* **Implementation Status**: **Implemented and Tested** (Integrated within the Python AI Log Parser and Spring Boot attachment parser).

---

### C — Correlation ID (Trace Identifier)

* **Plain-English Definition**: A unique alphanumeric fingerprint assigned to a single user request so all actions across dozens of computers can be linked together.
* **Real-World Analogy**: A baggage claim ticket number: regardless of which conveyor belts or airports your suitcase touches, that single ticket links all movements back to your trip.
* **How It Works in JiraPilot AI**: When an incident occurs, JiraPilot extracts values like `corrId: tx-8921-4f` from incoming logs. This allows the system to filter out background noise and reconstruct the exact sequence of events for the failing user session.
* **Implementation Status**: **Implemented and Tested** (Deterministic regex extraction in `telemetry_parser.py` and visualized in the timeline).

---

### D — Deterministic Readiness Scoring

* **Plain-English Definition**: An automated checklist that grades a bug ticket on a 100-point scale based on whether essential debugging details are present.
* **Real-World Analogy**: A pre-flight safety checklist used by pilots before takeoff—the plane is not allowed to leave the tarmac if tire pressure or fuel levels are unverified.
* **How It Works in JiraPilot AI**: JiraPilot checks whether the ticket contains an endpoint, environment, steps to reproduce, user role, and log attachment. A score below 60 flags the ticket as "Incomplete" and prompts JiraPilot to generate clarification questions for the submitter.
* **Implementation Status**: **Implemented and Tested** (Handled by the Spring Boot scoring rules and displayed on the main dashboard).

---

### E — EmailJS Notification Gateway

* **Plain-English Definition**: A cloud service that sends real-time email alerts directly from web and enterprise applications without requiring an internal mail server.
* **Real-World Analogy**: A high-priority messenger who immediately carries a certified telegram to the department head when an urgent alarm sounds.
* **How It Works in JiraPilot AI**: When an investigation completes, JiraPilot triggers an executive summary email containing the incident score, root-cause hypothesis, and dashboard link to designated engineering leads using live verified EmailJS templates.
* **Implementation Status**: **Implemented and Tested** (Verified in production with service `service_1ooa8fh` and template `template_ohed206`).

---

### F — Failure Hypothesis Generation

* **Plain-English Definition**: An evidence-backed explanation produced by AI describing why a system failed, supported by line numbers and error codes.
* **Real-World Analogy**: A forensic detective report detailing not just that a car crashed, but showing brake-pad wear marks on the road as physical proof.
* **How It Works in JiraPilot AI**: JiraPilot analyzes stack traces and HTTP error codes to output a concise diagnostic hypothesis (e.g., *"Upstream payment gateway timeout returned HTTP 503 during checkout payload validation"*), explicitly referencing line numbers in the attached log.
* **Implementation Status**: **Implemented and Tested** (Returned via `/api/analyze` and displayed in the Investigation Card).

---

### G — Git Clone & Repository Matching

* **Plain-English Definition**: The ability to identify which source code project caused an incident and provide engineers with an immediate one-click command to download it.
* **Real-World Analogy**: A mechanic's manual that immediately opens to the exact page and tells you which toolbox to grab when a specific engine code flashes.
* **How It Works in JiraPilot AI**: By analyzing package declarations, error stack traces, and microservice names, JiraPilot selects the target Git repository with a percentage confidence match and generates a ready-to-run `git clone` terminal command.
* **Implementation Status**: **Implemented and Tested** (Available in the Repository Recommendation section of the dashboard).

---

### H — Holographic Isometric Canvas

* **Plain-English Definition**: A high-tech visual display that presents network nodes and services with glowing, layered geometry to make complex architectures easy to understand.
* **Real-World Analogy**: The glowing 3D tactical radar displays seen in airport air-traffic control towers.
* **How It Works in JiraPilot AI**: Built using hardware-accelerated SVG and CSS glow filters, the canvas renders services in isometric perspective. It pulsates with animated network traffic lines without slowing down the user's web browser.
* **Implementation Status**: **Implemented and Tested** (Engineered in `ApiFlowCanvas.tsx` with zero heavy WebGL dependencies).

---

### I — Investigation History & Audit Log

* **Plain-English Definition**: A permanent, searchable ledger that records every bug analysis, timestamp, findings, and notifications sent over time.
* **Real-World Analogy**: A hospital medical chart that records every doctor's consultation, prescription, and vital sign reading for future review.
* **How It Works in JiraPilot AI**: Every processed Jira issue is saved into an H2/PostgreSQL database with its readiness score, log extraction findings, generated comment, and dispatch status, allowing teams to review historical incidents anytime.
* **Implementation Status**: **Implemented and Tested** (Persisted via Spring Boot JPA `InvestigationRepository`).

---

### J — Jira Cloud REST API Integration

* **Plain-English Definition**: The programmatic bridge that allows JiraPilot AI to read issues, download attachments, and write comments directly inside Atlassian Jira Cloud.
* **Real-World Analogy**: A diplomatic courier with an official keycard who walks into Jira's headquarters, reviews open tickets, and stamps official reports on them.
* **How It Works in JiraPilot AI**: JiraPilot connects to Jira Cloud via REST API v3 using HTTPS basic authentication. It retrieves issue summaries, labels, and file attachments, and can post back formatted technical comments on demand.
* **Implementation Status**: **Implemented and Tested** (Active across Jira projects `KAN` and `NOVA`).

---

### K — Key-Value Secret Redaction (Zero-Trust Privacy)

* **Plain-English Definition**: An automated security filter that detects and masks passwords, tokens, API keys, and sensitive user data before it is processed or shared.
* **Real-World Analogy**: A legal redaction pen that blacks out Social Security numbers and credit card numbers from court evidence before showing it to the jury.
* **How It Works in JiraPilot AI**: Before any log content is analyzed by AI models or saved to databases, regular-expression filters replace sensitive patterns (e.g., `Bearer ey...` or `password=secret`) with sanitized placeholders like `[REDACTED_SECRET]`.
* **Implementation Status**: **Implemented and Tested** (Enforced in both frontend preview buffers and backend telemetry ingestors).

---

### L — Log Telemetry Parsing

* **Plain-English Definition**: The automated process of scanning thousands of lines of computer logs to extract meaningful facts like timestamps, error codes, and URLs.
* **Real-World Analogy**: A high-speed digital highlighter that scans a 500-page book in one second and highlights only the names of suspects and times of events.
* **How It Works in JiraPilot AI**: JiraPilot's Python engine scans raw log files using deterministic regex patterns. It isolates HTTP methods (`POST`, `GET`), response codes (`500`, `503`), endpoints (`/api/v1/checkout`), and source line numbers.
* **Implementation Status**: **Implemented and Tested** (Executed by `app/services/log_parser.py`).

---

### M — Mean Time to Investigate (MTTI / MTTR)

* **Plain-English Definition**: The average number of minutes or hours it takes for an engineering team to identify what caused a software outage.
* **Real-World Analogy**: The response time of emergency firefighters between receiving an emergency call and arriving on the scene to locate the source of the fire.
* **How It Works in JiraPilot AI**: JiraPilot targets the investigation phase of incident management, compressing the initial root-cause discovery time from an industry baseline of 180 minutes down to approximately 32 minutes.
* **Implementation Status**: **Measurable Pilot Metric** (Documented in `Business-Value-and-Impact.md`).

---

### N — NVIDIA NIM Microservices & Multi-LLM Fallback

* **Plain-English Definition**: Optimized cloud AI services and backup models that allow software to generate human-like summaries and reasoning safely and quickly.
* **Real-World Analogy**: Having an emergency backup electrical generator in a hospital: if the main power grid goes down, the backup generator starts instantly without interrupting surgeries.
* **How It Works in JiraPilot AI**: JiraPilot can connect to enterprise NVIDIA NIM endpoints (e.g., Llama 3 models) for root-cause synthesis. If external AI endpoints are unreachable, it falls back seamlessly to deterministic rule-based analysis without crashing.
* **Implementation Status**: **Implemented with Resilient Local Rule Fallback** (Configured via `AI_PROVIDER` and environment adapters).

---

### O — Observability Pipeline

* **Plain-English Definition**: The complete system of software tools that monitors, gathers, and displays the health and status of computing applications.
* **Real-World Analogy**: The full dashboard in a pilot's cockpit displaying airspeed, fuel gauges, altitude, radar, and engine status all in one unified view.
* **How It Works in JiraPilot AI**: JiraPilot sits between issue tracking (Jira) and observability (logs, APM metrics), turning raw telemetry into structured, human-readable root-cause intelligence.
* **Implementation Status**: **Implemented and Tested** (End-to-end integration between Jira attachments, backend parser, and interactive canvas).

---

### P — Polyglot Microservice Architecture

* **Plain-English Definition**: Building a software system using multiple programming languages, picking the best language for each specific job.
* **Real-World Analogy**: A world-class kitchen where the head baker is French, the pasta specialist is Italian, and the sushi chef is Japanese—each doing what they excel at.
* **How It Works in JiraPilot AI**: JiraPilot uses **TypeScript/React 18** for a responsive user interface, **Java 21 / Spring Boot 3** for secure enterprise business logic and Jira connectors, and **Python 3.12 / FastAPI** for rapid AI and telemetry text parsing.
* **Implementation Status**: **Implemented and Tested** (All three services run concurrently and communicate via REST).

---

### Q — Query Rate Limiting & Resilience

* **Plain-English Definition**: Built-in safeguards that prevent a system from making too many requests to external servers, avoiding throttling or system lockouts.
* **Real-World Analogy**: A revolving door that only allows one person through at a time during rush hour to prevent a dangerous stampede in the lobby.
* **How It Works in JiraPilot AI**: When communicating with Jira Cloud or email gateways, JiraPilot enforces exponential backoff and rate-limiting policies, ensuring third-party APIs are never overwhelmed during mass alert incidents.
* **Implementation Status**: **Implemented and Tested** (Managed in Spring Boot client services).

---

### R — Repository Catalog Matcher

* **Plain-English Definition**: An algorithmic matching engine that compares error traces against an internal inventory of software repositories to determine code ownership.
* **Real-World Analogy**: A lost-and-found registry that scans a lost dog's microchip and instantly matches it with the owner's home address and phone number.
* **How It Works in JiraPilot AI**: The system uses fuzzy string matching and heuristic scoring on package paths (e.g., `com.northstar.checkout`) to rank internal repositories (e.g., `repo-payment-gateway` at 94% confidence).
* **Implementation Status**: **Implemented and Tested** (Available in `/api/repositories/recommend`).

---

### S — Spring Boot Core Engine

* **Plain-English Definition**: A battle-tested enterprise Java framework used by Fortune 500 companies to build secure, high-speed business software.
* **Real-World Analogy**: The high-strength steel chassis and suspension of a commercial truck that supports the engine and payload under heavy duty.
* **How It Works in JiraPilot AI**: Spring Boot 3 handles security filters, JPA database management, Jira REST API calls, EmailJS webhook dispatch, and audit logging with enterprise-grade reliability.
* **Implementation Status**: **Implemented and Tested** (Runs on port 8080 with clean Maven build).

---

### T — Ticket Ingestion Pipeline

* **Plain-English Definition**: The automated workflow that fetches newly created or updated bug reports from Jira and prepares them for immediate analysis.
* **Real-World Analogy**: An automated mailroom scanner that opens incoming letters, sorts them by priority, and places them onto the correct desk.
* **How It Works in JiraPilot AI**: JiraPilot queries the Jira Cloud REST API, identifies new issues, extracts descriptions, downloads associated log attachments, and feeds them into the evaluation pipeline.
* **Implementation Status**: **Implemented and Tested** (Operates both on manual sync and scheduled polling).

---

### U — Unstructured Incident Triaging

* **Plain-English Definition**: Converting messy, free-text bug descriptions written by different humans into organized, categorized, and standardized technical data.
* **Real-World Analogy**: A triage nurse in an emergency room who listens to a patient describe their symptoms and translates them into medical vital signs and priority codes.
* **How It Works in JiraPilot AI**: JiraPilot takes vague descriptions like *"Checkout button is frozen"* and translates them into structured fields: HTTP status codes, failing endpoints, impacted environments, and required follow-up actions.
* **Implementation Status**: **Implemented and Tested** (Core functionality of the JiraPilot analysis engine).

---

### V — Vector & Semantic Code Search

* **Plain-English Definition**: Searching for software code based on what the code *does conceptually*, rather than searching for exact keyword matches.
* **Real-World Analogy**: Searching a recipe app for "quick comforting dinner" and getting tomato soup, even if the word "dinner" isn't in the recipe title.
* **How It Works in JiraPilot AI**: JiraPilot indexes repository metadata and class responsibilities to link natural-language bug descriptions to the right code modules even when the exact error message isn't present in the code.
* **Implementation Status**: **Implemented via Lexical & Package Heuristics; Full Dense Embedding Vector Search Planned for Phase 2**.

---

### W — Webhook Dispatcher

* **Plain-English Definition**: An automated mechanism that sends instant notifications to other systems the exact moment an event occurs.
* **Real-World Analogy**: An automated doorbell that sends an alert to your phone the millisecond someone steps on the front porch.
* **How It Works in JiraPilot AI**: When an investigation completes, JiraPilot dispatches webhooks to external services like EmailJS and Jira Cloud without requiring human intervention.
* **Implementation Status**: **Implemented and Tested** (Active for EmailJS alerts and Jira comments).

---

### X — X-Ray Stack Trace Extraction

* **Plain-English Definition**: Deep analysis of a software crash report that reveals the exact line of code that triggered the failure, filtering out standard system code.
* **Real-World Analogy**: A doctor examining an X-ray who looks past healthy ribs and muscles to pinpoint the hairline bone fracture in seconds.
* **How It Works in JiraPilot AI**: Server stack traces can contain hundreds of lines of framework overhead. JiraPilot's parser filters out third-party framework lines to highlight the exact business logic line (e.g., `payment.service.ts:412`) where execution failed.
* **Implementation Status**: **Implemented and Tested** (Visible in the Evidence-backed Hypothesis view).

---

### Y — YAML & Configuration Manifests

* **Plain-English Definition**: Human-readable configuration files used to control how microservices, security tokens, and deployment environments behave.
* **Real-World Analogy**: An instruction manual that tells an appliance whether to use Celsius or Fahrenheit and which electrical outlet to plug into.
* **How It Works in JiraPilot AI**: JiraPilot uses configuration manifests (`application.yml` and `.env`) to manage environment variables, third-party API keys, fallback thresholds, and server ports cleanly without hardcoded secrets.
* **Implementation Status**: **Implemented and Tested** (Standard configuration pattern used across Spring Boot and FastAPI).

---

### Z — Zero-Trust Security Pipeline

* **Plain-English Definition**: A security design philosophy where software treats every piece of incoming data as potentially dangerous and verifies and sanitizes everything before use.
* **Real-World Analogy**: An airport security checkpoint where every passenger, including airport staff, passes through the metal detector and baggage scanner before entering the gate area.
* **How It Works in JiraPilot AI**: JiraPilot assumes all logs contain unvetted credentials, PII, or internal tokens. It applies client-side and server-side sanitization *before* any text is forwarded to AI reasoning engines or third-party APIs.
* **Implementation Status**: **Implemented and Tested** (Enforced across all telemetry and API workflows).
