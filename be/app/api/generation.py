from pathlib import Path


from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.generation import GroverRequest
from app.services.grover_service import GroverGeneratorService
from app.quantum.Folders import Folders

router = APIRouter()

grover_generator_service = GroverGeneratorService()

@router.post("/generate")
def generate_fragments(request: GroverRequest):
    try:
        return grover_generator_service.generate_fragments(
            qubits=request.qubits, 
            backend_names=request.backends,
            markable_values=request.markable_values, 
            searched_values = request.searched_values,
            default_values = request.default_values
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/results")
def get_results():
    folders = Folders()

    results_file = Path(folders.root_folder) / "results.tsv"

    if not results_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {results_file}"
        )

    return FileResponse(
        path=results_file,
        media_type="text/tab-separated-values",
        filename="results.tsv"
    )