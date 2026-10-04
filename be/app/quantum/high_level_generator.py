import math
import os 

from dataclasses import dataclass
from qiskit import QuantumCircuit
from app.quantum.CircuitsAndCode import generate_subcircuit
from app.quantum.Folders import Folders

@dataclass
class HighLevelGenerator:

    folders = Folders()

    def generate_at_high_level(self, qubits : int, searched_values) -> tuple[QuantumCircuit, list[QuantumCircuit], QuantumCircuit]:
        generated_files : list[str] = []
        found_files : list[str] = []

        python_file_name = f"{self.folders.root_folder}fragments/h/high_level/h_{qubits}.py"
        h_circuit = self._h_column(qubits) # Lo genero, aunque ya exista, porque lo tengo que devolver para transpilarlo
        if not os.path.exists(python_file_name):
            h_code = generate_subcircuit(h_circuit, function_name=f"get_h_{qubits}")
            self.folders.save_text(python_file_name, h_code)
            generated_files.append(python_file_name)
        else :
            found_files.append(python_file_name)

        oracles = []
        for searched_value in searched_values:
            python_file_name = f"{self.folders.root_folder}fragments/oracles/high_level/oracle_{qubits}_{searched_value}.py"
            oracle_circuit = self._oracle_circuit(searched_value, qubits) # Lo genero, aunque ya exista, porque lo tengo que devolver para transpilarlo
            oracles.append(oracle_circuit)
            if not os.path.exists(python_file_name):
                oracle_code = generate_subcircuit(oracle_circuit, function_name=f"get_oracle_{qubits}_{searched_value}")
                self.folders.save_text(python_file_name, oracle_code)
                generated_files.append(python_file_name)
            else:
                found_files.append(python_file_name)

        python_file_name = f"{self.folders.root_folder}fragments/diffusers/high_level/diffuser_{qubits}.py"
        diffuser_circuit = self._diffuser_circuit(qubits) # Lo genero, aunque ya exista, porque lo tengo que devolver para transpilarlo
        if not os.path.exists(python_file_name):
            diffuser_code = generate_subcircuit(diffuser_circuit, function_name=f"get_diffuser_{qubits}")
            self.folders.save_text(python_file_name, diffuser_code)
            generated_files.append(python_file_name)
        else:
            found_files.append(python_file_name)
        return h_circuit, oracles, diffuser_circuit, generated_files, found_files


    def _oracle_circuit(self, n: int, qubits: int) -> QuantumCircuit:
        qc = QuantumCircuit(qubits)
        binary_value = bin(n)[2:].zfill(qubits)
        for i in range(len(binary_value)):
            if binary_value[i] == "0":
                qc.x(i)
        control = list(range(0, qubits - 1))
        qc.mcp(math.pi, control, qubits - 1)
        for i in range(len(binary_value)):
            if binary_value[i] == "0":
                qc.x(i)
        return qc

    def _diffuser_circuit(self, qubits: int) -> QuantumCircuit:
        qc = QuantumCircuit(qubits)
        for i in range(qubits):
            qc.h(i)
            qc.x(i)
        control = list(range(0, qubits - 1))
        qc.mcp(math.pi, control, qubits - 1)
        for i in range(qubits):
            qc.x(i)
            qc.h(i)
        return qc

    def _h_column(self, qubits: int) -> QuantumCircuit:
        qc = QuantumCircuit(qubits)
        for i in range(qubits):
            qc.h(i)
        return qc