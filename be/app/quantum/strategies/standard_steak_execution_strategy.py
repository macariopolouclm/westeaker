from app.quantum.strategies.steak_execution_strategy import SteakExecutionStrategy


class StandardSteakExecutionStrategy(SteakExecutionStrategy):
    def execute(self, backend, backend_name, qubits, cl_bits, searched_values,
                iterations, origin, from_source, summary_file):

        self.steaker._execute_standard_steaks(
            backend, backend_name, qubits, cl_bits, searched_values,
            iterations, origin, from_source, summary_file
        )
