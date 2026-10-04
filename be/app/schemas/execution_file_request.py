from typing import Literal

from pydantic import BaseModel, Field

class ExecuteFileRequest(BaseModel):
    backend: str
    filename: str
    origin: Literal["composed_grovers", "whole_grovers"]
    searched_values: list[int]
    shots: int = Field(default=1024, gt=0)