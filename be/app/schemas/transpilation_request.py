from typing import Literal
from app.schemas.generation import BackendInfo
from pydantic import BaseModel, ConfigDict, Field, PositiveInt

class TranspilationRequest(BaseModel):
    filename : str
    code: str
    backends: list[BackendInfo] = Field(min_length=1)

