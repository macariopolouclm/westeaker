import os
import pickle
import shutil
from codecs import ignore_errors
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Folders:
    root_folder = str(Path.home() / "Desktop" / "westeakers" / "web") + "/"

    def get_grover_filename(self, clbits: int, searched_values: list[int], transpiled_first: str | None = None) -> str:
        values = "_".join(map(str, sorted(searched_values)))
        if transpiled_first is None:
            return f"grover_{clbits}_{values}.py"
        
        return f"grover_{transpiled_first}_{clbits}_{values}.py"

    def save_text(self, file_name, text):
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(text)
            file.flush()

    def dump(self, file_name, object):
        with open(file_name, "wb") as file:
            pickle.dump(object, file)

    def undump(self, file_name):
        file_name = Path(file_name)
        with open(file_name, "rb") as file:
            return pickle.load(file)

    def get_fragment_filepath(self, backend_name: str, circuit: str, qubits: int | None, searched_value: int | None = None, transpile_first = None) -> str:
        prefix = f"{transpile_first}_" if transpile_first is not None else ""

        fubfolder = circuit
        if fubfolder=="oracles" :
            circuit = "oracle"
        elif fubfolder=="diffusers" :
            circuit = "diffuser"
        if searched_value is None :
            return os.path.join(self.root_folder, "fragments", fubfolder, backend_name, f"{circuit}_{prefix}{qubits}.py")
        else :
            return os.path.join(self.root_folder, "fragments", fubfolder, backend_name, f"{circuit}_{prefix}{qubits}_{searched_value}.py")

    def get_name(self, backend):
        return backend.name if not callable(backend.name) else backend.name()

    def create(self, backends, remove_old = False) :
        if remove_old:
            shutil.rmtree(self.root_folder, ignore_errors=True)

        os.makedirs(self.root_folder, exist_ok=True)

        os.makedirs(self.root_folder + "fragments/", exist_ok=True)
        os.makedirs(self.root_folder + "fragments/h/", exist_ok=True)
        os.makedirs(self.root_folder + "fragments/diffusers/", exist_ok=True)
        os.makedirs(self.root_folder + "fragments/oracles/", exist_ok=True)

        #os.makedirs(self.root_folder + "execution_results/", exist_ok=True)

        backend_names = [ "high_level"]
        for backend in backends :
            backend_name = self.get_name(backend)
            backend_names.append(backend_name)

        for backend_name in backend_names :
            os.makedirs(self.root_folder + f"fragments/h/{backend_name}/", exist_ok=True)
            os.makedirs(self.root_folder + f"fragments/oracles/{backend_name}/", exist_ok=True)
            os.makedirs(self.root_folder + f"fragments/diffusers/{backend_name}/", exist_ok=True)

        #folders = [ "whole_grovers", "composed_grovers", "steaks" ]
        folders = [ "whole_grovers", "composed_grovers" ]

        for folder in folders :
            for backend_name in backend_names :
                os.makedirs(self.root_folder + f"{folder}/{backend_name}/", exist_ok=True)


