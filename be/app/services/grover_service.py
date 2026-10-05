import math
from pathlib import Path

from app.quantum.backends import create_backends
from app.quantum.grover_generator import GroverGenerator
from app.quantum.grover_mounter_from_fragments import GroverMounterFromFragments
from app.quantum.grover_whole_generator import WholeGroverGenerator

class GroverGeneratorService:

    def generate_fragments(self, qubits: list[int], markable_values: list[int], searched_values: list[list[int]], default_values: bool = False, backend_names: list[str] | None = None, repetitions: int = 10):
        
        backends = create_backends(backend_names)

        generated_files = []
        found_files = []

        for repetition in range(1, repetitions + 1):  # Repeat the process specified number of times
            for clbits in qubits:
                if default_values:
                    searched_values = self._get_default_searched_values(clbits)
                    markable_values = searched_values[-1].copy()


                generator = GroverGenerator()
                generated, found = generator.generate_fragments(backends, clbits, markable_values)

                generated_files.extend(generated)
                found_files.extend(found)

                fragments_mounter = GroverMounterFromFragments()
                for backend in backends:
                    for current_searched_values in searched_values:
                        fragments_mounter.mount_for(backend, clbits=clbits, searched_values=current_searched_values)
                    generated_files.extend(fragments_mounter.generated_files)
                    found_files.extend(fragments_mounter.found_files)


                for backend in backends:
                    whole_mounter = WholeGroverGenerator(clbits)
                    for current_searched_values in searched_values:
                        generated_filenames = whole_mounter.generate_files(backend, current_searched_values)
                        generated_files.extend(generated_filenames)

                # Borrar los files de generated cuando repetitions >1
                if repetitions > 1 and repetition < repetitions:
                    for file in generated:
                        if Path(file).exists():
                            Path(file).unlink()  # Delete the file



        return {
            "qubits": qubits,
            "marked_values": markable_values,
            "backends": [
                backend.name
                for backend in backends
            ],
            "generated_files": generated_files,
            "found_files": found_files
        }


    def _get_default_searched_values(self, qubits: int) -> list[list[int]]:
        values = self._get_default_values(qubits)
        return [values[:index] for index in range(1, len(values) + 1)]

    def _get_default_values(self, qubits: int) -> list[int]:
        space_size = 2 ** qubits
        number_of_values = math.isqrt(space_size)
        values = [1, space_size]
        level = 1
        while len(values) < number_of_values:
            divisions = 2 ** level
            step = space_size // divisions
            for position in range(1, divisions, 2):
                values.append(position * step)
                if len(values) == number_of_values:
                    break
            level += 1
        return [value - 1 for value in values]

