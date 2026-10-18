from dataclasses import dataclass, field
from typing import Any

@dataclass
class BackendWrapper:
    backend: Any
    provider: str
    noise_model: str | None = None
    name: str = field(init=False)

    def __post_init__(self):
        self.name = f"{self.backend.name}_{self.noise_model}" if self.noise_model is not None else self.backend.name
        if self.noise_model is not None:
            self.backend.set_options(noise_model=self.noise_model)

    @property
    def backend_name(self) -> str:
        return self.backend.name
    
    @property
    def num_qubits(self) -> int | None:
        return getattr(self.backend, "num_qubits", None)