import re
from typing import List, Dict
from app.models.schemas import ParsedLogEntry, LogParseResponse

LOG_PATTERN = re.compile(
    r'(?P<timestamp>\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d{3,6})?(?:Z|[+-]\d{2}:?\d{2})?)?\s*'
    r'(?:\[?(?P<level>FATAL|ERROR|WARN|WARNING|INFO|DEBUG|TRACE)\]?)?\s*'
    r'(?:\[(?P<service>[A-Za-z0-9_\-]+)\])?\s*'
    r'(?P<message>.*)',
    re.IGNORECASE
)

CORRELATION_PATTERN = re.compile(
    r'(?:correlationId|requestId|traceId|corr_id|x-correlation-id)[=:\s]+([A-Za-z0-9_\-]+)',
    re.IGNORECASE
)

HTTP_PATTERN = re.compile(
    r'(?:(?P<method>GET|POST|PUT|DELETE|PATCH)\s+(?P<endpoint>/[^\s,;"\']+))|(?:endpoint=(?P<endpoint2>/[^\s,;"\']+))',
    re.IGNORECASE
)

STATUS_PATTERN = re.compile(
    r'(?:status(?:Code)?|HTTP|code)[=:\s]+(?P<code>[1-5]\d{2})',
    re.IGNORECASE
)

EXCEPTION_PATTERN = re.compile(
    r'(?:Exception|Error|Throwable):?\s*([A-Za-z0-9_\.]+Exception|[A-Za-z0-9_\.]+Error)',
    re.IGNORECASE
)

def parse_logs(log_text: str) -> LogParseResponse:
    if not log_text or not log_text.strip():
        return LogParseResponse(
            entries=[],
            correlatedIdGroups={},
            detectedServices=[],
            detectedExceptions=[],
            detectedEndpoints=[],
            probableErrorSummary="No logs provided."
        )

    lines = log_text.strip().splitlines()
    entries: List[ParsedLogEntry] = []
    detected_services = set()
    detected_exceptions = set()
    detected_endpoints = set()
    corr_groups: Dict[str, List[ParsedLogEntry]] = {}

    for line in lines:
        raw = line.strip()
        if not raw:
            continue

        match = LOG_PATTERN.match(raw)
        timestamp = match.group("timestamp") if match else None
        level = (match.group("level") or "INFO").upper() if match else "INFO"
        service = match.group("service") if match else None
        message = match.group("message") if match else raw

        # Fallback service extraction if not bracketed
        if not service:
            svc_match = re.search(r'\b(PEDS|WFM|CIRCUIT[-_]SVC|GATEWAY|INVENTORY|NTLS|AUTH[-_]SVC)\b', raw, re.IGNORECASE)
            if svc_match:
                service = svc_match.group(1).upper()

        if service:
            detected_services.add(service)

        # Correlation ID
        corr_match = CORRELATION_PATTERN.search(raw)
        corr_id = corr_match.group(1) if corr_match else None

        # HTTP method and endpoint
        http_match = HTTP_PATTERN.search(raw)
        method = http_match.group("method").upper() if (http_match and http_match.group("method")) else None
        endpoint = None
        if http_match:
            endpoint = http_match.group("endpoint") or http_match.group("endpoint2")
            if endpoint:
                detected_endpoints.add(endpoint)

        # Status code
        status_match = STATUS_PATTERN.search(raw)
        status_code = int(status_match.group("code")) if status_match else None

        # Exception
        exc_match = EXCEPTION_PATTERN.search(raw)
        exc_class = None
        if exc_match:
            exc_class = exc_match.group(1)
            detected_exceptions.add(exc_class)
        elif "Duplicate NFID" in raw:
            exc_class = "DuplicateNfidException"
            detected_exceptions.add(exc_class)
        elif "timeout" in raw.lower() or "timed out" in raw.lower():
            exc_class = "DownstreamTimeoutException"
            detected_exceptions.add(exc_class)
        elif "NullPointer" in raw:
            exc_class = "NullPointerException"
            detected_exceptions.add(exc_class)

        entry = ParsedLogEntry(
            timestamp=timestamp,
            logLevel=level,
            serviceName=service,
            correlationId=corr_id,
            httpMethod=method,
            endpoint=endpoint,
            statusCode=status_code,
            exceptionClass=exc_class,
            message=message,
            rawLine=raw
        )
        entries.append(entry)

        if corr_id:
            if corr_id not in corr_groups:
                corr_groups[corr_id] = []
            corr_groups[corr_id].append(entry)

    # Summary
    errors = [e for e in entries if e.logLevel in ("ERROR", "FATAL") or e.exceptionClass]
    if errors:
        first_err = errors[0]
        probable_summary = f"{first_err.serviceName or 'Service'} reported {first_err.exceptionClass or 'Error'}: {first_err.message[:120]}"
    else:
        probable_summary = "Logs analyzed with no critical errors detected."

    return LogParseResponse(
        entries=entries,
        correlatedIdGroups=corr_groups,
        detectedServices=list(detected_services),
        detectedExceptions=list(detected_exceptions),
        detectedEndpoints=list(detected_endpoints),
        probableErrorSummary=probable_summary
    )
