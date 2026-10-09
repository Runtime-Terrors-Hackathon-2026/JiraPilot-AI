# JiraPilot AI — Repository Discovery & Matching

## 1. Approved Synthetic Repositories

In accordance with our strict confidentiality policy for Northstar Digital Systems, JiraPilot AI matches failure evidence **only** against approved synthetic repositories registered in `demo-data/repositories.json`. No proprietary, internal, or invented ad-hoc repository URLs are produced.

### Catalog of Approved Repositories:
1. **service-request-api**
   - Service ID: `service-request-api`
   - Group: Service Operations Group
   - Repository: `https://github.com/northstar-labs/service-request-api.git`
   - Default Branch: `main`
   - Primary Paths: `/api/v1/requests`, `/api/v1/requests/{id}`
   - Code Package: `com.northstar.servicerequest`

2. **workflow-orchestrator**
   - Service ID: `workflow-orchestrator`
   - Group: Service Operations Group
   - Repository: `https://github.com/northstar-labs/workflow-orchestrator.git`
   - Default Branch: `main`
   - Primary Paths: `/api/v1/workflows`, `/api/v1/workflows/{id}/execute`
   - Code Package: `com.northstar.workflow`

3. **request-validation-engine**
   - Service ID: `request-validation-engine`
   - Group: Service Operations Group
   - Repository: `https://github.com/northstar-labs/request-validation-engine.git`
   - Default Branch: `main`
   - Primary Paths: `/api/v1/validate`
   - Code Package: `com.northstar.validation`

4. **resource-inventory-service**
   - Service ID: `resource-inventory-service`
   - Group: Network Resource Group
   - Repository: `https://github.com/northstar-labs/resource-inventory-service.git`
   - Default Branch: `main`
   - Primary Paths: `/api/v1/resources`, `/api/v1/resources/allocate`
   - Code Package: `com.northstar.resource`

5. **capacity-planning-api**
   - Service ID: `capacity-planning-api`
   - Group: Network Resource Group
   - Repository: `https://github.com/northstar-labs/capacity-planning-api.git`
   - Default Branch: `main`
   - Primary Paths: `/api/v1/capacity/check`, `/api/v1/capacity/reserve`
   - Code Package: `com.northstar.capacity`

6. **topology-registry**
   - Service ID: `topology-registry`
   - Group: Network Resource Group
   - Repository: `https://github.com/northstar-labs/topology-registry.git`
   - Default Branch: `main`
   - Primary Paths: `/api/v1/topology/nodes`, `/api/v1/topology/routes`
   - Code Package: `com.northstar.topology`

7. **integration-gateway**
   - Service ID: `integration-gateway`
   - Group: Integration Platform Group
   - Repository: `https://github.com/northstar-labs/integration-gateway.git`
   - Default Branch: `main`
   - Primary Paths: `/gateway/v1/dispatch`, `/gateway/v1/routes`
   - Code Package: `com.northstar.gateway`

---

## 2. Multi-Signal Matching Strategy

When an incident or attachment is analyzed, the Repository Matcher (`ai-service/app/services/repository_matcher.py`) evaluates multiple evidence vectors:
1. **Explicit Service Identifier**: Direct mention of `service-name` in log headers or ticket metadata. (Weight: 45)
2. **API Endpoint Route Match**: Substring or prefix match on registered API endpoints (e.g. `/api/v1/resources/allocate`). (Weight: 35)
3. **Java Package / Stack Trace Match**: Class or package paths in exception stack traces (e.g. `com.northstar.resource.service.AllocationService`). (Weight: 25)
4. **Keyword & Symptom Match**: Component domain keywords (e.g. `inventory`, `allocation`, `gateway`). (Weight: 15)

---

## 3. Clone Commands Generation

Once the repository is identified, JiraPilot AI generates copyable shell commands ready for engineers to inspect the code locally:

```bash
# Clone default branch
git clone https://github.com/northstar-labs/resource-inventory-service.git

# Clone explicitly referencing main branch
git clone --branch main https://github.com/northstar-labs/resource-inventory-service.git
```

These clone commands are surfaced in the React Dashboard investigation card and formatted into the Jira issue markdown comments.
