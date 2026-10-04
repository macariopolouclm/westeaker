import csv
import math
from pathlib import Path
import time
from dataclasses import dataclass

from app.quantum.CircuitsAndCode import load_module, _load_module
from app.quantum.Folders import Folders
from app.quantum.grover_base import GroverBase
from app.quantum.grover_whole_generator import WholeGroverGenerator
from app.quantum.file_utils import get_transpilation_time, check_exist

from app.quantum.qiskit_executor import run 

from qiskit import QuantumCircuit

@dataclass
class GroverExecutor():

    def execute_from_fragments(self, backend, qubits: int, searched_values: list[int], shots: int, transpiled_first : str | None = None):
        common_fragment = f"grover_{transpiled_first}_{qubits}_{'_'.join(map(str, searched_values))}"
        python_filename = f"{Folders().root_folder}composed_grovers/{backend.name}/{common_fragment}/{common_fragment}.py"
        module = load_module(python_filename)
        qc = module.get_qc()
        counts, execution_time = run(backend, qc, shots)
        error = self.calculate_error(counts, searched_values)
        self.save_execution_result(backend.name, python_filename, shots, execution_time, error)
        

    def execute_whole(self, backend, qubits: int, searched_values: list[int], shots: int):
            python_filename = f"{Folders().root_folder}whole_grovers/{backend.name}/grover_whole_{qubits}_{'_'.join(map(str, searched_values))}.py"
            module = load_module(python_filename)
            qc = module.qc
            counts, execution_time = run(backend, qc, shots)
            error = self.calculate_error(counts, searched_values)
            self.save_execution_result(backend.name, python_filename, shots, execution_time, error)

    def execute_file(self, backend, filename: str, origin: str,
                    searched_values: list[int], shots: int):

        root_folder = Path(Folders().root_folder)
        if origin == "composed_grovers":
            configuration_folder = Path(filename).stem
            python_filename = root_folder / origin / backend.name / configuration_folder / filename
            il_filename = root_folder / origin / backend.name / configuration_folder / "il.txt"
        elif origin == "whole_grovers":
            python_filename = root_folder / origin / backend.name / filename
        else:
            raise ValueError(f"Unknown origin: {origin}")

        if not python_filename.exists():
            raise FileNotFoundError(f"File not found: {python_filename}")

        module = load_module(python_filename)
        if origin == "composed_grovers":
            if il_filename.exists():
                initial_layout = [int(value.strip()) for value in il_filename.read_text(encoding="utf-8").split(",")]
                qc = module.get_qc(initial_layout)
            else:
                qc = module.get_qc()
        else :
            qc = module.qc

        counts, execution_time = run(backend, qc, shots)
        error = self.calculate_error(counts, searched_values)
        self.save_execution_result(backend.name, python_filename, shots, execution_time, error)

        return {
            "backend": backend.name,
            "filename": filename,
            "origin": origin,
            "shots": shots,
            "execution_time": execution_time,
            "counts": counts
        }


    def calculate_error(self, counts: dict[str, int], searched_values: list[int]) -> float:
        total = sum(counts.values())

        correct = sum(
            count
            for bitstring, count in counts.items()
            if int(bitstring.replace(" ", ""), 2) in searched_values
        )

        return 1 - (correct / total)

    def save_execution_result(self, backend_name: str, filename: str, shots: int,
                            execution_time: float, error: float):
        results_filename = Path(Folders().root_folder) / "results.tsv"

        with results_filename.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file, delimiter="\t")
            fieldnames = list(reader.fieldnames or [])
            rows = list(reader)

        execution_fields = ["shots", "execution_time", "error"]

        for field in execution_fields:
            if field not in fieldnames:
                fieldnames.append(field)

        target_filename = Path(filename).name

        matching_rows = [
            row for row in rows
            if row.get("backend") == backend_name
            and Path(row.get("filename", "")).name == target_filename
        ]

        if not matching_rows:
            raise ValueError(
                f"Result row not found for {backend_name}: {target_filename}"
            )

        # Primera ejecución: reutilizamos la fila original.
        empty_row = next(
            (
                row for row in matching_rows
                if not row.get("shots")
                and not row.get("execution_time")
                and not row.get("error")
            ),
            None
        )

        if empty_row is not None:
            execution_row = empty_row
        else:
            # Ejecuciones posteriores: nueva fila para el mismo programa.
            execution_row = matching_rows[0].copy()
            rows.append(execution_row)

        execution_row["shots"] = str(shots)
        execution_row["execution_time"] = str(execution_time)
        execution_row["error"] = str(error)

        with results_filename.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)   
    
    
    
    
    
    
    
    
    def _execute_from_source(self, backend, transpiled_first, cl_bits, searched_values, iterations, summary_file):
        transpilation_time_filenames = []

        h_filename = Path(self.folders.root_folder) / "fragments" / "h" / f"{backend.name}" / f"h_{transpiled_first}_{cl_bits}.py"
        h_transpilation_time_filename = h_filename.with_suffix(".transpilation_time.txt")

        transpilation_time_filenames.append(h_transpilation_time_filename)

        oracles_filenames = []
        for searched_value in searched_values :
            oracle_filename = Path(self.folders.root_folder) / "fragments" / "oracles" / f"{backend.name}" / f"oracle_{transpiled_first}_{cl_bits}_{searched_value}.py"
            oracle_transpilation_time_filename = oracle_filename.with_suffix(".transpilation_time.txt")
            oracles_filenames.append(oracle_filename)
            transpilation_time_filenames.append(oracle_transpilation_time_filename)
        diffuser_filename = Path(self.folders.root_folder) / "fragments" / "diffusers" / f"{backend.name}" / f"diffuser_{transpiled_first}_{cl_bits}.py"
        diffuser_transpilation_time_filename = diffuser_filename.with_suffix(".transpilation_time.txt")
        transpilation_time_filenames.append(diffuser_transpilation_time_filename)

        il_folder = "h" if transpiled_first=="h" else f"{transpiled_first}s"
        if transpiled_first == "h" :
            il_filename = Path(self.folders.root_folder) / "fragments" / il_folder / f"{backend.name}" / f"h_{transpiled_first}_{cl_bits}.il.txt"
        elif transpiled_first == "diffuser" :
            il_filename = Path(self.folders.root_folder) / "fragments" / il_folder / f"{backend.name}" / f"diffuser_{transpiled_first}_{cl_bits}.il.txt"
        else :
            il_filename = Path(self.folders.root_folder) / "fragments" / il_folder / f"{backend.name}" / f"oracle_{transpiled_first}_{cl_bits}.il.txt"

        check_exist([h_filename, h_transpilation_time_filename, 
                oracles_filenames, transpilation_time_filenames, 
                diffuser_filename])

        if backend.name!="aer_simulator" :
            check_exist([il_filename])

        transpilation_time = 0
        for transpilation_time_filename in transpilation_time_filenames :
            transpilation_time += float(transpilation_time_filename.read_text(encoding="utf-8").strip())

        initial_layout = None
        if il_filename.exists() :
            initial_layout = [int(value.strip()) for value in il_filename.read_text(encoding="utf-8").split(",") ]

        h_module = _load_module(h_filename)
        h = h_module.get_qc(initial_layout)
        oracles = []
        for oracle_filename in oracles_filenames :
            oracle_module = _load_module(oracle_filename)
            oracle = oracle_module.get_qc(initial_layout)
            oracles.append(oracle)
        diffuser_module = _load_module(diffuser_filename)
        diffuser = diffuser_module.get_qc(initial_layout)

        qc = QuantumCircuit(h.num_qubits, cl_bits)
        qc.append(h.to_instruction(label="h"), range(qc.num_qubits))
        for iteration in range(iterations) :
            for index, oracle in enumerate(oracles) :
                qc.append(oracle.to_instruction(label=f"oracle_{searched_values[index]}"), range(qc.num_qubits))
            qc.append(diffuser.to_instruction(label="diffuser"), range(qc.num_qubits))

        for index in range(cl_bits):
            if initial_layout is None:
                qc.measure(cl_bits - index - 1, index)
            else:
                qc.measure(initial_layout[index], index)

        qc = qc.decompose()
        for current_shots in self.shots:
            execution_time = time.time()
            counts, run_time = self._run(backend, qc, current_shots)
            execution_time = time.time() - execution_time

            gates = sum(qc.count_ops().values())
            depth = qc.depth()

            self._save_line(counts, backend.name, type, "xxx", iterations, "Final", 
                "source code", transpiled_first, qc, gates, depth,
                current_shots, execution_time, transpilation_time, run_time, searched_values, summary_file)


    def _execute_from_ser(self, backend, transpiled_first, cl_bits, searched_values, iterations, summary_file):
        transpilation_time_filenames = []

        h_filename = Path(self.folders.root_folder) / "fragments" / "h" / f"{backend.name}" / f"h_{transpiled_first}_{cl_bits}.ser"
        h_transpilation_time_filename = h_filename.with_suffix(".transpilation_time.txt")

        transpilation_time_filenames.append(h_transpilation_time_filename)

        oracles_filenames = []
        for searched_value in searched_values :
            oracle_filename = Path(self.folders.root_folder) / "fragments" / "oracles" / f"{backend.name}" / f"oracle_{transpiled_first}_{cl_bits}_{searched_value}.ser"
            oracle_transpilation_time_filename = oracle_filename.with_suffix(".transpilation_time.txt")
            oracles_filenames.append(oracle_filename)
            transpilation_time_filenames.append(oracle_transpilation_time_filename)
        diffuser_filename = Path(self.folders.root_folder) / "fragments" / "diffusers" / f"{backend.name}" / f"diffuser_{transpiled_first}_{cl_bits}.ser"
        diffuser_transpilation_time_filename = diffuser_filename.with_suffix(".transpilation_time.txt")
        transpilation_time_filenames.append(diffuser_transpilation_time_filename)

        il_folder = "h" if transpiled_first=="h" else f"{transpiled_first}s"
        if transpiled_first == "h" :
            il_filename = Path(self.folders.root_folder) / "fragments" / il_folder / f"{backend.name}" / f"h_{transpiled_first}_{cl_bits}.il.txt"
        elif transpiled_first == "diffuser" :
            il_filename = Path(self.folders.root_folder) / "fragments" / il_folder / f"{backend.name}" / f"diffuser_{transpiled_first}_{cl_bits}.il.txt"
        else :
            il_filename = Path(self.folders.root_folder) / "fragments" / il_folder / f"{backend.name}" / f"oracle_{transpiled_first}_{cl_bits}.il.txt"

        check_exist([h_filename, h_transpilation_time_filename, 
                oracles_filenames, transpilation_time_filenames, 
                diffuser_filename])

        if backend.name!="aer_simulator" :
            check_exist([il_filename])        

        transpilation_time = 0
        for transpilation_time_filename in transpilation_time_filenames :
            transpilation_time += float(transpilation_time_filename.read_text(encoding="utf-8").strip())

        initial_layout = None
        if il_filename.exists() :
            initial_layout = [int(value.strip()) for value in il_filename.read_text(encoding="utf-8").split(",") ]


        h = self.folders.undump(h_filename)
        oracles = []
        for oracle_filename in oracles_filenames :
            oracle = self.folders.undump(oracle_filename)
            oracles.append(oracle)
        diffuser = self.folders.undump(diffuser_filename)

        qc = QuantumCircuit(h.num_qubits, cl_bits)
        qc.append(h.to_instruction(label="h"), range(qc.num_qubits))
        for iteration in range(iterations) :
            for index, oracle in enumerate(oracles) :
                qc.append(oracle.to_instruction(label=f"oracle_{searched_values[index]}"), range(qc.num_qubits))
            qc.append(diffuser.to_instruction(label="diffuser"), range(qc.num_qubits))

        for index in range(cl_bits):
            if initial_layout is None:
                qc.measure(cl_bits - index - 1, index)
            else:
                qc.measure(initial_layout[index], index)    

        qc = qc.decompose()
        for current_shots in self.shots:
            execution_time = time.time()
            counts, run_time = self._run(backend, qc, current_shots)
            execution_time = time.time() - execution_time

            gates = sum(qc.count_ops().values())
            depth = qc.depth()

            self._save_line(counts, backend.name, type, "xxx", iterations, "Final", 
                "serialized", transpiled_first, qc, gates, depth,
                current_shots, execution_time, transpilation_time, run_time, searched_values, summary_file)

 

    def _execute_wholes(self, generated_filenames, summary_file, backend, searched_values, iterations):
        backend_name = self.get_backend_name(backend)

        transpilation_time = 0
        for generated_filename in generated_filenames :
            if generated_filename.endswith("_transpilation_time.txt") :
                filename = generated_filename.removesuffix("_transpilation_time.txt")
                transpilation_time = get_transpilation_time(filename)
                continue

            check_exist([generated_filename])
            module = load_module(generated_filename)
            qc = module.qc

            for current_shots in self.shots:
                execution_time = time.time()
                counts, run_time = self._run(backend, qc, current_shots)
                execution_time = time.time() - execution_time

                gates = sum(qc.count_ops().values())
                depth = qc.depth()

                self._save_line(counts, backend_name, "Generated from scratch", generated_filename, iterations, "Final", 
                    "source code", "Whole program", qc, gates, depth,
                    current_shots, execution_time, transpilation_time, run_time, searched_values, summary_file)


