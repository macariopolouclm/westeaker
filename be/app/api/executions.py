from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from typing import Literal

from app.schemas.execution import GroverExecutionRequest
from app.schemas.execution_file_request import ExecuteFileRequest
from app.services.grover_execution_service import GroverExecutionService


router = APIRouter()

grover_execution_service = GroverExecutionService()


@router.post("/execute")
def execute_grover(request: GroverExecutionRequest):
    try:
        return grover_execution_service.execute(
            qubits=request.qubits,
            searched_values=request.searched_values,
            backend_names=request.backends,
            shots=request.shots,
            transpiled_firsts = request.transpiled_firsts
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/executeFile")
def execute_file(request: ExecuteFileRequest):
    try:
        return grover_execution_service.execute_file(
            backend_name=request.backend,
            filename=request.filename,
            origin=request.origin,
            searched_values=request.searched_values,
            shots=request.shots
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))



@router.get("/configurations")
def get_configurations():
    return grover_execution_service.get_configurations()


@router.get("/source", response_class=PlainTextResponse)
def get_source(backend: str, filename: str, origin: Literal["composed_grovers", "whole_grovers"]):
    try:
        return grover_execution_service.get_source(backend, filename, origin)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))