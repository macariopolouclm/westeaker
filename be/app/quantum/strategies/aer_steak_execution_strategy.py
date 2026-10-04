import math
import time

from qiskit import QuantumCircuit

from app.quantum.strategies.steak_execution_strategy import SteakExecutionStrategy

from qiskit_aer import AerSimulator
from qiskit_aer.library import save_density_matrix

class AerSteakExecutionStrategy(SteakExecutionStrategy):

    shots = []

    def execute(self, backend, qubits, cl_bits, searched_values, iterations, origin, from_source, summary_file, shots):
        if from_source :
            self._execute_from_source(backend, qubits, cl_bits, searched_values, iterations, origin, summary_file, shots)

    def _execute_from_source(self, backend, qubits, cl_bits, searched_values, iterations, origin, summary_file, shots):
        program_filename = self.folders.get_grover_filename(cl_bits, searched_values)
        for current_shots in shots :
            run_time = 0
            steak, layout = self.steaker._mount_steak_1_from_source(backend, qubits, cl_bits, searched_values)
            steak = steak.decompose()
            self._add_density_matrix_saves(steak, cl_bits, layout)
            self.steaker._add_measures(steak, layout)
            total_gates = sum(steak.count_ops().values())
            total_depth = steak.depth()
            counts, density_matrices, current_run_time = self._run_aer(backend, steak, current_shots, cl_bits)
            run_time += current_run_time
            self.steaker._save_steak_line(counts, backend.name, program_filename, iterations, 1,
                origin, steak, total_gates, total_depth, current_shots, run_time, searched_values, summary_file)
            
            angles = self.steaker._angles_from_counts(counts, cl_bits, current_shots)
            angles_in_degrees = [math.degrees(angle) for angle in angles]

            for iteration in range(2, iterations+1) :
                steak = self._mount_next_steak(backend, qubits, cl_bits, searched_values, layout, angles, density_matrices, True)
                steak = steak.decompose()
                self._add_density_matrix_saves(steak, cl_bits, layout)
                self.steaker._add_measures(steak, layout)
                total_gates = sum(steak.count_ops().values())
                total_depth = steak.depth()
                counts, density_matrices, current_run_time = self._run_aer(backend, steak, current_shots, cl_bits)
                run_time += current_run_time
                self.steaker._save_steak_line(counts, backend.name, program_filename, iterations, 1,
                    origin, steak, total_gates, total_depth, current_shots, run_time, searched_values, summary_file)
                angles = self.steaker._angles_from_counts(counts, cl_bits, current_shots)
                angles_in_degrees = [math.degrees(angle) for angle in angles]
            

    def _mount_next_steak(self, backend, qubits, cl_bits, searched_values, initial_layout, angles, density_matrices, from_source):
        steak = QuantumCircuit(qubits+1, cl_bits)

        ancilla = cl_bits
        for index, rho in enumerate(density_matrices):
            theta, alpha = self._get_mixed_state_angles(rho)
            steak.ry(theta, index)
            steak.ry(alpha, ancilla)
            steak.cry(math.pi, ancilla, index)
            steak.reset(ancilla)

        if from_source:
            self.steaker._add_oracles_and_diffuser_from_source(backend.name, steak, qubits, cl_bits, searched_values, initial_layout)

        return steak

    def _add_density_matrix_saves(self, qc, cl_bits, initial_layout):
        for index in range(cl_bits):
            qubit = index if initial_layout is None else initial_layout[index]
            qc.save_density_matrix([qubit], label=f"rho_{index}")


    def _run_aer(self, backend, qc, current_shots, cl_bits):
        run_time = time.time()
        result = backend.run(qc, shots=current_shots).result()
        run_time = time.time() - run_time
        counts = dict(sorted(result.get_counts().items()))
        data = result.data(0)
        density_matrices = []
        for index in range(cl_bits) :
            rho = data[f"rho_{index}"]
            density_matrices.append(rho)
        return counts, density_matrices, run_time

    def _get_mixed_state_angles(self, rho):
        data = rho.data

        x = 2 * data[0, 1].real
        y = -2 * data[0, 1].imag
        z = data[0, 0].real - data[1, 1].real

        r = math.sqrt(x*x + y*y + z*z)
        r = min(1.0, max(0.0, r))

        theta = 0.0 if r == 0 else math.atan2(x, z)
        alpha = math.acos(r)

        return theta, alpha