import json
from app.models.schemas import TicketPayload, ApiFinding, ReproductionResponse

def generate_reproduction(ticket: TicketPayload, api_finding: ApiFinding = None) -> ReproductionResponse:
    method = (api_finding.method if api_finding else "POST").upper()
    endpoint = api_finding.endpoint if api_finding else "/api/circuit/provision"
    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint

    host = "http://localhost:8080"
    url = f"{host}{endpoint}"

    # Generate synthetic safe payload
    sample_payload = {
        "circuitId": "TEST-CKT-1001",
        "customerId": "TEST-CUST-8821",
        "nfid": "TEST-NFID-1001",
        "environment": "SANDBOX",
        "region": "US-EAST",
        "bandwidthMbps": 1000,
        "provisioningType": "STANDARD"
    }

    if ticket.requestPayload:
        try:
            parsed = json.loads(ticket.requestPayload)
            if isinstance(parsed, dict):
                # Sanitize keys with synthetic values
                for k, v in parsed.items():
                    if "id" in k.lower():
                        sample_payload[k] = f"TEST-{v}" if not str(v).startswith("TEST-") else v
                    else:
                        sample_payload[k] = v
        except Exception:
            pass

    payload_str = json.dumps(sample_payload, indent=2)

    # curl command
    if method in ("POST", "PUT", "PATCH"):
        curl_cmd = (
            f"curl -X {method} \"{url}\" \\\n"
            f"  -H \"Content-Type: application/json\" \\\n"
            f"  -H \"X-Correlation-ID: CORR-TEST-1001\" \\\n"
            f"  -d '{payload_str}'"
        )
    else:
        curl_cmd = (
            f"curl -X {method} \"{url}\" \\\n"
            f"  -H \"Accept: application/json\" \\\n"
            f"  -H \"X-Correlation-ID: CORR-TEST-1001\""
        )

    # Postman format
    postman = {
        "info": {
            "name": f"Reproduction - {ticket.key or 'HACK-INCIDENT'}",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [
            {
                "name": f"{method} {endpoint}",
                "request": {
                    "method": method,
                    "header": [
                        {"key": "Content-Type", "value": "application/json"},
                        {"key": "X-Correlation-ID", "value": "CORR-TEST-1001"}
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": payload_str,
                        "options": {"raw": {"language": "json"}}
                    },
                    "url": {
                        "raw": url,
                        "protocol": "http",
                        "host": ["localhost"],
                        "port": "8080",
                        "path": endpoint.strip("/").split("/")
                    }
                }
            }
        ]
    }

    # Python snippet
    py_snippet = (
        f"import requests\n\n"
        f"url = \"{url}\"\n"
        f"headers = {{\n"
        f"    \"Content-Type\": \"application/json\",\n"
        f"    \"X-Correlation-ID\": \"CORR-TEST-1001\"\n"
        f"}}\n"
        f"payload = {payload_str}\n\n"
        f"response = requests.{method.lower()}(url, json=payload, headers=headers)\n"
        f"print(f\"Status: {{response.status_code}}\")\n"
        f"print(response.json() if response.content else response.text)\n"
    )

    return ReproductionResponse(
        curlCommand=curl_cmd,
        postmanPayload=postman,
        pythonRequestSnippet=py_snippet
    )
