from dataclasses import dataclass, field
import math
from pathlib import Path
import shutil
import sys
import importlib.util

from qiskit import QuantumCircuit
from qiskit.qasm2 import dumps

from app.quantum.CircuitsAndCode import generate_subcircuit, load_module, _load_module
from app.quantum.Folders import Folders
from app.quantum.file_utils import get_transpilation_time, get_initial_layout
from app.quantum.result_utils import save_result

@dataclass
class GroverMounterFromFragments:

    folders = Folders()

    generated_files: list[str] = field(default_factory=list, init=False)
    found_files: list[str] = field(default_factory=list, init=False)

    def mount_for(self, backend, clbits : int | None = None, searched_values: list[int] | None = None) :
        #for transpiled_first in ["h", "diffuser", "oracle"] :
        for transpiled_first in ["diffuser", "oracle"] :
            oracles_filenames = []
            h_filename = Path(self.folders.root_folder) / "fragments" / "h" / backend.name / f"h_{transpiled_first}_{clbits}"
            diffuser_filename = Path(self.folders.root_folder) / "fragments" / "diffusers" / backend.name / f"diffuser_{transpiled_first}_{clbits}"
            for searched_value in searched_values :
                oracle_filename = Path(self.folders.root_folder) / "fragments" / "oracles" / backend.name / f"oracle_{transpiled_first}_{clbits}_{searched_value}"
                oracles_filenames.append(oracle_filename)
                
            target_file, transpilation_time, gates, depth = self.mount_from_fragments(backend, transpiled_first, h_filename, oracles_filenames, diffuser_filename, clbits, searched_values)
            save_result(backend, target_file, "from_fragments", transpiled_first, clbits, transpilation_time, searched_values, gates, depth)


    def mount_from_fragments(self, backend, transpiled_first, h_filename, oracles_filenames, diffuser_filename, clbits, searched_values) :
        searched_values_str = '_'.join(map(str, searched_values))

        target_folder = Path(self.folders.root_folder) / "composed_grovers" / backend.name / f"grover_{transpiled_first}_{clbits}_{searched_values_str}"
        target_folder.mkdir(parents = True, exist_ok=True)

        h_transpilation_time = self._get_transpilation_time(h_filename)
        oracles_transpilation_time = 0
        for oracle_filename in oracles_filenames :
            oracle_transpilation_time = self._get_transpilation_time(oracle_filename)
            oracles_transpilation_time = oracles_transpilation_time + oracle_transpilation_time 
        diffuser_transpilation_time =self._get_transpilation_time(diffuser_filename)
        transpilation_time = h_transpilation_time + oracles_transpilation_time + diffuser_transpilation_time

        il_filename = None
        if transpiled_first=="h" :
            il_filename = target_folder.parent.parent.parent / "fragments" / "h" / backend.name / f"h_{transpiled_first}_{clbits}.il.txt"
        elif transpiled_first=="diffuser" :
            il_filename = target_folder.parent.parent.parent / "fragments" / "diffusers" / backend.name / f"diffuser_{transpiled_first}_{clbits}.il.txt"
        else :
            il_filename = target_folder.parent.parent.parent / "fragments" / "oracles" / backend.name / f"oracle_{transpiled_first}_{clbits}.il.txt"

        initial_layout = None
        if (il_filename.exists()) :
            initial_layout = [ int(value.strip()) for value in il_filename.read_text(encoding="utf-8").split(",") ]
            shutil.copy2(il_filename, target_folder / "il.txt")

        h_filename = f"{h_filename}.py"
        oracles_filenames = [f"{oracle_filename}.py" for oracle_filename in oracles_filenames]
        diffuser_filename = f"{diffuser_filename}.py"

        shutil.copy2(h_filename, target_folder)
        for oracle_filename in oracles_filenames:
            shutil.copy2(oracle_filename, target_folder)
        shutil.copy2(diffuser_filename, target_folder)

        if backend.name == "aer_simulator":
            num_qubits = clbits
        else :
            num_qubits = backend.num_qubits

        target_file = target_folder / f"{target_folder.name}.py"
        iterations = max(1, round((math.pi / 4) * math.sqrt((2 ** clbits) / len(searched_values))))

        with target_file.open("w", encoding="utf-8") as f:
            f.write("from qiskit import QuantumCircuit\n\n")
            f.write(f"from {Path(h_filename).stem} import get_qc as get_h\n")
            for index, oracle_filename in enumerate(oracles_filenames):
                f.write(f"from {Path(oracle_filename).stem} import get_qc as get_oracle_{searched_values[index]}\n")
            f.write(f"from {Path(diffuser_filename).stem} import get_qc as get_diffuser\n\n")

            f.write("def get_qc(initial_layout : list[int] | None = None) :\n")
            f.write(f"\tqc=QuantumCircuit({num_qubits}, {clbits})\n\n")

            f.write(f"\tqc.compose(get_h(initial_layout), qubits=range({num_qubits}), inplace=True)\n")
            f.write(f"\tfor iteration in range({iterations}) :\n")
            for index, oracle_filename in enumerate(oracles_filenames):
                f.write(f"\t\tqc.compose(get_oracle_{searched_values[index]}(initial_layout), qubits=range({num_qubits}), inplace=True)\n")
            f.write(f"\t\tqc.compose(get_diffuser(initial_layout), qubits=range({num_qubits}), inplace=True)\n")

            f.write("\n")
            if initial_layout is None:
                for index in range(clbits):
                    f.write(f"\tqc.measure({clbits-index-1}, {index})\n")
            else :
                cont = len(initial_layout) - 1
                for index in range(len(initial_layout)) :
                    f.write(f"\tqc.measure(initial_layout[{index}], {cont})\n")
                    cont = cont - 1
            f.write("\n\treturn qc")

        transpilation_time_filename = target_folder / "transpilation_time.txt"
        transpilation_time_filename.write_text(str(transpilation_time), encoding="utf-8")

        module = load_module(target_file)
        qc = module.get_qc(initial_layout)

        excluded = {"measure", "barrier", "reset"}
        gates = sum(count for name, count in qc.count_ops().items() if name not in excluded)
        depth = qc.depth()

        qasm_filename = target_file.with_suffix(".qasm")
        self.folders.save_text(qasm_filename, dumps(qc))

        ser_filename = target_file.with_suffix(".ser")
        self.folders.dump(ser_filename, qc)

        self._generated(target_file)
        self._generated(transpilation_time_filename)
        self._generated(qasm_filename)
        self._generated(ser_filename)

        return target_file, transpilation_time, gates, depth

    def _get_transpilation_time(self, filename) :
        path = Path(filename)
        transpilation_time_filename = path.parent / f"{path.name}.transpilation_time.txt"
        transpilation_time = float(transpilation_time_filename.read_text(encoding="utf-8").strip())
        return transpilation_time

    def _generated(self, *file_names):
        for file_name in file_names:
            self.generated_files.append(str(Path(file_name).resolve()))

    def _found(self, *file_names):
        for file_name in file_names:
            self.found_files.append(str(Path(file_name).resolve()))
