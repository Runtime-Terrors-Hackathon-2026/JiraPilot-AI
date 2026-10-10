# JiraPilot AI — Hackathon Presentation Content (Slide-by-Slide)

> **Theme:** Deep Purple (`#170B2B`) & Near-Black (`#08070D`) with Electric Violet (`#8B5CF6`) and Lavender (`#C4B5FD`) Accents  
> **Format:** 16:9 Widescreen Presentation (8 Slides)  
> **Style:** Premium Enterprise AI Launch Film Aesthetic — Explained in Clear, Easy-to-Understand English

---

## Slide 1 — Cinematic Opening

* **Headline:** Turn Jira issues into actionable investigations.
* **Subtitle:** AI-powered ticket triage, log analysis, and approved repository discovery.
* **Visual Composition:**
  * Clean, near-black canvas (`#08070D`) with expanding concentric violet light rings.
  * Original geometric JiraPilot AI flight emblem with glowing lavender core centered on screen.
  * Minimalist typography with elegant visual hierarchy and subtle accent line.
  * Tagline: *JiraPilot AI — Your investigation copilot.*
* **Plain English Explanation:**
  When software breaks, developers get overwhelmed by messy bug reports. JiraPilot AI organizes the investigation from the very first second so engineers know exactly where to begin.

---

## Slide 2 — The Problem

* **Headline:** Too much time spent finding where to start.
* **Sub-headline:** Software engineering teams face four major friction points during initial incident triage.
* **Four Content Cards:**
  1. **Incomplete Jira Tickets:** Incidents filed with missing server logs, unclear environments, and absent request payloads require tedious manual back-and-forth follow-ups.
  2. **Scattered Telemetry:** Engineers must manually dig through different logging consoles, correlation IDs, and timestamps to find relevant failure events.
  3. **Manual Error Extraction:** Parsing distributed stack traces, HTTP 503 cascades, and circuit breaker trip states consumes valuable senior engineering focus.
  4. **Locating The Right Repository:** Large microservice architectures make finding the exact service code repository, clone command, and local reproduction steps frustrating.
* **Closing Insight:**
  > *"The challenge isn't only solving the issue. It's organizing the investigation."*

---

## Slide 3 — Ticket Readiness

* **Headline:** Every new issue gets a clearer next step.
* **Sub-headline:** Automated completeness audit highlights missing fields and prepares reporter clarification comments.
* **Embedded Media:** `assets/gifs/01-jira-ticket-readiness.gif`
* **Workflow Demonstrated:**
  * Incoming synthetic Jira ticket `NOVA-1001` received via webhook.
  * Evaluates 4 essential criteria: Summary & Context, API Endpoint, Application Server Logs, Request Payload.
  * Highlights missing fields in warm **amber** (`#FBBF24`) — no premature guessing.
  * Generates a polite, copy-ready clarification comment asking the reporter for the exact missing details.
  * Updates issue status to `WAITING_FOR_INFO` only when operation succeeds.
* **Caption:**
  > **Identify missing information before investigation goes deeper.**

---

## Slide 4 — Log Analysis

* **Headline:** Turn raw logs into structured evidence.
* **Sub-headline:** Extracts endpoints, status codes, and correlation traces while maintaining clear hypothesis boundaries.
* **Embedded Media:** `assets/gifs/02-log-analysis.gif`
* **Synthetic Evidence Group:**
  * **File:** `application-demo.log`
  * **Detected Endpoint:** `POST /api/v1/resources/allocate`
  * **HTTP Status:** `503 Service Unavailable`
  * **Correlation ID:** `CORR-DEMO-1001`
  * **Observed Chain:** 3 retries failed → Circuit breaker tripped to `OPEN`.
* **Responsible AI Note:**
  * Displays: `⚠ Probable Cause — Verification Required`.
  * Clearly states that findings are evidence-backed hypotheses, not assumed root causes, keeping engineers in control.
* **Caption:**
  > **From raw log lines to a clearer debugging path.**

---

## Slide 5 — Repository Discovery

* **Headline:** Find a relevant place to start debugging.
* **Sub-headline:** Multi-signal catalog lookup maps endpoints to verified synthetic repositories with zero invented URLs.
* **Embedded Media:** `assets/gifs/03-repository-discovery.gif`
* **Configured Repository Catalog Match:**
  * **Matched Repo:** `resource-inventory-service`
  * **Approved Clone URL:** `https://github.com/northstar-labs/resource-inventory-service.git`
  * **Matching Logic:** Route Match (Weight 35) + Package Trace (Weight 25) + Service ID.
  * **Developer Convenience:** Provides an animated, copy-ready `git clone` command in a clean terminal card.
  * **Security & Accuracy Guarantee:** Only project-configured repositories are surfaced; never hallucinated ad-hoc URLs.
* **Caption:**
  > **Give developers a more direct starting point for investigation.**

---

## Slide 6 — Reporting and Notifications

* **Headline:** Clear findings. Better handoffs.
* **Sub-headline:** Structured investigation reports posted to Jira Cloud with concise stakeholder email notifications.
* **Embedded Media:** `assets/gifs/04-jira-email-reporting.gif`
* **Standardized Investigation Report:**
  1. **Executive Summary:** Quick impact overview.
  2. **Observed Evidence:** Exact endpoints, HTTP status codes, and correlation IDs.
  3. **Probable Cause:** Synthesized hypothesis with confidence score (e.g. 88%).
  4. **Recommended Next Steps:** Suggested configuration changes and local test reproduction scripts.
  5. **Repository Link:** Approved Git URL for the service.
  6. **Honest Delivery Status:** Explicitly labelled as `Simulated Demo Mode` in test environments.
* **Caption:**
  > **Prepare consistent investigation updates without repetitive manual writing.**

---

## Slide 7 — Connected Architecture

* **Headline:** One connected investigation workflow.
* **Sub-headline:** Modular multi-tier architecture connecting Atlassian Jira, Spring Boot, FastAPI, and React.
* **Embedded Media:** `assets/gifs/05-end-to-end-workflow.gif`
* **Architecture Flow Pipeline:**
  1. **Atlassian Jira Cloud:** Real-time webhook ingestion for project NOVA.
  2. **Spring Boot Orchestrator (Java 21):** Manages triage workflows, state transitions, and audit records.
  3. **Python FastAPI Service (Python 3.12):** High-speed log correlation and payload validation.
  4. **AI Provider Adapter:** Evidence synthesis and root-cause hypothesis generation.
  5. **Repository Matcher:** Enterprise service catalog mapper.
  6. **Notification Engine:** Standardized Jira comment formatter & optional email dispatcher.
  7. **React Console:** Dark-mode web interface for monitoring incident telemetry.
* **Four Core Benefits:**
  * Consistent ticket completeness checks.
  * Clustered, correlation-backed evidence.
  * Instant access to the right code repositories.
  * Standardized handoff notes for SREs and developers.
* **Caption:**
  > **Designed to organize the investigation while keeping developers in control.**

---

## Slide 8 — Cinematic Closing

* **Headline:** Less repetitive triage. More time to solve.
* **Subtitle:** JiraPilot AI — Your investigation copilot.
* **Visual Composition:**
  * Centered glowing geometric emblem.
  * Deep violet radial ambient lighting with concentric rings.
  * Elegant product title and tagline reveal.
  * Quiet fade to black.
