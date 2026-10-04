from pathlib import Path

from app.quantum.Folders import Folders

from pathlib import Path


def check_exist(files) -> None:
    missing_files = []

    def check(item):
        if isinstance(item, (list, tuple, set)):
            for subitem in item:
                check(subitem)
        else:
            path = Path(item)

            if not path.exists():
                missing_files.append(path)

    check(files)

    if missing_files:
        raise FileNotFoundError(
            "Files not found:\n" + "\n".join(str(file) for file in missing_files)
        )

def get_transpilation_time_filename(program_filename) -> Path:
    program_filename = Path(program_filename)

    return program_filename.with_name(
        program_filename.stem + "_transpilation_time.txt"
    )


def get_transpilation_time(program_filename) -> float:
    transpilation_time_filename = get_transpilation_time_filename(program_filename)

    return float(
        transpilation_time_filename.read_text(encoding="utf-8").strip()
    )

def get_transpiled_first(program_filename) -> str:
    program_path = Path(program_filename)

    backend_name = program_path.parent.name
    qubits = program_path.stem.split("_")[1]

    folders = Folders()
    transpiled_first_filename = (
        Path(folders.root_folder)
        / "fragments"
        / "h"
        / backend_name
        / f"transpiled_first_{qubits}.txt"
    )

    return transpiled_first_filename.read_text(encoding="utf-8").strip()


def get_initial_layout(backend_name, cl_bits) :
    folders = Folders()
    il_filename = folders.get_filepath(backend_name, "il", cl_bits)
    il_filename = Path(il_filename).with_suffix(".ser")
    if il_filename.exists() :
        initial_layout = Folders().undump(il_filename)
        return initial_layout
    return None

def get_circuit_from_module(module, function_name, initial_layout):
    function = getattr(module, function_name)
    if initial_layout is None:
        return function()
    return function(initial_layout)