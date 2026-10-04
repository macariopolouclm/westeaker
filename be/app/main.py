from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import executions
from app.api import generation


app = FastAPI(title="Westeaker API", version="0.1.0")

origins = [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    generation.router, 
    prefix="/api/generation", 
    tags=["Generation"]
)

app.include_router(
    executions.router,
    prefix="/api/executions",
    tags=["Executions"]
)

@app.get("/api/health")
def health():
    return {
        "status": "ok"
    }