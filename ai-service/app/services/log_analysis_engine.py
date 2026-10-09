"""
Comprehensive Log Analysis and Evidence Correlation Engine for JiraPilot AI (Northstar Digital Systems)
Performs deterministic log extraction, line-referenced evidence gathering, repository discovery,
NVIDIA LLM contextual reasoning, and structured findings categorization.
"""

import re
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.services.redaction import sanitize_and_redact
from app.services.repository_matcher import match_repositories
from app.services.nvidia_client import analyze_with_nvidia, get_nvidia_status

TIMESTAMP_PATTERN = re.compile(
    r'\b(?P<ts>\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d{3,6})?(?:Z|[+-]\d{2}:?\d{2})?)\b'
)

LEVEL_PATTERN = re.compile(
    r'\b(?P<level>FATAL|ERROR|WARN|WARNING|INFO|DEBUG|TRACE)\b',
    re.IGNORECASE
)

CORRELATION_PATTERN = re.compile(
    r'(?:correlationId|requestId|traceId|corrId|corr_id|x-correlation-id)[=:\s]+(?P<id>[A-Za-z0-9_\-]+)',
    re.IGNORECASE
)

HTTP_PATTERN = re.compile(
    r'(?:(?P<method>GET|POST|PUT|DELETE|PATCH)\s+(?P<endpoint>/[^\s,;"\']+))|(?:(?:endpoint|path|url)[=:\s]+(?P<endpoint2>/[^\s,;"\']+))',
    re.IGNORECASE
)

STATUS_PATTERN = re.compile(
    r'(?:status(?:Code)?|HTTP|code)[=:\s]+(?P<code>[1-5]\d{2})\b',
    re.IGNORECASE
)

EXCEPTION_PATTERN = re.compile(
    r'\b(?P<exc>[A-Za-z0-9_\.]*(?:Exception|Error))\b'
)

STACK_TRACE_FRAME = re.compile(
    r'^\s*at\s+(?P<class>[A-Za-z0-9_\.$]+)\.(?P<method>[A-Za-z0-9_<>]+)\((?P<file>[A-Za-z0-9_\.]+):(?P<line>\d+)\)'
)

KNOWN_SERVICES = [
    "service-request-api",
    "workflow-orchestrator",
    "request-validation-engine",
    "resource-inventory-service",
    "capacity-planning-api",
    "topology-registry",
    "integration-gateway",
    "event-delivery-service",
    "partner-connect-api",
    "incident-intelligence-service",
    "log-correlation-engine",
    "recovery-coordinator"
]

class LogAnalysisEngine:

    @staticmethod
    async def analyze_log(
        log_text: str,
        filename: Optional[str] = "upload.log",
        ticket_key: Optional[str] = "NOVA-SIM",
        analysis_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end log triage, parsing, evidence extraction,
        repository discovery, and root cause synthesis.
        """
        analysis_id = analysis_id or f"LA-{uuid.uuid4().hex[:8].upper()}"
        created_at = datetime.now(timezone.utc).isoformat()

        if not log_text or not log_text.strip():
            return {
                "analysisId": analysis_id,
                "ticketKey": ticket_key,
                "filename": filename,
                "status": "COMPLETED",
                "isComplete": False,
                "summary": "Empty or missing log file content.",
                "probableRootCause": "Inconclusive - no log telemetry provided.",
                "confidenceScore": 0.0,
                "confidenceCategory": "INCONCLUSIVE",
                "observedFacts": [],
                "evidenceHypotheses": [],
                "unconfirmedPossibilities": ["Log file was empty or corrupted during upload"],
                "recommendedDebuggingSteps": ["Re-upload valid log file containing application telemetry."],
                "suggestedTestCases": [],
                "evidence": [],
                "endpoints": [],
                "services": [],
                "repositoryMatches": [],
                "createdAt": created_at,
                "nvidiaUsed": False
            }

        # 1. Sanitize and redact
        sanitized_text, quarantine_required, quarantine_reasons, redaction_counts = sanitize_and_redact(log_text)

        if quarantine_required:
            return {
                "analysisId": analysis_id,
                "ticketKey": ticket_key,
                "filename": filename,
                "status": "NEEDS_REVIEW",
                "isComplete": False,
                "summary": "Log analysis quarantined due to detected sensitive credentials or private key patterns.",
                "probableRootCause": "Quarantined - external and automated processing halted for security compliance.",
                "confidenceScore": 0.0,
                "confidenceCategory": "QUARANTINED",
                "observedFacts": [f"Quarantine trigger: {reason}" for reason in quarantine_reasons],
                "evidenceHypotheses": [],
                "unconfirmedPossibilities": ["Log may contain unredacted internal security keys."],
                "recommendedDebuggingSteps": [
                    "Manual security officer review required.",
                    "Strip raw private keys or certificates before re-uploading."
                ],
                "suggestedTestCases": [],
                "evidence": [],
                "endpoints": [],
                "services": [],
                "repositoryMatches": [],
                "createdAt": created_at,
                "nvidiaUsed": False,
                "quarantined": True,
                "quarantineReasons": quarantine_reasons
            }

        # 2. Deterministic line-by-line parsing
        lines = sanitized_text.splitlines()
        line_count = len(lines)

        detected_endpoints = []
        detected_methods = []
        detected_status_codes = []
        detected_exceptions = []
        detected_services = set()
        detected_correlation_ids = set()
        stack_frames = []
        evidence_entries = []
        downstream_calls = []

        # Check if entire payload or line is JSON
        is_json_payload = False
        try:
            parsed_json = json.loads(sanitized_text)
            if isinstance(parsed_json, dict):
                is_json_payload = True
                if "service" in parsed_json:
                    detected_services.add(parsed_json["service"])
                if "correlationId" in parsed_json:
                    detected_correlation_ids.add(parsed_json["correlationId"])
                if "traceId" in parsed_json:
                    detected_correlation_ids.add(parsed_json["traceId"])
                if "exception" in parsed_json and isinstance(parsed_json["exception"], dict):
                    exc_info = parsed_json["exception"]
                    if "class" in exc_info:
                        detected_exceptions.append(exc_info["class"])
                    if "stackTrace" in exc_info and isinstance(exc_info["stackTrace"], list):
                        for st_entry in exc_info["stackTrace"]:
                            st_match = re.match(r'(?P<class>[A-Za-z0-9_\.$]+)\.(?P<method>[A-Za-z0-9_<>]+)\((?P<file>[A-Za-z0-9_\.]+):(?P<line>\d+)\)', st_entry)
                            if st_match:
                                stack_frames.append({
                                    "logLine": 1,
                                    "className": st_match.group("class"),
                                    "methodName": st_match.group("method"),
                                    "file": st_match.group("file"),
                                    "lineNumber": st_match.group("line")
                                })
                if "context" in parsed_json and isinstance(parsed_json["context"], dict):
                    ctx = parsed_json["context"]
                    if "targetEndpoint" in ctx:
                        url_ep = re.sub(r'^https?://[^/]+', '', ctx["targetEndpoint"])
                        if url_ep:
                            detected_endpoints.append({
                                "line": 1,
                                "method": "POST" if "allocate" in url_ep or "start" in url_ep else "GET",
                                "endpoint": url_ep,
                                "isDownstream": True
                            })
        except Exception:
            pass

        for idx, line in enumerate(lines, start=1):
            raw = line.strip()
            if not raw:
                continue

            # Check service name
            for svc in KNOWN_SERVICES:
                if svc.lower() in raw.lower():
                    detected_services.add(svc)

            # Check correlation ID
            c_match = CORRELATION_PATTERN.search(raw)
            if c_match:
                cid = c_match.group("id")
                detected_correlation_ids.add(cid)

            # Check HTTP method & endpoint (including full URLs like http://service:port/api/...)
            url_match = re.search(r'https?://[A-Za-z0-9\.\-:]+(?P<path>/[A-Za-z0-9_\-/]+)', raw)
            if url_match:
                url_path = url_match.group("path")
                if url_path not in [e["endpoint"] for e in detected_endpoints]:
                    detected_endpoints.append({
                        "line": idx,
                        "method": "POST" if "allocate" in url_path or "submit" in url_path or "start" in url_path else "GET",
                        "endpoint": url_path,
                        "isDownstream": True
                    })

            h_match = HTTP_PATTERN.search(raw)
            if h_match:
                m = h_match.group("method")
                ep = h_match.group("endpoint") or h_match.group("endpoint2")
                if ep and ep not in [e["endpoint"] for e in detected_endpoints]:
                    detected_endpoints.append({
                        "line": idx,
                        "method": m.upper() if m else "GET",
                        "endpoint": ep,
                        "isDownstream": False
                    })
                    if m:
                        detected_methods.append(m.upper())

            # Check status code
            s_match = STATUS_PATTERN.search(raw)
            if s_match:
                code = int(s_match.group("code"))
                if code not in detected_status_codes:
                    detected_status_codes.append(code)
                if code >= 400:
                    evidence_entries.append({
                        "line": idx,
                        "category": "HTTP_ERROR",
                        "detail": f"HTTP status code {code} detected in log line: {raw[:160]}"
                    })

            # Check exception
            e_match = EXCEPTION_PATTERN.search(raw)
            if e_match:
                full_exc = e_match.group("exc")
                simple_exc = full_exc.split(".")[-1]
                if simple_exc not in ["Exception", "Error"] and simple_exc not in detected_exceptions:
                    detected_exceptions.append(simple_exc)
                    evidence_entries.append({
                        "line": idx,
                        "category": "EXCEPTION",
                        "detail": f"Exception thrown: {simple_exc} ({full_exc}) - {raw[:180]}"
                    })
            elif "timeout" in raw.lower() or "timed out" in raw.lower():
                if "HttpTimeoutException" not in detected_exceptions and "DownstreamTimeoutException" not in detected_exceptions:
                    detected_exceptions.append("HttpTimeoutException")
                    if 504 not in detected_status_codes:
                        detected_status_codes.append(504)
                    evidence_entries.append({
                        "line": idx,
                        "category": "TIMEOUT",
                        "detail": f"Timeout detected: {raw[:160]}"
                    })

            # Check stack trace frames
            st_match = STACK_TRACE_FRAME.match(raw)
            if st_match:
                cls_name = st_match.group("class")
                meth_name = st_match.group("method")
                f_name = st_match.group("file")
                l_num = st_match.group("line")
                stack_frames.append({
                    "logLine": idx,
                    "className": cls_name,
                    "methodName": meth_name,
                    "file": f_name,
                    "lineNumber": l_num
                })
                # Check for project packages
                if "com.northstar" in cls_name or "c.n." in cls_name:
                    if len([e for e in evidence_entries if e.get("category") == "STACK_FRAME"]) < 3:
                        evidence_entries.append({
                            "line": idx,
                            "category": "STACK_FRAME",
                            "detail": f"Application stack frame in {cls_name}.{meth_name}() at {f_name}:{l_num}"
                        })

            # Check downstream timeouts / calls
            if "calling http" in raw.lower() or "downstream" in raw.lower() or "timed out after" in raw.lower():
                downstream_calls.append({
                    "line": idx,
                    "detail": raw[:180]
                })

        # Primary extracted attributes
        primary_endpoint = detected_endpoints[0]["endpoint"] if detected_endpoints else None
        primary_method = detected_endpoints[0]["method"] if detected_endpoints else "UNKNOWN"
        primary_service = list(detected_services)[0] if detected_services else None
        primary_status = detected_status_codes[0] if detected_status_codes else None
        primary_correlation = list(detected_correlation_ids)[0] if detected_correlation_ids else "NOT_FOUND"

        # 3. Match Repositories
        stack_packages = [f["className"] for f in stack_frames]
        endpoint_paths = [e["endpoint"] for e in detected_endpoints]
        repo_matches = match_repositories(
            service_name=primary_service,
            endpoints=endpoint_paths,
            stack_trace_packages=stack_packages
        )

        # 4. Confidence scoring calculation
        # Calculation method:
        # +0.25 for status code >= 400
        # +0.25 for extracted API endpoint
        # +0.25 for identified exception/stack trace
        # +0.15 for correlation ID
        # +0.10 for verified repository match
        score = 0.0
        if primary_status and primary_status >= 400:
            score += 0.25
        if primary_endpoint:
            score += 0.25
        if detected_exceptions or stack_frames:
            score += 0.25
        if primary_correlation != "NOT_FOUND":
            score += 0.15
        if repo_matches:
            score += 0.10

        score = round(min(score, 1.0), 2)
        if score >= 0.70:
            confidence_cat = "HIGH"
        elif score >= 0.40:
            confidence_cat = "MEDIUM"
        else:
            confidence_cat = "INCONCLUSIVE"

        # 5. Deterministic Findings Synthesis
        observed_facts = [
            f"Extracted {len(lines)} log lines across file {filename}.",
            f"Observed HTTP Status: {primary_status}" if primary_status else "No explicit HTTP error status code detected.",
            f"Identified API: {primary_method} {primary_endpoint}" if primary_endpoint else "No HTTP request endpoint path found.",
            f"Correlation ID: {primary_correlation}",
            f"Detected Exceptions: {', '.join(detected_exceptions)}" if detected_exceptions else "No explicit Java/Python exception signatures identified."
        ]

        evidence_hypotheses = []
        if detected_exceptions:
            evidence_hypotheses.append(
                f"Defect is directly correlated with {detected_exceptions[0]} during processing."
            )
        if downstream_calls:
            evidence_hypotheses.append(
                f"Downstream dependency latency/timeout contributed to failure: {downstream_calls[0]['detail'][:120]}"
            )

        unconfirmed_possibilities = [
            "Confounding intermittent network partition or packet loss during execution",
            "Concurrency race condition under multi-worker burst load"
        ]

        debugging_steps = [
            f"Examine application logs matching correlation ID '{primary_correlation}' in log aggregator.",
            f"Inspect endpoint handler for {primary_method} {primary_endpoint}." if primary_endpoint else "Verify originating API endpoint from client.",
            f"Review stack trace top frame: {stack_frames[0]['className']}.{stack_frames[0]['methodName']}" if stack_frames else "Reproduce using synthetic curl payload.",
            "Verify database connection pool and thread metrics around error timestamp."
        ]

        test_cases = [
            f"test_{primary_service or 'service'}_handlesErrorGracefully()",
            "test_downstreamTimeout_triggersCircuitBreakerFallback()"
        ]

        root_cause = "Inconclusive - insufficient diagnostic telemetry."
        if score >= 0.40:
            if detected_exceptions:
                root_cause = f"Failure triggered by {detected_exceptions[0]}"
                if stack_frames:
                    root_cause += f" at {stack_frames[0]['className']}.{stack_frames[0]['methodName']}():{stack_frames[0]['lineNumber']}"
            elif primary_status == 504:
                root_cause = "Downstream timeout: target service failed to respond within configured SLA boundary."
            elif primary_status == 409:
                root_cause = "Resource conflict: duplicate synthetic entity identifier detected during reservation."
            elif primary_status == 401:
                root_cause = "Security credential rejected: expired or invalid token on ingress gateway."
            elif primary_status == 400:
                root_cause = "Client schema mismatch: request payload failed validation constraints."
            else:
                root_cause = f"System error resulting in HTTP {primary_status}."

        limitations = "Findings generated deterministically from provided synthetic log excerpt. Full upstream request payloads were not verified."

        # 6. Optional NVIDIA LLM Contextual Reasoning
        nvidia_used = False
        if get_nvidia_status()["enabled"]:
            llm_result = await analyze_with_nvidia(
                sanitized_logs=sanitized_text,
                context_metadata={
                    "service": primary_service,
                    "endpoint": primary_endpoint,
                    "statusCode": primary_status,
                    "correlationId": primary_correlation
                }
            )
            if llm_result:
                nvidia_used = True
                root_cause = llm_result.get("probableRootCause", root_cause)
                score = round(float(llm_result.get("confidenceScore", score)), 2)
                observed_facts = llm_result.get("observedFacts", observed_facts)
                evidence_hypotheses = llm_result.get("evidenceHypotheses", evidence_hypotheses)
                unconfirmed_possibilities = llm_result.get("unconfirmedPossibilities", unconfirmed_possibilities)
                debugging_steps = llm_result.get("recommendedDebuggingSteps", debugging_steps)
                test_cases = llm_result.get("suggestedTestCases", test_cases)
                limitations = llm_result.get("limitations", limitations)

        return {
            "analysisId": analysis_id,
            "ticketKey": ticket_key,
            "filename": filename,
            "status": "COMPLETED",
            "isComplete": score >= 0.40,
            "summary": f"Investigation of {filename} ({line_count} lines) for ticket {ticket_key}.",
            "primaryService": primary_service or "Unknown Service",
            "primaryEndpoint": f"{primary_method} {primary_endpoint}" if primary_endpoint else "Unknown Endpoint",
            "primaryStatus": primary_status,
            "correlationId": primary_correlation,
            "probableRootCause": root_cause,
            "confidenceScore": score,
            "confidenceCategory": confidence_cat,
            "observedFacts": observed_facts,
            "evidenceHypotheses": evidence_hypotheses,
            "unconfirmedPossibilities": unconfirmed_possibilities,
            "recommendedDebuggingSteps": debugging_steps,
            "suggestedTestCases": test_cases,
            "limitations": limitations,
            "evidence": evidence_entries,
            "endpoints": detected_endpoints,
            "services": list(detected_services),
            "exceptions": detected_exceptions,
            "stackFrames": stack_frames[:10],
            "repositoryMatches": repo_matches,
            "redactionCounts": redaction_counts,
            "quarantined": False,
            "createdAt": created_at,
            "nvidiaUsed": nvidia_used
        }
