from dataclasses import dataclass, field
from pathlib import Path
import time

from qiskit import QuantumCircuit, transpile
from qiskit.qasm2 import dumps

from app.quantum.CircuitsAndCode import generate_subcircuit
from app.quantum.Folders import Folders
from app.quantum.high_level_generator import HighLevelGenerator
from app.quantum.result_utils import save_result

@dataclass
class GroverGenerator:

    folders = Folders()

    generated_files: list[str] = field(
        default_factory=list,
        init=False
    )
    
    found_files: list[str] = field(
        default_factory=list,
        init=False
    )

    def generate_fragments(self, backends, clbits, searched_values: list[int])    :
        self.folders.create(backends, False)
        self.generated_files = []
        self.found_files = []

        # Generamos fragmentos a alto nivel. Los transpilaremos en el bucle que ahí más abajo.
        high_level_generator = HighLevelGenerator()
        h, oracles, diffuser, generated_files, found_files = high_level_generator.generate_at_high_level(clbits, searched_values)
        self.generated_files.extend(generated_files)
        self.found_files.extend(found_files)

        circuits = [h, *oracles, diffuser]
        for backend in backends:
            #self._transpile_from("h", backend, circuits, clbits, searched_values)
            self._transpile_from("oracle", backend, circuits, clbits, searched_values)
            self._transpile_from("diffuser", backend, circuits, clbits, searched_values)

        return self.generated_files, self.found_files


    def _transpile_from(self, transpile_first, backend, circuits, clbits, searched_values):
        h = circuits[0]
        oracles = circuits[1:-1]
        diffuser = circuits[-1]
        if transpile_first == "h": # No se transpila desd H porque los resultados son un desastre 
            initial_layout, target_filename, transpilation_time, gates, depth = self._initial_transpile_and_save(h, backend, "h", "h", transpile_first, clbits)
            save_result(backend, target_filename, "h", transpile_first, clbits, transpilation_time, None, gates, depth)
            for index, oracle in enumerate(oracles):
                target_filename, transpilation_time, gates, depth = self._transpile_and_save(oracle, backend, "oracles", "oracle", transpile_first, clbits, initial_layout, searched_values[index])
                save_result(backend, target_filename, "oracle", transpile_first, clbits, transpilation_time, searched_values[index], gates, depth)
            target_filename, transpilation_time, gates, depth = self._transpile_and_save(diffuser, backend, "diffusers", "diffuser", transpile_first, clbits, initial_layout)
            save_result(backend, target_filename, "diffuser", transpile_first, clbits, transpilation_time, None, gates, depth)
        elif transpile_first == "oracle":
            initial_layout, target_filename, transpilation_time, gates, depth = self._initial_transpile_and_save(oracles[0], backend, "oracles", "oracle", transpile_first, clbits, searched_values[0])
            save_result(backend, target_filename, "oracle", transpile_first, clbits, transpilation_time, searched_values[0], gates, depth)
            for index, oracle in enumerate(oracles[1:], start=1):
                target_filename, transpilation_time, gates, depth = self._transpile_and_save(oracle, backend, "oracles", "oracle", transpile_first, clbits, initial_layout, searched_values[index])
                save_result(backend, target_filename, "oracle", transpile_first, clbits, transpilation_time, searched_values[index], gates, depth)
            target_filename, transpilation_time, gates, depth = self._transpile_and_save(h, backend, "h", "h", transpile_first, clbits, initial_layout)
            save_result(backend, target_filename, "h", transpile_first, clbits, transpilation_time, None, gates, depth)
            target_filename, transpilation_time, gates, depth = self._transpile_and_save(diffuser, backend, "diffusers", "diffuser", transpile_first, clbits, initial_layout)
            save_result(backend, target_filename, "diffuser", transpile_first, clbits, transpilation_time, None, gates, depth)
        else:
            initial_layout, target_filename, transpilation_time, gates, depth = self._initial_transpile_and_save(diffuser, backend, "diffusers", "diffuser", transpile_first, clbits)
            save_result(backend, target_filename, "diffuser", transpile_first, clbits, transpilation_time, None, gates, depth)
            target_filename, transpilation_time, gates, depth = self._transpile_and_save(h, backend, "h", "h", transpile_first, clbits, initial_layout)
            save_result(backend, target_filename, "h", transpile_first, clbits, transpilation_time, None, gates, depth)
            for index, oracle in enumerate(oracles):
                target_filename, transpilation_time, gates, depth = self._transpile_and_save(oracle, backend, "oracles", "oracle", transpile_first, clbits, initial_layout, searched_values[index])
                save_result(backend, target_filename, "oracle", transpile_first, clbits, transpilation_time, searched_values[index], gates, depth)


    def _save_artifacts(self, subfolder: str, backend_name: str, circuit_type : str, transpile_first: str, clbits : int, 
            code: str, qc, searched_value: int | None = None, initial_layout: list[int] | None = None,
            transpilation_time: float | None = None) :
        
        folder = Path(self.folders.root_folder) / "fragments" / subfolder / backend_name
        python_file = f"{folder}/{circuit_type}_{transpile_first}_{clbits}"
        ser_file = f"{python_file}"
        qasm_file = f"{python_file}"
        il_file = f"{folder}/{circuit_type}_{transpile_first}_{clbits}.il"
        transpilation_time_file = f"{folder}/{circuit_type}_{transpile_first}_{clbits}.transpilation_time"

        if searched_value is not None :
            python_file = f"{python_file}_{searched_value}"
            ser_file = f"{ser_file}_{searched_value}"
            qasm_file = f"{qasm_file}_{searched_value}"
            transpilation_time_file = f"{folder}/{circuit_type}_{transpile_first}_{clbits}_{searched_value}.transpilation_time"

        python_file = f"{python_file}.py"
        ser_file = f"{ser_file}.ser"
        qasm_file = f"{qasm_file}.qasm"
        il_file = f"{il_file}.txt"
        transpilation_time_file = f"{transpilation_time_file}.txt"

        self.folders.save_text(python_file, code)
        self._generated(python_file)
        self.folders.save_text(qasm_file, dumps(qc))
        self._generated(qasm_file)
        #self.folders.dump(ser_file, qc)
        #self._generated(ser_file)
        if initial_layout is not None :
            self.folders.save_text(il_file, ", ".join(map(str, initial_layout)))
            self._generated(il_file)
        if transpilation_time is not None:
            self.folders.save_text(transpilation_time_file, str(transpilation_time))
            self._generated(transpilation_time_file)

    
    def _get_target_filename(self, subfolder, backend_name, circuit_type, transpile_first, clbits, searched_value=None):
        filename = f"{circuit_type}_{transpile_first}_{clbits}"
        if searched_value is not None:
            filename += f"_{searched_value}"
        return (
            Path(self.folders.root_folder)
            / "fragments"
            / subfolder
            / backend_name
            / f"{filename}.py"
        )

    def _initial_transpile_and_save(self, circuit, backend, subfolder, circuit_type, transpile_first, clbits, searched_value=None):
        target_filename = self._get_target_filename(subfolder, backend.name, circuit_type, transpile_first, clbits, searched_value)
        if target_filename.exists():
            self._found(target_filename)
            name = target_filename.stem
            parts = name.split("_")
            il_filename = target_filename.with_name("_".join(parts[:3]) + ".il.txt")
            initial_layout = None
            if Path(il_filename).exists() :
                initial_layout = [
                        int(value.strip())
                        for value in il_filename.read_text(encoding="utf-8").split(",")
                    ]
                self._found(il_filename)

            path = Path(target_filename)
            transpilation_time_filename = path.parent / f"{path.stem}.transpilation_time.txt"
            transpilation_time = float(transpilation_time_filename.read_text(encoding="utf-8").strip())
            return initial_layout, target_filename, transpilation_time, 0, 0
        transpiled_qc, initial_layout, transpilation_time = self._initial_transpile_for(circuit, backend)
        code = generate_subcircuit(transpiled_qc, "get_qc", initial_layout, clbits)
        self._save_artifacts(
            subfolder, backend.name, circuit_type, transpile_first, clbits,
            code, transpiled_qc,
            searched_value=searched_value,
            initial_layout=initial_layout,
            transpilation_time=transpilation_time
        )
        excluded = {"measure", "barrier", "reset"}
        gates = sum(count for name, count in transpiled_qc.count_ops().items() if name not in excluded)
        depth = transpiled_qc.depth()
        return initial_layout, target_filename, transpilation_time, gates, depth

    def _transpile_and_save(self, circuit, backend, subfolder, circuit_type, transpile_first, clbits, initial_layout, searched_value=None):
        target_filename = self._get_target_filename(subfolder, backend.name, circuit_type, transpile_first, clbits, searched_value)
        if target_filename.exists():
            self._found(target_filename)
            path = Path(target_filename)
            transpilation_time_filename = path.parent / f"{path.stem}.transpilation_time.txt"
            transpilation_time = float(transpilation_time_filename.read_text(encoding="utf-8").strip())
            return target_filename, transpilation_time, 0, 0
        transpiled_qc, transpilation_time = self._transpile_for(circuit, backend, initial_layout=initial_layout)
        code = generate_subcircuit(transpiled_qc, "get_qc", initial_layout, clbits)
        self._save_artifacts(
            subfolder, backend.name, circuit_type, transpile_first, clbits,
            code, transpiled_qc,
            searched_value=searched_value,
            initial_layout=None,
            transpilation_time=transpilation_time
        )
        excluded = {"measure", "barrier", "reset"}
        gates = sum(count for name, count in transpiled_qc.count_ops().items() if name not in excluded)
        depth = transpiled_qc.depth()
        return target_filename, transpilation_time, gates, depth
        

    

    def _initial_transpile_for(self, circuit, backend, optimization_level=3):
        qc, transpilation_time = self._transpile_for(circuit, backend, initial_layout=None, optimization_level=optimization_level)
        if not qc.layout or not qc.layout.initial_layout:
            return qc, None, transpilation_time
        layout = qc.layout.initial_layout
        initial_layout = []
        for qubit in circuit.qubits:
            if qubit not in layout:
                raise ValueError(
                    f"No se encontró el cúbit original {qubit} en el initial_layout."
                )
            initial_layout.append(layout[qubit])
        return qc, initial_layout, transpilation_time

    def _transpile_for(self, circuit: QuantumCircuit, backend, initial_layout, optimization_level = 3) :
        transpilation_time = time.time()
        qc = transpile(circuit, backend,
               optimization_level=optimization_level, 
               initial_layout = initial_layout
        )
        transpilation_time = time.time() - transpilation_time
        #time_file_name = Path(file_name).with_name(Path(file_name).stem + "_transpilation_time.txt")
        #self.folders.save_file(time_file_name, str(transpilation_time))
        #self._generated(time_file_name)
        return qc, transpilation_time



    def _generated(self, *file_names):
        for file_name in file_names:
            self.generated_files.append(
                str(Path(file_name).resolve())
            )

    def _found(self, *file_names):
        for file_name in file_names:
            self.found_files.append(
                str(Path(file_name).resolve())
            )