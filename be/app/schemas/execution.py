from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

class GroverExecutionRequest(BaseModel):
    backends: list[str] = Field(default_factory=lambda: ["aer_simulator"])
    qubits: list[int] = Field(min_length=1)
    searched_values: list[int] = Field(min_length=1)
    shots: list[int] = [ 1024 ]
    transpiled_firsts: list[Literal["oracle", "diffuser"]] = Field(
        min_length=1,
        max_length=3
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "qubits": [4, 5, 6],
                "searched_values": [5],
                "shots": [ 1024, 2048],
                "backends": ["aer_simulator"],
                "transpiled_firsts" : ["oracle", "diffuser"]
            }
        }
    )