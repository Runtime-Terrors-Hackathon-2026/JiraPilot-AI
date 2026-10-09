"""
Secret Redaction and Quarantine Engine for JiraPilot AI (Northstar Digital Systems)
Sanitizes raw log telemetry, masks credentials, tokens, cookies, and sensitive headers,
and quarantines logs containing unredactable real private keys or proprietary patterns.
"""

import re
from typing import Tuple, List, Dict

# Regex patterns for credential masking
REDACTION_RULES = [
    # Authorization headers & Bearer tokens
    (r'(?i)(Authorization:\s*Bearer\s+)[A-Za-z0-9_\-\.]{15,}', r'\1[REDACTED_TOKEN]'),
    (r'(?i)(Authorization:\s*Basic\s+)[A-Za-z0-9+/=]{10,}', r'\1[REDACTED_BASIC_AUTH]'),
    (r'(?i)(bearer\s+)eyJ[A-Za-z0-9_\-\.]{20,}', r'\1[REDACTED_JWT]'),
    (r'(?i)eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}', r'[REDACTED_JWT]'),
    
    # Generic API Keys and tokens
    (r'(?i)(api[_-]?key|access[_-]?token|secret[_-]?key|client[_-]?secret|auth[_-]?token)\s*[:=]\s*["\']?[A-Za-z0-9_\-\.]{12,}["\']?', r'\1=[REDACTED_KEY]'),
    (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?[^"\',\s]{6,}["\']?', r'\1=[REDACTED_PASSWORD]'),
    
    # Cookies & Session tokens
    (r'(?i)(Set-Cookie:\s*[^=;]+)=[^;\r\n]+', r'\1=[REDACTED_COOKIE]'),
    (r'(?i)(Cookie:\s*[^=;]+)=[^;\r\n]+', r'\1=[REDACTED_COOKIE]'),
    (r'(?i)(JSESSIONID|PHPSESSID|session_id|sid)=([A-Za-z0-9_\-\.]{16,})', r'\1=[REDACTED_SESSION]'),
    
    # Cloud provider keys
    (r'(?i)AKIA[0-9A-Z]{16}', r'[REDACTED_AWS_KEY_ID]'),
    (r'(?i)ghp_[A-Za-z0-9]{36}', r'[REDACTED_GITHUB_TOKEN]'),
    (r'(?i)xox[baprs]-[0-9]{10,12}-[A-Za-z0-9]{24,32}', r'[REDACTED_SLACK_TOKEN]'),
    
    # Sensitive URL parameters
    (r'(?i)(\?|&)(key|token|api_key|secret|password)=([^&\s]+)', r'\1\2=[REDACTED_PARAM]')
]

# Patterns that trigger quarantine (do NOT send to external AI even with redaction)
QUARANTINE_PATTERNS = [
    (r'(?i)-----BEGIN\s+(RSA|EC|DSA|OPENSSH)?\s*PRIVATE\s+KEY-----', "Unencrypted Private Key Block Detected"),
    (r'(?i)-----BEGIN\s+CERTIFICATE-----.*-----END\s+CERTIFICATE-----', "Raw Public/Private Certificate Pair"),
]

def sanitize_and_redact(log_text: str) -> Tuple[str, bool, List[str], Dict[str, int]]:
    """
    Sanitizes log text by applying redaction patterns.
    Returns:
        sanitized_text: The log content with sensitive values replaced by placeholders.
        quarantine_required: True if content contains unmaskable secrets (e.g. private key blocks).
        quarantine_reasons: List of reasons if quarantined.
        redaction_counts: Breakdown of redacted items by category.
    """
    if not log_text:
        return "", False, [], {}

    quarantine_required = False
    quarantine_reasons = []
    
    # 1. Check quarantine rules
    for q_pattern, q_reason in QUARANTINE_PATTERNS:
        if re.search(q_pattern, log_text, re.DOTALL):
            quarantine_required = True
            quarantine_reasons.append(q_reason)

    # 2. Apply redactions line by line
    sanitized_text = log_text
    redaction_counts = {}

    for pattern, replacement in REDACTION_RULES:
        matches = len(re.findall(pattern, sanitized_text))
        if matches > 0:
            sanitized_text = re.sub(pattern, replacement, sanitized_text)
            category = replacement.strip('[]')
            redaction_counts[category] = redaction_counts.get(category, 0) + matches

    return sanitized_text, quarantine_required, quarantine_reasons, redaction_counts
