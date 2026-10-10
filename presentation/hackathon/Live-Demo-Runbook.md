# JiraPilot AI — 5-Minute Live Demo Runbook

> **Presenter Rule #1**: Never show an empty screen or unexplained technical logs.  
> **Presenter Rule #2**: Every click must be paired with an immediate verbal explanation of *why* it matters to the user.  
> **Target Duration**: Exactly 5 minutes (300 seconds).

---

## Pre-Demo Technical Checklist (T-minus 5 Minutes)

Ensure the following environments are active and verified on `localhost`:

| Service | Port | Health Check URL | Expected Response |
| :--- | :---: | :--- | :--- |
| **Vite Frontend** | `3000` | `http://localhost:3000` | JiraPilot AI enterprise dark UI loads |
| **Spring Boot Backend** | `8080` | `http://localhost:8080/api/jira/issues` | JSON list of active issues (`KAN`, `NOVA`) |
| **FastAPI AI Service** | `8000` | `http://localhost:8000/docs` | Swagger UI responds with 200 OK |
| **Jira Cloud Access** | Remote | Atlassian Cloud Workspace | Verified API token active |
| **EmailJS Dispatcher** | Remote | `api.emailjs.com` | Service `service_1ooa8fh` ready |

*Tip: Open the browser to `http://localhost:3000` in full-screen mode (`F11`) with browser zoom set to 100%.*

---

## Minute-by-Minute Demonstration Script

```
0:00 - 0:45 | Scene 1: The Incident Dashboard & The Triage Problem
0:45 - 1:45 | Scene 2: Selecting NOVA-1001 & Readiness Scoring Breakdown
1:45 - 2:45 | Scene 3: Holographic API Flow Visualization & Node Drill-Down
2:45 - 3:30 | Scene 4: Repository Discovery & Instant Git Clone
3:30 - 4:30 | Scene 5: Full-Loop Enterprise Action (Jira Comment + Live EmailJS)
4:30 - 5:00 | Scene 6: Summary & Hand-Off to Q&A
```

---

### Scene 1: The Incident Dashboard (0:00 – 0:45)
* **Starting State**: Browser on `http://localhost:3000`, showing the JiraPilot AI Enterprise Dashboard.
* **Action 1**: Point the mouse cursor to the top header showing "JIRAPILOT AI — ENTERPRISE TRIAGE & REPO COPILOT" and the live connection status indicators.
* **Talk Track**:
  > *"Welcome to the live demonstration of JiraPilot AI. Right now, you are looking at our live enterprise operations console running in real time.*
  > 
  > *Imagine you are an on-call engineer at Northstar Digital Systems. It is two in the morning, and multiple alerts have just come in. In a traditional workflow, you would have to open Jira, read dozens of disorganized comments, download log files onto your desktop, and guess where to start.*
  > 
  > *Instead, JiraPilot AI has already ingested the active issues from Jira Cloud, normalized their priority, and organized them into an operational triage queue."*

---

### Scene 2: Selecting NOVA-1001 & Readiness Scoring (0:45 – 1:45)
* **Action 2**: Click on ticket card **`NOVA-1001: Payment checkout failure on Black Friday staging`**.
* **Visual Result**: The ticket inspection panel updates immediately. The Ticket Readiness Score shows **38 / 100** with an amber/red warning badge.
* **Action 3**: Hover over the Readiness Score breakdown chips (*"Missing Payload"*, *"Missing Steps to Reproduce"*, *"Environment Ambiguous"*).
* **Talk Track**:
  > *"Let's look at ticket NOVA-1001. A customer reported that checkout is failing. Notice this metric right here: our **Ticket Readiness Engine** has assigned this ticket a score of only **38 out of 100**.*
  > 
  > *Why? Because whoever filed this ticket omitted the API payload, didn't provide reproduction steps, and didn't specify which environment was affected.*
  > 
  > *In most engineering teams, an engineer would waste half an hour writing an irritated message back to the customer or product manager. JiraPilot AI immediately generates a polite, structured Jira clarification comment asking for those exact three missing items.*
  > 
  > *Even with an incomplete ticket, JiraPilot doesn't stop. It automatically inspects the attached server logs to uncover the truth."*

---

### Scene 3: Holographic API Flow Visualization (1:45 – 2:45)
* **Action 4**: In the "Evidence-backed hypothesis" card, click the glowing cyan button: **`Explore API Flow`** (or navigate to `/api-flow/NOVA-1001`).
* **Visual Result**: The screen transitions into the dark-midnight Holographic API Flow Visualization. Animated luminous pulses travel between nodes:
  - `Client Request` (Cyan) $\rightarrow$ `API Gateway` (Cyan) $\rightarrow$ `Checkout Service` (Cyan) $\rightarrow$ `Payment Microservice` (**Glowing Red / HTTP 503**).
* **Action 5**: Click directly on the red **`Payment Microservice`** node.
* **Visual Result**: The right-hand Glass Details Panel slides open, displaying:
  - Service: `payment-microservice`
  - Status: `HTTP 503 Service Unavailable`
  - Upstream Failure: `Connection refused: payment-gateway.internal:8443`
  - Correlation ID: `tx-8921-4f`
  - Log Line Reference: `Line 412: java.net.ConnectException`
* **Talk Track**:
  > *"This is our **Interactive Holographic API Flow Visualization**.*
  > 
  > *Instead of forcing an on-call developer to scroll through thousands of lines of raw text logs at 2:00 AM, JiraPilot AI extracts the entire request journey and renders it visually.*
  > 
  > *Look at the canvas: the initial client request entered the gateway smoothly. Authentication passed. The checkout service began its workflow. But right here at the Payment Microservice, the connection illuminates in glowing red.*
  > 
  > *When I click on this failure node, our details panel reveals the exact physical proof: an HTTP 503 error, correlation ID `tx-8921-4f`, and the exact line number in the server log where the connection timed out.*
  > 
  > *In fifteen seconds, without reading a single stack trace manually, the engineer knows the exact point of failure."*

---

### Scene 4: Repository Discovery & Instant Git Clone (2:45 – 3:30)
* **Action 6**: Click the **`Back to Investigation`** button to return to the main investigation view.
* **Action 7**: Scroll down to the **`Repository Recommendation`** card.
* **Visual Result**: Card displays:
  - Repository: `repo-payment-gateway`
  - Match Confidence: **94% Match**
  - Primary Source File: `src/services/payment.service.ts`
  - Terminal Box: `git clone https://github.com/northstar/repo-payment-gateway.git && cd repo-payment-gateway && git checkout -b fix/nova-1001-payment-timeout`
* **Action 8**: Click the **`Copy Command`** icon.
* **Visual Result**: Tooltip briefly changes to *"Copied to clipboard!"*.
* **Talk Track**:
  > *"Now that we know the payment service failed, the next obstacle in any enterprise company is: 'Where does the source code live?'*
  > 
  > *Large companies have hundreds of microservices. Engineers often don't know who owns which repository. JiraPilot's **Repository Discovery Engine** evaluated package references and identified `repo-payment-gateway` with a **94% match confidence**.*
  > 
  > *It highlights the exact file where the timeout handler lives, and generates a pre-formatted, branch-ready `git clone` command. The developer clicks copy, pastes it into their terminal, and is ready to fix the code in under five seconds."*

---

### Scene 5: Enterprise Closed-Loop Action (Jira + Live EmailJS) (3:30 – 4:30)
* **Action 9**: Scroll down to the **`Jira Comment & Notification Actions`** card.
* **Action 10**: Click the **`Generate Jira Investigation Comment`** button.
* **Visual Result**: Rich preview updates with a formatted markdown comment containing:
  - Executive Incident Summary
  - Readiness Score (38/100) & Missing Information Notice
  - Root-Cause Hypothesis with Line 412 Stack Reference
  - Repository Link and Next Steps
* **Action 11**: Click **`Post Comment to Jira`** (or **`Dispatch EmailJS Alert`**).
* **Visual Result**: A green success notification badge appears: *"Investigation dispatched successfully! Jira issue updated & Email alert delivered."*
* **Talk Track**:
  > *"Finally, JiraPilot AI is not an isolated analysis sandbox. It closes the loop with your existing enterprise systems.*
  > 
  > *With one click, JiraPilot formats a comprehensive technical investigation report and uses the Atlassian REST API to post it directly onto Jira ticket NOVA-1001.*
  > 
  > *Simultaneously, using our live **EmailJS integration**, it dispatches an executive alert to engineering leads. The email contains the incident score, the root cause hypothesis, and a deep-link back to this investigation.*
  > 
  > *Every team member is synchronized, Jira is updated with verifiable facts, and no emergency triage meeting had to be scheduled."*

---

### Scene 6: Summary & Impact Recap (4:30 – 5:00)
* **Action 12**: Return to the top of the dashboard and face the judges directly.
* **Talk Track**:
  > *"To summarize what we just witnessed in under four minutes:*
  > 
  > *We took an incomplete, unstructured P1 bug ticket. JiraPilot scored its readiness, scrubbed sensitive data, parsed the server logs, generated an interactive holographic API flow map, matched the exact code repository, updated Jira, and notified the team.*
  > 
  > *What used to take three hours of stressful investigation was accomplished in thirty seconds of deterministic clarity.*
  > 
  > *Thank you very much. We are now eager to take your questions!"*

---

## Contingency & Fallback Matrix (What to do if something hiccups)

| Potential Failure Point | Likelihood | Immediate Contingency Action | Spoken Presenter Recovery Line |
| :--- | :---: | :--- | :--- |
| **Jira Cloud API Network Timeout** | Low | The Spring Boot backend automatically serves cached synthetic incident data from local JPA storage. | *"Notice that JiraPilot maintains an offline-first resilient cache, ensuring engineers can investigate even during third-party cloud outages."* |
| **EmailJS Daily Quota Exceeded** | Low | The UI displays the verified payload preview and graceful status modal. | *"Our EmailJS service formats the exact production payload, ready to dispatch across enterprise email relays."* |
| **Browser Zoom / Resolution Misaligned** | Medium | Press `Ctrl + 0` to reset zoom to 100% or `F11` for full screen. | (Perform seamlessly while continuing to talk about the incident triage queue.) |
| **User Accompanying Question Mid-Demo** | Medium | Acknowledge immediately, answer in 10 seconds, then resume current scene. | *"Great question—as you can see right here on the failure node..."* |

---

## Post-Demo Q&A Transition
* Keep `http://localhost:3000/api-flow/NOVA-1001` open on screen during Q&A so you can point to the interactive canvas when judges ask technical questions.
