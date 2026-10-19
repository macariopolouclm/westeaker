from pathlib import Path

from app.quantum.Folders import Folders
from qiskit import QuantumCircuit, transpile
from app.quantum.backends import find_backend
from app.quantum.CircuitsAndCode import generate_subcircuit
from app.quantum.result_utils import save_result
import time

class TranspilationService:

    def transpile(self, filename: str, code: str, backend_infos: list):
        filename = Path(filename).name
        if not filename.endswith(".py"):
            filename += ".py"
        circuit, expected = self._get_circuit(code)
        generated_files = []
        failed_backends = []
        root_folder = Path(Folders().root_folder) / "others"
        excluded = {"measure", "barrier", "reset"}
        for backend_info in backend_infos:
            backend = find_backend(backend_info.name)
            backendWrapper = find_backend(backend.name)
            try:
                start = time.perf_counter()
                transpiled_circuit = transpile(circuit, backend.backend)
                transpilation_time = time.perf_counter() - start
                gates = sum(count for name, count in transpiled_circuit.count_ops().items() if name not in excluded)
                depth = transpiled_circuit.depth()
                save_result(backend, filename, "others", "", 
                    circuit.num_clbits, transpilation_time, None, gates, depth)

                target_folder = root_folder / backend.name
                target_folder.mkdir(parents=True, exist_ok=True)
                target_filename = target_folder / filename
                transpiled_code = generate_subcircuit(backendWrapper, transpiled_circuit, None, None, circuit.num_clbits, expected)
                target_filename.write_text(transpiled_code, encoding="utf-8")
                generated_files.append(str(target_filename))
            except Exception as exception:
                failed_backends.append({
                    "name": backend.name,
                    "provider": backend.provider,
                    "error": str(exception)
                })
        return {
            "generated_files": generated_files,
            "failed_backends": failed_backends
        }
    
    def _get_circuit(self, code: str) -> QuantumCircuit:
        namespace = {}
        exec(code, namespace)
        qc = namespace.get("qc")
        if not isinstance(qc, QuantumCircuit):
            raise ValueError("Python code must create a QuantumCircuit named 'qc'.")
        expected = f"expected={namespace.get('expected')}"
        return qc, expected