from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, PositiveInt

class GroverRequest(BaseModel):
    qubits: list[PositiveInt] = Field(min_length=1)
    markable_values: list[int] = Field(default_factory=list)
    backends: list[str] | None = None
    searched_values: list[list[int]] = Field(default_factory=list)
    default_values: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "qubits": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                "markable_values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                "backends": ["aer_simulator"],
                "searched_values": [[3], [4], [3, 4, 5]],
                "default_values" : False
            }
        }
    )