"""
Confidentiality & Secret Scanner for JiraPilot AI (Northstar Digital Systems)

DISCLAIMER & LIMITATION OF AUTOMATION:
Automated scanning cannot guarantee that all confidential information, secrets,
or proprietary references have been removed. This tool provides static regex and
keyword heuristics for pre-commit / CI verification and flags candidate strings
for mandatory human peer review.
"""

import os
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# File patterns to exclude
EXCLUDE_DIRS = {
    ".git", ".idea", "node_modules", "target", ".venv", "venv",
    "__pycache__", ".pytest_cache", ".system_generated", "dist", "build"
}

EXCLUDE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".ico", ".svg", ".jar", ".class", ".zip", ".tar", ".gz"
}

# Regex patterns for high-entropy secrets and credential formats
SECRET_PATTERNS = [
    (r"(?i)aws_secret_access_key\s*=\s*['\"][A-Za-z0-9/+=]{40}['\"]", "AWS Secret Key"),
    (r"(?i)-----BEGIN\s+PRIVATE\s+KEY-----", "Unencrypted Private Key Block"),
    (r"(?i)ghp_[A-Za-z0-9]{36}", "GitHub Personal Access Token"),
    (r"(?i)xox[baprs]-[0-9]{10,12}-[A-Za-z0-9]{24,32}", "Slack API Token"),
    (r"(?i)(password|passwd|secret)\s*[:=]\s*['\"][^'\"]{8,}['\"]", "Hardcoded Password/Secret Assignment"),
]

# Sensitive corporate terms that must NOT appear in this public-safe fictional repository
DISALLOWED_TERMS = [
    r"\bverizon\b",
    r"\bvzwireless\b",
    r"\bonefib(er)?\b",
]

def scan_file(file_path: Path):
    issues = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return [f"Unable to read file: {e}"]

    # Check for secret patterns
    for pattern, label in SECRET_PATTERNS:
        matches = re.finditer(pattern, content)
        for m in matches:
            # Check if this is a known safe example in docs or tests
            matched_str = m.group(0)
            if "example" in matched_str.lower() or "synthetic" in matched_str.lower() or "demo" in matched_str.lower():
                continue
            line_no = content[:m.start()].count("\n") + 1
            issues.append(f"[CRITICAL SECRET] Line {line_no}: Found potential {label}")

    # Check for disallowed corporate terms (strictly public-safe check)
    for pattern in DISALLOWED_TERMS:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for m in matches:
            line_no = content[:m.start()].count("\n") + 1
            # Check context to avoid false positives if mentioned in negative prohibition instructions
            line_text = content.splitlines()[line_no - 1]
            if "never use" in line_text.lower() or "do not" in line_text.lower() or "no verizon" in line_text.lower():
                continue
            issues.append(f"[CONFIDENTIALITY WARNING] Line {line_no}: Disallowed term match: '{m.group(0)}'")

    return issues

def scan_repository():
    print("=" * 70)
    print(" Northstar Digital Systems - Confidentiality & Secret Scanner")
    print("=" * 70)
    print("Running static analysis across workspace...")
    print("NOTE: Automated scanning cannot guarantee that all confidential")
    print("information has been eliminated. Human review is required.")
    print("-" * 70)

    total_scanned = 0
    total_violations = 0

    for root, dirs, files in os.walk(BASE_DIR):
        # Prune excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in EXCLUDE_EXTENSIONS:
                continue

            rel_path = file_path.relative_to(BASE_DIR)
            # Skip this scanner script itself when scanning for banned regex terms
            if str(rel_path).replace("\\", "/") == "scripts/scan_secrets_and_compliance.py":
                continue

            total_scanned += 1
            file_issues = scan_file(file_path)
            if file_issues:
                print(f"\n[FILE] {rel_path}")
                for issue in file_issues:
                    print(f"  --> {issue}")
                    total_violations += 1

    print("\n" + "=" * 70)
    print(f"Scan complete. Total files evaluated: {total_scanned}")
    print(f"Violations detected: {total_violations}")
    print("=" * 70)

    if total_violations > 0:
        print("[FAIL] Repository compliance check failed. Address flags above.")
        return False
    else:
        print("[PASS] Repository check passed. No hardcoded secrets or disallowed terms found.")
        return True

if __name__ == "__main__":
    success = scan_repository()
    sys.exit(0 if success else 1)
