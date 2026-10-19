from app.quantum.Folders import Folders
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import executions, generation
from app.quantum.backends import initialize_backends, get_all_backends
from app.api import executions
from app.api import generation
from app.api import executions, generation, transpilation

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_backends()
    backends = get_all_backends()
    Folders().create(backends, False)
    yield

app = FastAPI(title="Westeaker API", version="0.1.0", lifespan=lifespan)

origins = [ "http://localhost:4200" ]


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

app.include_router(transpilation.router, prefix="/api/transpilation", tags=["Transpilation"])

@app.get("/api/health")
def health():
    return {
        "status": "ok"
    }