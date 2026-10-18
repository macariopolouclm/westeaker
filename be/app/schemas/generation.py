from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, PositiveInt

class BackendInfo(BaseModel):
    name: str
    num_qubits : int

class GroverRequest(BaseModel):
    backends: list[BackendInfo] = Field(default_factory=list)
    qubits: list[PositiveInt] = Field(min_length=1)
    markable_values: list[int] = Field(default_factory=list)
    searched_values: list[list[int]] = Field(default_factory=list)
    default_values: bool = False
    repetitions: int = Field(default=10, gt=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "qubits": [4],
                "markable_values": [5],
                "backends": ["aer_simulator", "simulator"],
                "searched_values": [[5]],
                "default_values" : False,
                "repetitions": 1
            }
        }
    )