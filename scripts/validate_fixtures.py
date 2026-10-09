"""
Fixture and Schema Validation Script for JiraPilot AI (Northstar Digital Systems)
Validates all demo-data JSON fixtures against formal schemas in schemas/.
"""

import sys
import json
from pathlib import Path
import jsonschema

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = BASE_DIR / "schemas"
DEMO_DATA_DIR = BASE_DIR / "demo-data"

def load_json(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_service_catalog():
    schema_path = SCHEMAS_DIR / "service-catalog.schema.json"
    data_path = DEMO_DATA_DIR / "service-catalog.json"
    
    schema = load_json(schema_path)
    data = load_json(data_path)
    
    jsonschema.validate(instance=data, schema=schema)
    print(f"[PASS] Service catalog validated successfully: {data_path.name}")
    print(f"       Organization: {data.get('organization')}, Groups: {len(data.get('groups', []))}")

def validate_incidents():
    schema_path = SCHEMAS_DIR / "incident-record.schema.json"
    data_path = DEMO_DATA_DIR / "incidents.json"
    
    schema = load_json(schema_path)
    incidents = load_json(data_path)
    
    assert isinstance(incidents, list), "Incidents fixture must be a list"
    assert len(incidents) >= 20, f"Expected >= 20 incidents, found {len(incidents)}"
    
    for idx, inc in enumerate(incidents):
        try:
            jsonschema.validate(instance=inc, schema=schema)
        except jsonschema.ValidationError as e:
            print(f"[FAIL] Incident #{idx} ({inc.get('ticketKey', 'Unknown')}) failed validation: {e.message}")
            raise e
            
    print(f"[PASS] Synthetic incidents validated successfully: {len(incidents)} records checked in {data_path.name}")

def validate_repositories():
    schema_path = SCHEMAS_DIR / "repository-catalog.schema.json"
    data_path = DEMO_DATA_DIR / "repositories.json"
    
    schema = load_json(schema_path)
    data = load_json(data_path)
    
    assert isinstance(data, list), "Repositories catalog must be a list"
    assert len(data) >= 6, f"Expected >= 6 repositories, found {len(data)}"
    
    jsonschema.validate(instance=data, schema=schema)
    print(f"[PASS] Repository catalog validated successfully: {len(data)} repositories checked in {data_path.name}")

def main():
    print("=" * 60)
    print(" Northstar Digital Systems - Fixture Validation Suite")
    print("=" * 60)
    try:
        validate_service_catalog()
        validate_incidents()
        validate_repositories()
        print("=" * 60)
        print("All fixtures passed schema validation cleanly!")
        print("=" * 60)
    except Exception as e:
        print(f"[ERROR] Validation failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
