import re
from pathlib import Path

from app.quantum.Folders import Folders

from app.quantum.backends import create_backends
from app.quantum.grover_executor import GroverExecutor


class GroverExecutionService:

    def execute(self, qubits: list[int], searched_values: list[int], backend_names: list[str] | None = None,
            shots: list[int] = [1024], transpiled_firsts : list[str] | None = None):

        backends = create_backends(backend_names)

        executor = GroverExecutor()
        for current_shots in shots:
            for current_qubits in qubits:
                for transpiled_first in transpiled_firsts:
                    for backend in backends:
                        executor.execute_from_fragments(backend=backend, qubits=current_qubits, 
                            searched_values=searched_values, shots=current_shots, transpiled_first = transpiled_first)

                    executor.execute_whole(backend=backend, qubits=current_qubits, 
                            searched_values=searched_values, shots=current_shots)

        return {
            "qubits": qubits, "searched_values": searched_values, 
            "backends": [backend.name for backend in backends],
            "status": "completed"
        }

    def execute_file(self, backend_name: str, filename: str, origin: str,
                 searched_values: list[int], shots: int = 1024):

        backends = create_backends([backend_name])
        if not backends:
            raise ValueError(f"Backend not found: {backend_name}")
        
        backend = backends[0]
        executor = GroverExecutor()

        return executor.execute_file(
            backend=backend,
            filename=filename,
            origin=origin,
            searched_values=searched_values,
            shots=shots
        )

    def _validate(self, qubits: int, values: list[int], shots):
        max_value = 2 ** qubits - 1

        invalid_values = [
            value
            for value in values
            if value < 0 or value > max_value
        ]

        if invalid_values:
            raise ValueError(f"Values {invalid_values} cannot be represented with {qubits} qubits")

        if len(values) != len(set(values)):
            raise ValueError("searched_values cannot contain duplicates")

        if isinstance(shots, int) and shots <= 0:
            raise ValueError("shots must be greater than 0")

        if isinstance(shots, list) and any(value <= 0 for value in shots):
            raise ValueError("all shots values must be greater than 0")

    def get_configurations(self):
        root_folder = Path(Folders().root_folder)

        composed_grovers_folder = root_folder / "composed_grovers"
        whole_grovers_folder = root_folder / "whole_grovers"

        configurations = []

        composed_pattern = re.compile(r"^grover_(h|oracle|diffuser)_(\d+)_(.+)$")
        whole_pattern = re.compile(r"^grover_whole_(\d+)_(.+)\.py$")

        # Grovers construidos a partir de fragmentos
        if composed_grovers_folder.exists():
            for backend_folder in composed_grovers_folder.iterdir():
                if not backend_folder.is_dir() or backend_folder.name == "high_level":
                    continue

                for configuration_folder in backend_folder.iterdir():
                    if not configuration_folder.is_dir():
                        continue

                    match = composed_pattern.match(configuration_folder.name)

                    if not match:
                        continue

                    python_filename = configuration_folder / f"{configuration_folder.name}.py"

                    if not python_filename.exists():
                        continue

                    configurations.append({
                        "backend": backend_folder.name,
                        "filename": python_filename.name,
                        "origin": "composed_grovers",
                        "transpiled_first": match.group(1),
                        "qubits": int(match.group(2)),
                        "searched_values": [int(value) for value in match.group(3).split("_")]
                    })

        # Grovers completos
        if whole_grovers_folder.exists():
            for backend_folder in whole_grovers_folder.iterdir():
                if not backend_folder.is_dir() or backend_folder.name == "high_level":
                    continue

                for python_filename in backend_folder.glob("*.py"):
                    match = whole_pattern.match(python_filename.name)

                    if not match:
                        continue

                    configurations.append({
                        "backend": backend_folder.name,
                        "filename": python_filename.name,
                        "origin": "whole_grovers",
                        "transpiled_first": "Whole grover",
                        "qubits": int(match.group(1)),
                        "searched_values": [int(value) for value in match.group(2).split("_")]
                    })

        configurations.sort(
            key=lambda configuration: (
                configuration["backend"],
                configuration["qubits"],
                configuration["transpiled_first"],
                configuration["searched_values"]
            )
        )

        return configurations



    def get_source(self, backend: str, filename: str, origin: str) -> str:
        if Path(backend).name != backend:
            raise ValueError("Invalid backend")
        if Path(filename).name != filename:
            raise ValueError("Invalid filename")
        root_folder = Path(Folders().root_folder)
        if origin == "composed_grovers":
            configuration_folder = Path(filename).stem
            python_filename = root_folder / origin / backend / configuration_folder / filename
        elif origin == "whole_grovers":
            python_filename = root_folder / origin / backend / filename
        else:
            raise ValueError(f"Unknown origin: {origin}")
        if not python_filename.exists():
            raise FileNotFoundError(f"File not found: {python_filename}")
        return python_filename.read_text(encoding="utf-8")
    