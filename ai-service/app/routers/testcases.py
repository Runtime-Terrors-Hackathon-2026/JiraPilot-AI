from fastapi import APIRouter
from app.models.schemas import TestCaseRequest, TestCaseResponse
from app.services.testcase_engine import generate_test_cases

router = APIRouter(prefix="/analyze", tags=["TestCases"])

@router.post("/test-cases", response_model=TestCaseResponse)
async def create_test_cases(req: TestCaseRequest):
    return generate_test_cases(req.ticket, req.affectedApi, req.rootCause)
