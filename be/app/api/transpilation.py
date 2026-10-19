from app.schemas.transpilation_request import TranspilationRequest
from fastapi import APIRouter, HTTPException
from app.services.transpilation_service import TranspilationService

router = APIRouter()
transpilation_service = TranspilationService()
@router.post("/transpile")
def transpile(request: TranspilationRequest):
    try:
        return transpilation_service.transpile(request.filename, request.code, request.backends)
    except ValueError as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    except Exception as exception:
        raise HTTPException(status_code=500, detail=str(exception))