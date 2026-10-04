import math
import os
from dataclasses import dataclass, field
from pathlib import Path
import time

from qiskit import QuantumCircuit, transpile
from qiskit.qasm2 import dumps

from app.quantum.CircuitsAndCode import generate_subcircuit, load_module
from app.quantum.Folders import Folders
from app.quantum.result_utils import save_result

@dataclass
class WholeGroverGenerator:
    qubits : int
    clbits : int | None = None

    folders = Folders()

    generated_files: list[str] = field(
        default_factory=list,
        init=False
    )

    def __post_init__(self) :
        self.clbits = self.qubits

    def generate_files(self, backend, searched_values: list[int]) :
        self.generated_files = []

        iterations = max(1, round((math.pi / 4) * math.sqrt((2 ** self.clbits) / len(searched_values))))

        qc = self.generate_at_high_level(searched_values, iterations)
        values = "_".join(map(str, sorted(searched_values)))
        python_file_name = Path(self.folders.root_folder) / "whole_grovers" / "high_level" / f"grover_whole_{self.qubits}_{values}.py"
        code = generate_subcircuit(qc, None, cl_bits=self.qubits)
        self.folders.save_text(python_file_name, code)

        python_file_name, transpilation_time, gates, depth = self._generate_for(backend, qc, searched_values)
        save_result(backend, python_file_name, "whole_grover", "", self.clbits, transpilation_time, searched_values, gates, depth)
        return self.generated_files

    def _generate_for(self, backend, qc: QuantumCircuit, searched_values):
        values = "_".join(map(str, sorted(searched_values)))
        python_file_name = Path(self.folders.root_folder) / "whole_grovers" / f"{backend.name}" / f"grover_whole_{self.qubits}_{values}.py"
        transpiled_qc, transpilation_time, gates, depth = self._transpile_for(qc, backend, python_file_name, initial_layout=None)
        code = generate_subcircuit(transpiled_qc, function_name=None, initial_layout=None, cl_bits=self.qubits)
        self.folders.save_text(python_file_name, code)
        self._generated(python_file_name)
        return python_file_name, transpilation_time, gates, depth

    def generate_at_high_level(self, searched_values, iterations) -> QuantumCircuit :
        qc = QuantumCircuit(self.qubits, self.qubits)
        for i in range(self.qubits):
            qc.h(i)
        qc.barrier()

        for iteration in range(iterations) :
            # Oráculos
            for searched_value in searched_values :
                binary_value = bin(searched_value)[2:].zfill(self.qubits)
                for i in range(len(binary_value)):
                    if binary_value[i] == "0":
                        qc.x(i)
                control = list(range(0, self.qubits - 1))
                qc.mcp(math.pi, control, self.qubits - 1)
                for i in range(len(binary_value)):
                    if binary_value[i] == "0":
                        qc.x(i)
                qc.barrier()
            # Difusor
            for i in range(self.qubits):
                qc.h(i)
                qc.x(i)
            control = list(range(0, self.qubits - 1))
            qc.mcp(math.pi, control, self.qubits - 1)
            for i in range(self.qubits):
                qc.x(i)
                qc.h(i)
            qc.barrier()

        for index in range(self.qubits):
            qc.measure(self.qubits-index-1, index)

        return qc
        

    def _transpile_for(self, circuit: QuantumCircuit, backend, file_name, initial_layout, optimization_level = 3) :
        transpilation_time = time.time()
        qc = transpile(circuit, backend,
               optimization_level=optimization_level, 
               initial_layout = initial_layout
        )
        transpilation_time = time.time() - transpilation_time
        time_file_name = Path(file_name).with_name(Path(file_name).stem + "_transpilation_time.txt")
        self.folders.save_text(time_file_name, str(transpilation_time))
        self._generated(time_file_name)
        excluded = {"measure", "barrier", "reset"}
        gates = sum(count for name, count in qc.count_ops().items() if name not in excluded)
        depth = qc.depth()
        return qc, transpilation_time, gates, depth

    
    def _generated(self, *file_names):
        for file_name in file_names:
            self.generated_files.append(
                str(Path(file_name).resolve())
            )

