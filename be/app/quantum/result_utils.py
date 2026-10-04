from pathlib import Path
from app.quantum.Folders import Folders

def save_result(backend, filename, type, transpiled_first,
                clbits, transpilation_time, searched_values : list[int] | None = None, gates : int | None = None, depth : int | None = None):

    folders = Folders()
    results_file = Path(folders.root_folder) / "results.tsv"
    searched_values_str = (
        ""
        if searched_values is None
        else str(searched_values)
        if isinstance(searched_values, int)
        else ",".join(map(str, searched_values))
    )

    if not results_file.exists():
        results_file.write_text(
            "backend\tfilename\ttype\ttranspiled_first\tqubits\tcl_bits\tsearched_values\ttranspilation_time\tgates\tdepth\n",
            encoding="utf-8"
        )

    qubits = clbits if backend.name == "aer_simulator" else backend.num_qubits

    with results_file.open("a", encoding="utf-8") as f:
        f.write(
            f"{backend.name}\t{Path(filename).name}\t{type}\t{transpiled_first}\t"
            f"{qubits}\t{clbits}\t"
            f"{searched_values_str}\t{transpilation_time}\t{gates}\t{depth}\n"
        )