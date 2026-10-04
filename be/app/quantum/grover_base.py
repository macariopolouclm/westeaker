import os
import time
from pathlib import Path

from app.quantum.Folders import Folders

class GroverBase :

    folders = Folders()

    def __init__(self, shots: int | list[int] | None = None):
        if shots is None:
            self.shots = [1024]
        elif isinstance(shots, int):
            self.shots = [shots]
        else:
            self.shots = shots

    def execute(self, backends, generated_lines : list[str], origins, transpiled_firsts : list[str]):
        summary_path = Path(os.path.join(Folders().root_folder, "summary.tsv"))
        file_exists = summary_path.exists()
        with open(summary_path, "a") as summary_file:
            if not file_exists:
                summary_file.write("Backend\tType\tProgram\tIterations\tIteration\tOrigin\tTranspiled 1st\tQubits\tBits\tGates\tDepth\tShots\tError\tTotal time\tTransp. time\tRun time\tSearched_values\n")
            summary_file.flush()
            self._traverse(backends, summary_file, generated_lines, origins, transpiled_firsts)

    def _run(self, backend, qc, current_shots):
        run_time = time.time()
        job = backend.run(qc, shots=current_shots)
        result = job.result()
        counts = result.get_counts()
        run_time = time.time() - run_time
        counts = dict(sorted(counts.items()))
        return counts, run_time

    def _error(self, counts: dict[str, int], searched_values: list[int], reverse_bits: bool = False) -> float:
        total_shots = sum(counts.values())

        decimal_counts = {}
        for bitstring, shots in counts.items():
            normalized_bitstring = bitstring.replace(" ", "")
            decimal_value = int(normalized_bitstring, 2)
            decimal_counts[decimal_value] = shots

        correct_shots = 0
        for searched_value in searched_values:
            obtained_freq = decimal_counts.get(searched_value, 0)
            correct_shots += obtained_freq
        return round(1.0 - correct_shots / total_shots, 2)

    def _save_line(self, 
            counts, backend_name, type, program_filename, iterations, iteration, 
            origin, transpiled_first, qc, gates, depth, 
            shots, execution_time, transpilation_time, run_time, searched_values, summary_file):
        error = self._error(counts, searched_values)
        qubits = qc.num_qubits
        clbits = qc.num_clbits
        if execution_time :
            execution_time = self._fmt_decimal(execution_time, 2)
        transpilation_time = self._fmt_decimal(round(transpilation_time, 2))
        run_time = self._fmt_decimal(round(run_time, 2))
        summary_file.write(
            f"{backend_name}\t{type}\t{Path(program_filename).name}\t{iterations}\t{iteration}"
            f"\t{origin}\t{transpiled_first}\t{qubits}\t{clbits}\t{gates}\t{depth}"
            f"\t{shots}\t{error}\t{execution_time}\t{transpilation_time}\t{run_time}\t{searched_values}\n")
        summary_file.flush()

    def get_backend_name(self, backend):
        return backend.name if hasattr(backend, "name") else backend.backend_name

    def _fmt_decimal(self, value, ndigits=2):
        if value is None:
            return ""

        if isinstance(value, float):
            return f"{value:.{ndigits}f}".replace(".", ",")

        return str(value).replace(".", ",")
