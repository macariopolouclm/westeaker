import math
import time
from dataclasses import dataclass
from pathlib import Path

from qiskit import QuantumCircuit

from app.quantum.CircuitsAndCode import load_module, generate_subcircuit
from app.quantum.Folders import Folders
from app.quantum.grover_base import GroverBase
from app.quantum.file_utils import get_transpilation_time, get_transpiled_first, get_initial_layout, get_circuit_from_module

from app.quantum.strategies.aer_steak_execution_strategy import AerSteakExecutionStrategy
from app.quantum.strategies.standard_steak_execution_strategy import StandardSteakExecutionStrategy

@dataclass
class GroverSteaker(GroverBase) :

    folders = Folders()

    def __init__(self, shots: int | list[int] | None = None):
        super().__init__(shots=shots)

    def _traverse(self, backends, summary_file, generated_lines, from_source, transpiled_firsts):
        origin = "source code" if from_source else "serialized"
        for backend in backends:
            backend_name = self.get_backend_name(backend)
            strategy = AerSteakExecutionStrategy(self) if backend_name == "aer_simulator" else StandardSteakExecutionStrategy(self)

            for line in generated_lines:
                parsed = self._parse_generated_line(line)
                if parsed is None:
                    continue
                cl_bits, iterations, searched_values = parsed
                qubits = cl_bits if backend_name == "aer_simulator" else backend.num_qubits
                strategy.execute(backend, qubits, cl_bits, searched_values, iterations, origin, from_source, summary_file, self.shots)



    def _execute_standard_steaks(self, backend, backend_name, qubits, cl_bits, searched_values, iterations, origin, from_source, summary_file):
        program_filename = self.folders.get_grover_filename(cl_bits, searched_values)

        for current_shots in self.shots:
            run_time = 0

            steak, initial_layout = self._mount_steak_1(backend, qubits, cl_bits, searched_values, from_source)
            steak = steak.decompose()

            total_gates = sum(steak.count_ops().values())
            total_depth = steak.depth()

            counts, current_run_time = self._run(backend, steak, current_shots)
            run_time += current_run_time

            self._save_steak_line(counts, backend_name, program_filename, iterations, 1,
                origin, steak, total_gates, total_depth, current_shots, run_time, searched_values, summary_file)

            angles = self._angles_from_counts(counts, cl_bits, current_shots)
            angles_in_degrees = [math.degrees(angle) for angle in angles]

            for iteration in range(2, iterations + 1):
                steak = self._mount_next_steak(backend_name, qubits, cl_bits, searched_values, initial_layout, angles, from_source)

                total_gates += sum(steak.count_ops().values())
                total_depth += steak.depth()

                counts, current_run_time = self._run(backend, steak, current_shots)
                run_time += current_run_time

                self._save_steak_line(counts, backend_name, program_filename, iterations, iteration,
                    origin, steak, total_gates, total_depth, current_shots, run_time, searched_values, summary_file)

                angles = self._angles_from_counts(counts, cl_bits, current_shots)
                angles_in_degrees = [math.degrees(angle) for angle in angles]




    def _angles_from_counts(self, counts, cl_bits, shots):
        probabilities = self._calculate_probabilities(counts, cl_bits, shots)
        return [2 * math.asin(math.sqrt(min(1.0, max(0.0, p)))) for p in probabilities]

    def _mount_steak_1(self, backend, qubits, cl_bits, searched_values, from_source):
        if from_source:
            return self._mount_steak_1_from_source(backend, qubits, cl_bits, searched_values)

        return self._mount_steak_1_from_ser(backend, qubits, cl_bits, searched_values)

    def _mount_steak_1_from_source(self, backend, qubits, cl_bits, searched_values):
        backend_name = self.get_backend_name(backend)

        initial_layout = get_initial_layout(backend_name, cl_bits)

        h_filename = self.folders.get_filepath(backend_name, "h", cl_bits)
        module = load_module(h_filename)
        h = get_circuit_from_module(module, "h", initial_layout)

        steak_1 = QuantumCircuit(qubits, cl_bits)
        steak_1.append(h, range(qubits))

        self._add_oracles_and_diffuser_from_source(backend_name, steak_1, qubits, cl_bits, searched_values, initial_layout)
        return steak_1, initial_layout

    def _mount_steak_1_from_ser(self, backend, qubits, cl_bits, searched_values):
        backend_name = self.get_backend_name(backend)

        h_filename = self.folders.get_filepath(backend_name, "h", cl_bits)
        h_filename = Path(h_filename).with_suffix(".ser")
        h = self.folders.undump(h_filename)

        steak_1 = QuantumCircuit(qubits, cl_bits)
        steak_1.append(h, range(qubits))

    def _mount_next_steak(self, backend_name, qubits, cl_bits, searched_values, initial_layout, angles, from_source):
        steak = QuantumCircuit(qubits, cl_bits)

        for index, angle in enumerate(angles):
            qubit = index if initial_layout is None else initial_layout[index]
            steak.ry(angle, qubit)

        if from_source:
            self._add_oracles_and_diffuser_from_source(backend_name, steak, qubits, cl_bits, searched_values, initial_layout)
        else:
            self._add_oracles_and_diffuser_from_ser(backend_name, steak, qubits, cl_bits, searched_values, initial_layout)

        return steak


    def _save_steak_line(self, counts, backend_name, program_filename, iterations, iteration, origin,
        steak, total_gates, total_depth, shots, run_time, searched_values, summary_file):

        self._save_line(counts, backend_name, "steaks", program_filename, iterations, iteration, origin,
                    "T1st _traverse", steak, total_gates, total_depth, shots, run_time, 0, run_time,
                    searched_values, summary_file)

        
    def _parse_generated_line(self, line):
        line = line.strip()

        if not line:
            return None
        cl_bits, iterations, searched_values, _ = line.split("\t")
        return (int(cl_bits), int(iterations), list(map(int, searched_values.split(","))))

    def _add_oracles_and_diffuser_from_source(self, backend_name, steak, qubits, cl_bits, searched_values, initial_layout) :
        for searched_value in searched_values:
            oracle_filename = self.folders.get_filepath(backend_name, "oracles", cl_bits, searched_value)
            module = load_module(oracle_filename)

            oracle = get_circuit_from_module(module, f"oracle_{searched_value}", initial_layout)
            steak.append(oracle, range(0, qubits))

        diffuser_filename = self.folders.get_filepath(backend_name, "diffusers", cl_bits)
        module = load_module(diffuser_filename)
        diffuser = get_circuit_from_module(module, "diffuser", initial_layout)
        steak.append(diffuser, range(0, qubits))


    def _add_oracles_and_diffuser_from_ser(self, backend_name, steak, qubits, cl_bits, searched_values, initial_layout):
        for searched_value in searched_values:
            oracle_filename = self.folders.get_filepath(backend_name, "oracles", cl_bits, searched_value)
            oracle_filename = Path(oracle_filename).with_suffix(".ser")
            oracle = self.folders.undump(oracle_filename)

            steak.append(oracle, range(qubits))

        diffuser_filename = self.folders.get_filepath(backend_name, "diffusers", cl_bits)
        diffuser_filename = Path(diffuser_filename).with_suffix(".ser")
        diffuser = self.folders.undump(diffuser_filename)

        steak.append(diffuser, range(qubits))

    def _add_measures(self, steak, initial_layout) :
        for index in range(steak.num_clbits):
            if initial_layout is None:
                steak.measure(steak.num_clbits - index - 1, index)
            else:
                steak.measure(initial_layout[steak.num_clbits - index - 1], index)

    def _calculate_probabilities(self, counts, qubits, shots):
        probs = [0.0] * qubits
        #counts = {'0000': 30, '0001': 38, '0010': 41, '0011': 32, '0100': 49, '0101': 468, '0110': 42, '0111': 31, '1000': 32, '1001': 23, '1010': 36, '1011': 31, '1100': 45, '1101': 36, '1110': 32, '1111': 34}

        for bitstring, count in counts.items():
            if count == 0 :
                continue

            value = int(bitstring, 2)
            while value :
                lowest_one_bit = value & -value
                bit_index_from_right = lowest_one_bit.bit_length() - 1
                q = qubits - 1 - bit_index_from_right

                probs[q] += count
                value ^= lowest_one_bit

            '''
            bitstring = bitstring.zfill(qubits)

            for q in range(qubits):
                if bitstring[q] == "1":
                    probs[q] += count
            '''
        probs = [value / shots for value in probs]
        # probs = [ 0.281, 0.719, 0.281, 0.719]
        return probs
