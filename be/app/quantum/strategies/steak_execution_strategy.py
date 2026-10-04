from abc import ABC, abstractmethod

from app.quantum.Folders import Folders

class SteakExecutionStrategy(ABC):

    folders = Folders()

    def __init__(self, steaker):
        self.steaker = steaker

    @abstractmethod
    def execute(self, backend, qubits, cl_bits, searched_values, iterations, origin, from_source, summary_file, shots):
        pass

